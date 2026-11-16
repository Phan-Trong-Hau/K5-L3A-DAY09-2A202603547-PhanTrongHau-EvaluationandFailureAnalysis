"""Shape C — orchestrator plus read-only investigators. Student work.

1. Build a handoff with `lab8.handoff.make_handoff`. Allowed tools are read-only.
   Never put parent_secret, raw headers, or the full claim row into facts.
2. `lab8.runtime.run_readonly_investigators` runs those tools.
3. The orchestrator quotes from the investigator's order view and calls
   `durability.issue_refund`. Investigators have no write registry.
   Pass the full quote; the host subtracts earlier refunds on the same order.
   `lookup_refund_history` is a read-only tool you may hand to an investigator.
4. Trace the sanitized handoff, not the parent context.

An LLM summary of the parent context is not a sanitizer. Use the allowlist.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.
"""

from __future__ import annotations

import sqlite3

from lab8.db import connect
from lab8.durability import issue_refund
from lab8.handoff import make_handoff
from lab8.mock_llm import complete
from lab8.runtime import run_readonly_investigators
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish, safe_dump
from lab8.trace import Trace

# Read-only tools the investigator may use. Order matters: compute_compensation
# needs the order that lookup_order returns, so it comes last.
INVESTIGATOR_TOOLS = ["lookup_order", "lookup_policy", "compute_compensation"]
SHAPE = "orchestrator"


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    conn = connect(store_path)
    try:
        return _run(conn, claim_id, seed=seed, crash_at=crash_at)
    finally:
        conn.close()


def _run(conn: sqlite3.Connection, claim_id: str, *, seed: int, crash_at: str | None) -> RunResult:
    budget = Budget()
    trace = Trace(make_run_id(SHAPE, claim_id, seed))

    claim = conn.execute(
        "SELECT claim_id, principal_id, order_id FROM claims WHERE claim_id = ?",
        (claim_id,),
    ).fetchone()
    if claim is None:
        trace.add("error", {"reason": "unknown_claim"})
        return _done(conn, claim_id, seed, "failed", 0, budget, trace, "unknown_claim")

    if not claim["order_id"]:
        trace.add("decision", {"status": "needs_info", "reason": "missing_order_id"})
        return _done(conn, claim_id, seed, "needs_info", 0, budget, trace, "missing_order_id")

    # Orchestrator step: decide what the investigator should check. Counted for cost.
    handoff = make_handoff(
        request_id=f"REQ-{claim_id}",
        claim_id=claim_id,
        task="quote_refund_from_order",
        facts={},
        allowed_tools=INVESTIGATOR_TOOLS,
    )
    trace.add("handoff", safe_dump(handoff))
    complete(budget, seed=seed, purpose="plan", prompt=handoff["task"])

    investigated = run_readonly_investigators(
        conn, budget, handoff, principal_id=claim["principal_id"]
    )
    tools = investigated["tools"]
    order_view = tools.get("lookup_order") or {}
    trace.add("investigator", {"lookup_order": {"visible": order_view.get("visible"), "reason": order_view.get("reason")}, "tools": sorted(tools)})

    if not order_view.get("visible"):
        return _done(conn, claim_id, seed, "escalated", 0, budget, trace, order_view.get("reason"))

    # Quote from the investigator's order view. The ticket text is not read here.
    quote = tools.get("compute_compensation") or {}
    proposal = int(quote.get("amount_vnd") or 0)
    trace.add(
        "quote",
        {
            "amount_vnd": proposal,
            "reason": quote.get("reason"),
            "clause_ids": quote.get("clause_ids"),
            "parts": quote.get("parts"),
        },
    )
    if proposal <= 0:
        return _done(conn, claim_id, seed, "denied", 0, budget, trace, quote.get("reason"))

    # Full quote, not a net amount. The host subtracts earlier refunds on the order.
    # InjectedCrash is not caught here: the fault lab needs it to propagate.
    outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    trace.add("write", {"ok": outcome["ok"], "reason": outcome["reason"]})
    if not outcome["ok"]:
        status = "failed" if outcome["conflict"] else "denied"
        return _done(conn, claim_id, seed, status, proposal, budget, trace, outcome["reason"])
    return _done(conn, claim_id, seed, "resolved", proposal, budget, trace, None)


def _done(
    conn: sqlite3.Connection,
    claim_id: str,
    seed: int,
    status: str,
    proposal: int,
    budget: Budget,
    trace: Trace,
    error_reason: str | None,
) -> RunResult:
    return finish(
        conn,
        shape=SHAPE,
        claim_id=claim_id,
        seed=seed,
        status=status,
        proposal_amount=proposal,
        budget=budget,
        trace=trace,
        error_reason=error_reason,
    )
