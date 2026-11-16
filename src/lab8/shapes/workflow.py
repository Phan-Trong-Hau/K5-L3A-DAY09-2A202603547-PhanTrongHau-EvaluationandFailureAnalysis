"""Shape A — deterministic workflow. Student work.

Signature (do not change):

    run_claim(claim_id, *, seed, store_path, crash_at=None) -> RunResult

Suggested steps. Money stays in code (`lab8.tools.compute_compensation`).

1. Open the store. Read the claim through `get_claim_view` (not SELECT *).
2. Missing order_id -> status `needs_info`. Do not write the ledger.
3. `lookup_order`. If not visible -> `escalated`. Do not copy phone, address, item, internal note.
4. Quote from the order row. Ignore delay numbers written in the ticket.
5. Quote amount 0 -> `denied`. Do not call issue_refund.
6. Quote amount > 0 -> `durability.issue_refund(conn, claim_id, <full quote>)`.
   Pass the FULL quote. The host checks the claim's own approval and subtracts
   what earlier claims already got for the same order (T13, T14). Do not
   subtract it yourself or the host subtracts twice.
   Auth failure or order already refunded -> `denied` (the host writes `policy_denied`).
   `proposal_amount` stays the full quote. Amount conflict -> `failed`.
7. Success -> `resolved`. One ledger row, one `refund_committed` audit.
8. Use MockLLM only to draft the reply text, if you want a model call at all.

The model must not choose the refund amount and must not commit the refund.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.
"""

from __future__ import annotations

import sqlite3

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.mock_llm import complete
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish, safe_dump
from lab8.tools import compute_compensation, get_claim_view, lookup_order, tool_cost
from lab8.trace import Trace

_SHAPE = "workflow"


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


def _run(
    conn: sqlite3.Connection,
    claim_id: str,
    *,
    seed: int,
    crash_at: str | None,
) -> RunResult:
    budget = Budget()
    trace = Trace(make_run_id(_SHAPE, claim_id, seed))

    # Step 1: read the claim through the sanitized view only. The ticket text and
    # the raw claim row (parent_secret) never enter the trace.
    budget.add_tool(tool_cost())
    claim = get_claim_view(conn, claim_id)
    trace.add(
        "claim_view",
        safe_dump({key: value for key, value in claim.items() if key != "ticket"}),
    )
    if not claim["found"]:
        trace.add("decision", {"status": "failed", "reason": "unknown_claim"})
        return _finish(conn, claim_id, seed, "failed", 0, budget, trace, "unknown_claim")

    # Step 2: missing order_id -> needs_info. The ledger stays untouched.
    if not claim["order_id"]:
        trace.add("decision", {"status": "needs_info", "reason": "missing_order_id"})
        complete(budget, seed=seed, purpose="draft", prompt="needs_info")
        return _finish(conn, claim_id, seed, "needs_info", 0, budget, trace, "missing_order_id")

    # Step 3: the order must exist and belong to the same principal. The view is
    # the allowlisted ORDER_FIELDS projection; phone/address/item/note never leave it.
    budget.add_tool(tool_cost())
    view = lookup_order(conn, claim["order_id"], claim["principal_id"])
    trace.add("order_view", safe_dump({key: value for key, value in view.items() if key != "order"}))
    if not view["visible"]:
        trace.add("decision", {"status": "escalated", "reason": view["reason"]})
        complete(budget, seed=seed, purpose="draft", prompt="escalated")
        return _finish(conn, claim_id, seed, "escalated", 0, budget, trace, view["reason"])

    order = view["order"]

    # Step 4: quote from the order row only. Delay numbers written in the ticket
    # are ignored on purpose (that is the swarm's REFERENCE_WEAKNESS, not ours).
    budget.add_tool(tool_cost())
    quote = compute_compensation(conn, order)
    trace.add("quote", safe_dump(quote))
    proposal = int(quote["amount_vnd"])

    # Step 5: nothing to refund -> denied. Do not call issue_refund, so there is
    # deliberately no policy_denied audit on this path (quote 0 is not a policy hit).
    if proposal <= 0:
        trace.add("decision", {"status": "denied", "reason": quote.get("reason")})
        complete(budget, seed=seed, purpose="draft", prompt="denied")
        return _finish(conn, claim_id, seed, "denied", 0, budget, trace, quote.get("reason"))

    # Steps 6-7: the host checks approval, the per-order cap and idempotency, then
    # writes the ledger in one transaction. We pass the FULL quote and crash_at;
    # InjectedCrash must propagate so the crash test sees a real crash.
    try:
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise

    if not outcome["ok"]:
        # Host refusal: the host already wrote the policy_denied audit. The
        # proposal stays the full quote; only the host may cap or reject it.
        status = "failed" if outcome.get("conflict") else "denied"
        trace.add("decision", {"status": status, "reason": outcome["reason"]})
        complete(budget, seed=seed, purpose="draft", prompt=status)
        return _finish(conn, claim_id, seed, status, proposal, budget, trace, outcome["reason"])

    trace.add("decision", {"status": "resolved"})
    complete(budget, seed=seed, purpose="draft", prompt=f"resolved:{proposal}")
    return _finish(conn, claim_id, seed, "resolved", proposal, budget, trace, None)


def _finish(
    conn: sqlite3.Connection,
    claim_id: str,
    seed: int,
    status: str,
    proposal_amount: int,
    budget: Budget,
    trace: Trace,
    error_reason: str | None,
) -> RunResult:
    """Single exit point so refund_effects, audit count and the trace stay consistent."""
    return finish(
        conn,
        shape=_SHAPE,
        claim_id=claim_id,
        seed=seed,
        status=status,
        proposal_amount=proposal_amount,
        budget=budget,
        trace=trace,
        error_reason=error_reason,
    )
