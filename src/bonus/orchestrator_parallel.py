"""B1 — orchestrator with parallel read-only investigators (bonus variant).

Same contract and same host gate as shapes/orchestrator.py. The only change is
the read step:

    plan -> claim_view -> { lookup_order , lookup_policy } -> compute_compensation -> issue_refund

lookup_order and lookup_policy do not depend on each other, so they run on a
ThreadPoolExecutor. Each worker opens its own SQLite connection. Only the main
thread writes (issue_refund). Results are joined in a fixed order, so the
outcome does not depend on which thread finishes first.

Timing is measured with time.perf_counter() on real runs. The trace gets a
"timing" event with the wall-clock of the whole run, the read phase, and each
worker. Nothing is simulated.

Run timing and equality from src/:
  python -m bonus.timing_report --seeds 11,22,33,44,55 --reps 5 --out reports/bonus_timing.json
"""

from __future__ import annotations

import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from lab8.db import connect
from lab8.durability import issue_refund
from lab8.handoff import make_handoff
from lab8.mock_llm import complete
from lab8.runtime import dispatch
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish, safe_dump
from lab8.tools import get_claim_view, tool_cost
from lab8.trace import Trace

SHAPE = "orchestrator_parallel"
MAX_WORKERS = 2
INVESTIGATOR_TOOLS = ["lookup_order", "lookup_policy", "compute_compensation"]


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    conn = connect(store_path)
    try:
        return _run(conn, store_path, claim_id, seed=seed, crash_at=crash_at, max_workers=MAX_WORKERS)
    finally:
        conn.close()


def _read_worker(store_path: str, name: str, args: dict[str, Any]) -> tuple[dict[str, Any], float]:
    """Runs in a worker thread with its own connection. Returns (result, measured ms).

    Budget is discarded; the main thread counts tool calls.
    """
    started = time.perf_counter()
    conn = connect(store_path)
    try:
        result = dispatch(conn, Budget(), name, args, worker=True)
    finally:
        conn.close()
    return result, _ms(started)


def _ms(started: float) -> float:
    return round((time.perf_counter() - started) * 1000, 3)


def _run(
    conn: sqlite3.Connection,
    store_path: str,
    claim_id: str,
    *,
    seed: int,
    crash_at: str | None,
    max_workers: int,
) -> RunResult:
    t_run = time.perf_counter()
    budget = Budget()
    trace = Trace(make_run_id(SHAPE, claim_id, seed))
    timing: dict[str, Any] = {"read_phase_ms": None, "worker_ms": {}}

    claim = conn.execute(
        "SELECT claim_id, principal_id, order_id FROM claims WHERE claim_id = ?",
        (claim_id,),
    ).fetchone()
    if claim is None:
        trace.add("error", {"reason": "unknown_claim"})
        return _done(conn, claim_id, seed, "failed", 0, budget, trace, timing, t_run, "unknown_claim")
    if not claim["order_id"]:
        trace.add("decision", {"status": "needs_info", "reason": "missing_order_id"})
        return _done(conn, claim_id, seed, "needs_info", 0, budget, trace, timing, t_run, "missing_order_id")

    handoff = make_handoff(
        request_id=f"REQ-{claim_id}",
        claim_id=claim_id,
        task="quote_refund_from_order",
        facts={},
        allowed_tools=INVESTIGATOR_TOOLS,
    )
    trace.add("handoff", safe_dump(handoff))
    complete(budget, seed=seed, purpose="plan", prompt=handoff["task"])

    # claim_view on the main connection, counted like run_readonly_investigators does.
    view = get_claim_view(conn, claim_id)
    budget.add_tool(tool_cost())

    # Independent read-only steps run in parallel. Join order is fixed by dict order.
    scope = {"order_id": view.get("order_id"), "principal_id": claim["principal_id"]}
    t_read = time.perf_counter()
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            "lookup_order": pool.submit(_read_worker, store_path, "lookup_order", scope),
            "lookup_policy": pool.submit(_read_worker, store_path, "lookup_policy", {}),
        }
        joined = {name: future.result() for name, future in futures.items()}
    timing["read_phase_ms"] = _ms(t_read)
    tools: dict[str, dict[str, Any]] = {}
    for name, (result, worker_ms) in joined.items():
        tools[name] = result
        timing["worker_ms"][name] = worker_ms
        budget.add_tool(tool_cost())

    order_view = tools["lookup_order"]
    trace.add(
        "investigator",
        {
            "lookup_order": {"visible": order_view.get("visible"), "reason": order_view.get("reason")},
            "tools": sorted(tools),
            "parallel": sorted(futures),
        },
    )
    if not order_view.get("visible"):
        return _done(conn, claim_id, seed, "escalated", 0, budget, trace, timing, t_run, order_view.get("reason"))

    # Depends on lookup_order, so it runs after the parallel step, on the main connection.
    quote = dispatch(conn, budget, "compute_compensation", {"order": order_view["order"]}, worker=True)
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
        return _done(conn, claim_id, seed, "denied", 0, budget, trace, timing, t_run, quote.get("reason"))

    # Only the main thread writes. InjectedCrash is not caught.
    outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    trace.add("write", {"ok": outcome["ok"], "reason": outcome["reason"]})
    if not outcome["ok"]:
        status = "failed" if outcome["conflict"] else "denied"
        return _done(conn, claim_id, seed, status, proposal, budget, trace, timing, t_run, outcome["reason"])
    return _done(conn, claim_id, seed, "resolved", proposal, budget, trace, timing, t_run, None)


def _done(
    conn: sqlite3.Connection,
    claim_id: str,
    seed: int,
    status: str,
    proposal: int,
    budget: Budget,
    trace: Trace,
    timing: dict[str, Any],
    t_run: float,
    error_reason: str | None,
) -> RunResult:
    trace.add("timing", {"total_ms": _ms(t_run), **timing})
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
