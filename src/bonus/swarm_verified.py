"""B3: reference swarm with a structured-data verifier before refunding."""

from __future__ import annotations

import sqlite3

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.handoff import make_handoff
from lab8.mock_llm import complete, parse_delay_days
from lab8.runtime import run_readonly_investigators
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish, safe_dump
from lab8.tools import compute_compensation, tool_cost
from lab8.trace import Trace

VERIFIED_FIELDS = ("status", "delay_days", "shipping_fee_vnd", "paid_vnd", "damage_verified")


def mismatched_quote_fields(candidate: dict, authoritative: dict) -> list[str]:
    """Return quote inputs that differ from the structured order facts."""
    return [field for field in VERIFIED_FIELDS if candidate.get(field) != authoritative.get(field)]


def run_claim(claim_id: str, *, seed: int, store_path: str, crash_at: str | None = None) -> RunResult:
    conn = connect(store_path)
    try:
        return _run(conn, claim_id, seed=seed, crash_at=crash_at)
    finally:
        conn.close()


def _run(conn: sqlite3.Connection, claim_id: str, *, seed: int, crash_at: str | None) -> RunResult:
    budget = Budget()
    run_id = make_run_id("swarm_verified", claim_id, seed)
    trace = Trace(run_id)
    budget.add_tool(tool_cost())
    claim = conn.execute(
        "SELECT claim_id, principal_id, order_id, ticket FROM claims WHERE claim_id = ?", (claim_id,)
    ).fetchone()
    if claim is None:
        trace.add("error", {"reason": "unknown_claim"})
        return finish(conn, shape="swarm_verified", claim_id=claim_id, seed=seed, status="failed",
                      proposal_amount=0, budget=budget, trace=trace, error_reason="unknown_claim")

    ticket = claim["ticket"]
    complete(budget, seed=seed, purpose="peer", prompt=ticket)
    parsed_delay = parse_delay_days(ticket)
    complete(budget, seed=seed, purpose="parse", prompt=ticket)
    if not claim["order_id"]:
        complete(budget, seed=seed, purpose="draft", prompt="needs_info")
        trace.add("decision", {"status": "needs_info"})
        return finish(conn, shape="swarm_verified", claim_id=claim_id, seed=seed, status="needs_info",
                      proposal_amount=0, budget=budget, trace=trace, error_reason="missing_order_id")

    handoff = make_handoff(request_id=f"REQ-{claim_id}", claim_id=claim_id,
                           task="check_applicable_policy", facts={},
                           allowed_tools=["lookup_order", "lookup_policy", "compute_compensation"])
    trace.add("handoff", safe_dump(handoff))
    investigated = run_readonly_investigators(conn, budget, handoff, principal_id=claim["principal_id"])
    order_view = investigated["tools"].get("lookup_order", {})
    trace.add("investigator", {"lookup_order": order_view,
                               "policy_count": len((investigated["tools"].get("lookup_policy") or {}).get("policies") or [])})
    if not order_view.get("visible"):
        complete(budget, seed=seed, purpose="draft", prompt="escalated")
        return finish(conn, shape="swarm_verified", claim_id=claim_id, seed=seed, status="escalated",
                      proposal_amount=0, budget=budget, trace=trace, error_reason=order_view.get("reason"))

    authoritative = dict(order_view["order"])
    candidate = dict(authoritative)
    # Preserve the reference swarm's known weakness so the verifier's effect is measurable.
    if parsed_delay is not None and parsed_delay != int(candidate["delay_days"]) and seed % 5 == 0:
        candidate["delay_days"] = parsed_delay
        trace.add("model_override", {"delay_days": parsed_delay})

    mismatches = mismatched_quote_fields(candidate, authoritative)
    if mismatches:
        budget.add_tool(tool_cost())
        quote_payload = compute_compensation(conn, authoritative)
        trace.add("verifier_override", {"fields": mismatches,
                                         "amount_vnd": int(quote_payload["amount_vnd"])})
    else:
        quote_payload = investigated["tools"]["compute_compensation"]
        trace.add("verifier_pass", {"fields": list(VERIFIED_FIELDS)})

    proposal = int(quote_payload["amount_vnd"])
    trace.add("quote", quote_payload)
    complete(budget, seed=seed, purpose="draft", prompt=f"proposal={proposal}")
    if proposal <= 0:
        return finish(conn, shape="swarm_verified", claim_id=claim_id, seed=seed, status="denied",
                      proposal_amount=0, budget=budget, trace=trace, error_reason=quote_payload.get("reason"))
    try:
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise
    if not outcome["ok"]:
        status = "failed" if outcome["conflict"] else "denied"
        return finish(conn, shape="swarm_verified", claim_id=claim_id, seed=seed, status=status,
                      proposal_amount=proposal, budget=budget, trace=trace, error_reason=outcome["reason"])
    return finish(conn, shape="swarm_verified", claim_id=claim_id, seed=seed, status="resolved",
                  proposal_amount=proposal, budget=budget, trace=trace)
