"""B1 timing: real wall-clock of the sequential orchestrator vs the parallel variant.

Same claims, seeds and corpus. Each timed run gets a fresh copy of an initialized store, copied
before the timer starts. Each claim × seed runs one untimed warm-up, then `--reps` timed runs per
shape; the order (sequential first or parallel first) alternates per rep to limit drift.

Run from src/:
  python -m bonus.timing_report --seeds 11,22,33,44,55 --reps 5 --out reports/bonus_timing.json
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import sqlite3
import tempfile
import time
from pathlib import Path
from statistics import median

from bonus import orchestrator_parallel as par
from lab8.config_loader import repo_path
from lab8.db import connect, init_store, load_json, load_jsonl
from lab8.metrics import trial_pass
from lab8.shapes import orchestrator

WORLD = load_json(repo_path("data", "public_world_state.json"))
CLAIMS = load_jsonl(repo_path("data", "public_claims.jsonl"))
BY_ID = {row["claim_id"]: row for row in CLAIMS}
RUNNERS = {"sequential": orchestrator.run_claim, "parallel": par.run_claim}


def _outcome(result, store: str) -> dict:
    conn = connect(store)
    try:
        ledger = [tuple(r) for r in conn.execute(
            "SELECT claim_id, amount_vnd FROM refund_ledger WHERE claim_id = ? ORDER BY claim_id",
            (result.claim_id,),
        ).fetchall()]
    finally:
        conn.close()
    return {
        "status": result.status,
        "proposal_amount": result.proposal_amount,
        "ledger": ledger,
        "audits": result.committed_audit_count,
        "tool_calls": result.tool_calls,
        "cost": result.cost_estimate,
        "error_reason": result.error_reason,
    }


def _timed_run(runner, store: str, claim_id: str, seed: int):
    started_wall = time.time()
    t0 = time.perf_counter()
    result = runner(claim_id, seed=seed, store_path=store)
    elapsed_ms = (time.perf_counter() - t0) * 1000
    return result, round(elapsed_ms, 3), started_wall


def _read_phase_ms(result) -> float | None:
    body = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))
    event = next((e["payload"] for e in body["events"] if e["kind"] == "timing"), None)
    return None if not event else event.get("read_phase_ms")


def _passed(result, store: str, claim_id: str, started_wall: float) -> bool:
    conn = connect(store)
    try:
        ok, _ = trial_pass(result.as_dict(), BY_ID[claim_id]["expected"], conn, started_at=started_wall)
    finally:
        conn.close()
    return ok


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", default="11,22,33,44,55")
    parser.add_argument("--reps", type=int, default=5)
    parser.add_argument("--out", default="reports/bonus_timing.json")
    args = parser.parse_args(argv)
    seeds = [int(s) for s in args.seeds.split(",")]

    trials = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        template = root / "template.sqlite"
        init_store(template, WORLD, CLAIMS).close()

        for claim_id in BY_ID:
            for seed in seeds:
                # Untimed warm-up on separate copies.
                for name, runner in RUNNERS.items():
                    warm = root / f"warm-{name}-{claim_id}-{seed}.sqlite"
                    shutil.copyfile(template, warm)
                    runner(claim_id, seed=seed, store_path=str(warm))

                times: dict[str, list[float]] = {name: [] for name in RUNNERS}
                read_ms: list[float] = []
                first: dict[str, tuple] = {}
                statuses_match = True
                for rep in range(args.reps):
                    order = list(RUNNERS) if rep % 2 == 0 else list(reversed(list(RUNNERS)))
                    rep_status = {}
                    for name in order:
                        store = root / f"{name}-{claim_id}-{seed}-{rep}.sqlite"
                        shutil.copyfile(template, store)  # copy happens before the timer
                        result, elapsed, started = _timed_run(RUNNERS[name], str(store), claim_id, seed)
                        times[name].append(elapsed)
                        rep_status[name] = result.status
                        if rep == 0:
                            first[name] = (result, str(store), started)
                        if name == "parallel":
                            phase = _read_phase_ms(result)
                            if phase is not None:
                                read_ms.append(phase)
                    statuses_match = statuses_match and rep_status["sequential"] == rep_status["parallel"]

                seq_result, seq_store, seq_started = first["sequential"]
                par_result, par_store, par_started = first["parallel"]
                identical = _outcome(seq_result, seq_store) == _outcome(par_result, par_store)
                trials.append({
                    "claim_id": claim_id,
                    "seed": seed,
                    "status": par_result.status,
                    "identical_outcome": identical and statuses_match,
                    "pass_sequential": _passed(seq_result, seq_store, claim_id, seq_started),
                    "pass_parallel": _passed(par_result, par_store, claim_id, par_started),
                    "sequential_ms": times["sequential"],
                    "parallel_ms": times["parallel"],
                    "sequential_median_ms": round(median(times["sequential"]), 3),
                    "parallel_median_ms": round(median(times["parallel"]), 3),
                    "parallel_read_phase_median_ms": round(median(read_ms), 3) if read_ms else None,
                })

    seq_total = sum(t["sequential_median_ms"] for t in trials)
    par_total = sum(t["parallel_median_ms"] for t in trials)
    per_trial_ratio = [t["sequential_median_ms"] / t["parallel_median_ms"] for t in trials]
    reads = [t["parallel_read_phase_median_ms"] for t in trials if t["parallel_read_phase_median_ms"] is not None]
    summary = {
        "trials": len(trials),
        "reps_per_shape": args.reps,
        "identical_outcomes": sum(t["identical_outcome"] for t in trials),
        "pass_rate_sequential": round(sum(t["pass_sequential"] for t in trials) / len(trials), 3),
        "pass_rate_parallel": round(sum(t["pass_parallel"] for t in trials) / len(trials), 3),
        "sequential_total_median_ms": round(seq_total, 3),
        "parallel_total_median_ms": round(par_total, 3),
        "speedup_of_totals": round(seq_total / par_total, 3),
        "speedup_median_per_trial": round(median(per_trial_ratio), 3),
        "trials_parallel_faster": sum(r > 1 for r in per_trial_ratio),
        "read_phase_median_ms_across_trials": round(median(reads), 3) if reads else None,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "cpu_count": os.cpu_count(),
            "sqlite": sqlite3.sqlite_version,
            "max_workers": par.MAX_WORKERS,
        },
        "measurement": "wall-clock, time.perf_counter around run_claim; store copy excluded; includes trace write",
    }
    out = {"summary": summary, "trials": trials}
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
