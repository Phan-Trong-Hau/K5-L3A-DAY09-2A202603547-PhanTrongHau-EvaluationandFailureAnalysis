"""B1: parallel investigators. Same outcome as the sequential orchestrator, whatever the thread timing."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from bonus import orchestrator_parallel as par
from lab8.db import connect, init_store
from lab8.durability import InjectedCrash
from lab8.shapes import orchestrator
from tests.conftest import CLAIMS, WORLD

ALL_CLAIMS = [row["claim_id"] for row in CLAIMS]


def _fresh_store(tmp_path: Path, name: str) -> str:
    path = tmp_path / name
    init_store(path, WORLD, CLAIMS).close()
    return str(path)


def _outcome(result, store: str) -> dict:
    conn = connect(store)
    try:
        rows = conn.execute(
            "SELECT claim_id, amount_vnd FROM refund_ledger WHERE claim_id = ? ORDER BY claim_id",
            (result.claim_id,),
        ).fetchall()
    finally:
        conn.close()
    return {
        "status": result.status,
        "proposal_amount": result.proposal_amount,
        "ledger": [tuple(row) for row in rows],
        "audits": result.committed_audit_count,
        "tool_calls": result.tool_calls,
        "model_calls": result.model_calls,
        "cost": result.cost_estimate,
        "error_reason": result.error_reason,
    }


def _events(result) -> list[dict]:
    return json.loads(Path(result.trace_path).read_text(encoding="utf-8"))["events"]


@pytest.mark.parametrize("seed", [11, 55])
@pytest.mark.parametrize("claim_id", ALL_CLAIMS)
def test_parallel_matches_sequential_orchestrator(tmp_path, claim_id, seed):
    seq_store = _fresh_store(tmp_path, "seq.sqlite")
    par_store = _fresh_store(tmp_path, "par.sqlite")
    seq = orchestrator.run_claim(claim_id, seed=seed, store_path=seq_store)
    got = par.run_claim(claim_id, seed=seed, store_path=par_store)
    assert _outcome(got, par_store) == _outcome(seq, seq_store)


def test_result_does_not_depend_on_thread_completion_order(tmp_path, monkeypatch):
    baseline_store = _fresh_store(tmp_path, "base.sqlite")
    slow_store = _fresh_store(tmp_path, "slow.sqlite")
    single_store = _fresh_store(tmp_path, "single.sqlite")
    baseline = par.run_claim("C-014", seed=22, store_path=baseline_store)

    real_worker = par._read_worker

    def slow_order_first(store_path, name, args):
        # Test-only delay: makes lookup_order finish after lookup_policy.
        if name == "lookup_order":
            time.sleep(0.05)
        return real_worker(store_path, name, args)

    monkeypatch.setattr(par, "_read_worker", slow_order_first)
    slowed = par.run_claim("C-014", seed=22, store_path=slow_store)
    monkeypatch.setattr(par, "_read_worker", real_worker)

    one_thread = par._run(
        connect(single_store), single_store, "C-014", seed=22, crash_at=None, max_workers=1
    )
    assert _outcome(slowed, slow_store) == _outcome(baseline, baseline_store)
    assert _outcome(one_thread, single_store) == _outcome(baseline, baseline_store)


def test_timing_event_is_real_and_each_worker_fits_inside_the_read_phase(tmp_path):
    store = _fresh_store(tmp_path, "timing.sqlite")
    result = par.run_claim("C-001", seed=11, store_path=store)
    timing = next(event["payload"] for event in _events(result) if event["kind"] == "timing")
    assert timing["total_ms"] > 0
    assert timing["read_phase_ms"] is not None and timing["read_phase_ms"] > 0
    assert set(timing["worker_ms"]) == {"lookup_order", "lookup_policy"}
    # Workers run inside the read phase, so no worker can take longer than the phase that waits for it.
    assert all(ms <= timing["read_phase_ms"] + 1e-6 for ms in timing["worker_ms"].values())
    assert timing["read_phase_ms"] <= timing["total_ms"] + 1e-6


def test_timing_event_has_no_simulated_fields(tmp_path):
    store = _fresh_store(tmp_path, "nosim.sqlite")
    result = par.run_claim("C-001", seed=11, store_path=store)
    kinds = {event["kind"] for event in _events(result)}
    assert "latency" not in kinds
    assert "timing" in kinds


def test_trace_has_no_secret_and_keeps_run_id(tmp_path):
    store = _fresh_store(tmp_path, "trace.sqlite")
    result = par.run_claim("C-001", seed=11, store_path=store)
    text = Path(result.trace_path).read_text(encoding="utf-8")
    assert "CANARY_SECRET" not in text
    assert json.loads(text)["run_id"] == result.run_id


def test_crash_propagates_and_resume_keeps_one_refund(tmp_path):
    store = _fresh_store(tmp_path, "crash.sqlite")
    with pytest.raises(InjectedCrash):
        par.run_claim("C-012", seed=11, store_path=store, crash_at="after_effect_before_checkpoint")
    resumed = par.run_claim("C-012", seed=11, store_path=store)
    conn = connect(store)
    try:
        n = conn.execute("SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = 'C-012'").fetchone()["n"]
    finally:
        conn.close()
    assert resumed.status == "resolved"
    assert n == 1
