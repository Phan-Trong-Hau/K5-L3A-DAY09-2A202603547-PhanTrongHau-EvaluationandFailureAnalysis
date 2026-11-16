"""Summarize verifier interventions from the two reproducible B3 benchmark runs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def analyze(report_path: Path, trace_dir: Path) -> dict[str, Any]:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    trials = [row for row in report["trials"] if row["shape"] == "swarm_verified"]
    intervention_count = 0
    missing_traces: list[str] = []
    examples: list[dict[str, Any]] = []
    for trial in trials:
        trace_path = trace_dir / f"{trial['run_id']}.json"
        if not trace_path.is_file():
            missing_traces.append(trial["run_id"])
            continue
        trace = json.loads(trace_path.read_text(encoding="utf-8"))
        for event in trace.get("events", []):
            if event.get("kind") == "verifier_override":
                intervention_count += 1
                if len(examples) < 5:
                    examples.append({
                        "claim_id": trial["claim_id"],
                        "seed": trial["seed"],
                        "event": event,
                    })
    return {
        "benchmark": str(report_path),
        "swarm_verified_trials": len(trials),
        "verifier_override_count": intervention_count,
        "traces_missing": missing_traces,
        "examples": examples,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="reports/bonus_analysis.json")
    parser.add_argument("--trace-dir", default="traces")
    args = parser.parse_args()
    result = {
        "public": analyze(Path("reports/bonus_benchmark_public.json"), Path(args.trace_dir)),
        "adversarial": analyze(Path("reports/bonus_benchmark_adversarial.json"), Path(args.trace_dir)),
    }
    if any(group["traces_missing"] for group in result.values()):
        raise SystemExit("benchmark traces are missing; rerun both benchmarks before summarizing")
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, group in result.items():
        print(f"{name}: verifier overrides {group['verifier_override_count']}/{group['swarm_verified_trials']}")
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
