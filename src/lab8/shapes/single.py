"""Shape B — one ReAct agent. Student work.

Use `lab8.runtime.run_react` with max_steps=8. `decide` may pick a read tool.
It must not call `issue_refund`. After the loop, the host validates the quote
and is the only writer.

A decide() that trusts ticket text over the order row will fail hidden claims
where the customer overstates the delay or cites a superseded clause.

Per-order cap: an order may already have been refunded by an earlier claim.
The read tool `lookup_refund_history` shows how much. The host still enforces
the cap, so pass the full quote to `durability.issue_refund`, not a net amount.

Caps: stop at 8 steps. Count model calls in the Budget so cost stays comparable.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.
"""

from __future__ import annotations

import sqlite3
from typing import Any

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.mock_llm import complete
from lab8.runtime import run_react
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish, safe_dump
from lab8.tools import get_claim_view, tool_cost
from lab8.trace import Trace


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    """Run Shape B (single ReAct agent) on one claim and return a RunResult."""
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
    run_id = make_run_id("single", claim_id, seed)
    trace = Trace(run_id)

    budget.add_tool(tool_cost())
    claim_view = get_claim_view(conn, claim_id)
    if not claim_view.get("found"):
        trace.add("error", {"reason": "unknown_claim"})
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status="failed",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason="unknown_claim",
        )

    state: dict[str, Any] = {}

    def decide(obs: dict[str, Any]) -> dict[str, Any]:
        last_tool = obs.get("last_tool")
        if last_tool is None:
            complete(budget, seed=seed, purpose="parse", prompt=str(claim_view.get("ticket") or ""))
            if not claim_view.get("order_id"):
                trace.add("decision", {"status": "needs_info", "reason": "missing_order_id"})
                return {"final": {"status": "needs_info", "proposal_amount": 0, "error_reason": "missing_order_id"}}
            trace.add("react_step", {"tool": "lookup_order", "order_id": claim_view["order_id"]})
            return {
                "tool": "lookup_order",
                "args": {
                    "order_id": claim_view["order_id"],
                    "principal_id": claim_view["principal_id"],
                },
            }

        if last_tool == "lookup_order":
            order_view = obs["last_result"]
            trace.add("lookup_order", safe_dump(order_view))
            complete(budget, seed=seed, purpose="react", prompt=f"visible={order_view.get('visible')}")
            if not order_view.get("visible"):
                trace.add("decision", {"status": "escalated", "reason": order_view.get("reason")})
                return {
                    "final": {
                        "status": "escalated",
                        "proposal_amount": 0,
                        "error_reason": order_view.get("reason"),
                    }
                }
            # Keep DB order facts intact; never override delay_days from ticket text.
            state["order"] = dict(order_view["order"])
            trace.add("react_step", {"tool": "lookup_refund_history", "order_id": claim_view["order_id"]})
            return {
                "tool": "lookup_refund_history",
                "args": {
                    "order_id": claim_view["order_id"],
                    "principal_id": claim_view["principal_id"],
                },
            }

        if last_tool == "lookup_refund_history":
            history_view = obs["last_result"]
            trace.add("lookup_refund_history", safe_dump(history_view))
            complete(budget, seed=seed, purpose="react", prompt=f"refunded_vnd={history_view.get('refunded_vnd', 0)}")
            trace.add("react_step", {"tool": "compute_compensation"})
            return {
                "tool": "compute_compensation",
                "args": {"order": state["order"]},
            }

        if last_tool == "compute_compensation":
            quote_payload = obs["last_result"]
            trace.add("quote", safe_dump(quote_payload))
            proposal = int(quote_payload["amount_vnd"])
            complete(budget, seed=seed, purpose="draft", prompt=f"proposal={proposal}")
            if proposal <= 0:
                trace.add(
                    "decision",
                    {
                        "status": "denied",
                        "proposal_amount": 0,
                        "reason": quote_payload.get("reason"),
                    },
                )
                return {
                    "final": {
                        "status": "denied",
                        "proposal_amount": 0,
                        "error_reason": quote_payload.get("reason"),
                    }
                }
            trace.add("decision", {"status": "propose_refund", "proposal_amount": proposal})
            return {
                "final": {
                    "status": "propose_refund",
                    "proposal_amount": proposal,
                    "error_reason": None,
                }
            }

        return {"final": {"status": "failed", "proposal_amount": 0, "error_reason": f"unexpected_tool:{last_tool}"}}

    react_out = run_react(
        conn,
        budget,
        observation={"claim": claim_view},
        decide=decide,
        max_steps=8,
        worker=True,
    )
    final = react_out["final"]
    status = final["status"]
    proposal = int(final.get("proposal_amount", 0))
    error_reason = final.get("error_reason")

    if status != "propose_refund":
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status=status,
            proposal_amount=proposal,
            budget=budget,
            trace=trace,
            error_reason=error_reason,
        )

    try:
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise

    if not outcome["ok"]:
        final_status = "failed" if outcome["conflict"] else "denied"
        trace.add("host_gate", {"ok": False, "status": final_status, "reason": outcome["reason"]})
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status=final_status,
            proposal_amount=proposal,
            budget=budget,
            trace=trace,
            error_reason=outcome["reason"],
        )

    trace.add("host_gate", {"ok": True, "status": "resolved", "reason": outcome["reason"]})
    return finish(
        conn,
        shape="single",
        claim_id=claim_id,
        seed=seed,
        status="resolved",
        proposal_amount=proposal,
        budget=budget,
        trace=trace,
        error_reason=None,
    )
