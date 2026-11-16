import json
from pathlib import Path

import pytest

from lab8.db import connect, init_store
from lab8.durability import InjectedCrash, committed_audit_count, get_refund
from lab8.metrics import check_trace, trial_pass
from lab8.shapes.swarm_reference import run_claim as run_swarm
from bonus.swarm_verified import mismatched_quote_fields, run_claim
from bonus.workflow_baseline import run_claim as run_workflow_baseline

BONUS = Path(__file__).resolve().parents[1] / "bonus"
WORLD = json.loads((BONUS / "world.json").read_text(encoding="utf-8"))
CASES = [json.loads(line) for line in (BONUS / "cases.jsonl").read_text(encoding="utf-8").splitlines()]


@pytest.mark.parametrize("field,bad_value", [
    ("delay_days", 99),
    ("status", "in_transit"),
    ("damage_verified", not True),
])
def test_verifier_checks_every_business_fact_used_for_quote(field, bad_value):
    authoritative = {"delay_days": 2, "status": "delivered", "damage_verified": True}
    candidate = dict(authoritative)
    candidate[field] = bad_value
    assert mismatched_quote_fields(candidate, authoritative) == [field]


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["claim_id"])
def test_adversarial_cases_follow_structured_order(case, tmp_path):
    store = tmp_path / f"{case['claim_id']}.sqlite"
    init_store(store, WORLD, CASES).close()
    result = run_claim(case["claim_id"], seed=11, store_path=str(store))
    conn = connect(store)
    try:
        passed, reason = trial_pass(result.as_dict(), case["expected"], conn)
        assert passed, reason
        trace_ok, trace_reason = check_trace(result.as_dict())
        assert trace_ok, trace_reason
        body = Path(result.trace_path).read_text(encoding="utf-8")
        assert case["parent_secret"] not in body
    finally:
        conn.close()


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["claim_id"])
def test_workflow_baseline_matches_labels_on_adversarial_cases(case, tmp_path):
    store = tmp_path / f"workflow-{case['claim_id']}.sqlite"
    init_store(store, WORLD, CASES).close()
    result = run_workflow_baseline(case["claim_id"], seed=11, store_path=str(store))
    conn = connect(store)
    try:
        passed, reason = trial_pass(result.as_dict(), case["expected"], conn)
        assert passed, reason
    finally:
        conn.close()


def test_verifier_fixes_reference_swarm_seed_55_public_t02(tmp_path):
    from tests.conftest import CLAIMS

    outcomes = {}
    for name, runner in (("swarm", run_swarm), ("swarm_verified", run_claim)):
        store = tmp_path / f"{name}.sqlite"
        init_store(store, WORLD, CLAIMS).close()
        result = runner("C-002", seed=55, store_path=str(store))
        outcomes[name] = (result.status, result.proposal_amount)
    assert outcomes == {"swarm": ("resolved", 20000), "swarm_verified": ("denied", 0)}


def test_verifier_emits_override_trace_for_seed_55(tmp_path):
    from tests.conftest import CLAIMS

    store = tmp_path / "override.sqlite"
    init_store(store, WORLD, CLAIMS).close()
    result = run_claim("C-002", seed=55, store_path=str(store))
    events = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))["events"]
    assert any(event["kind"] == "verifier_override" for event in events)


def test_verified_variant_resumes_after_effect_crash_once(tmp_path):
    from tests.conftest import CLAIMS

    store = tmp_path / "verified-crash.sqlite"
    init_store(store, WORLD, CLAIMS).close()
    with pytest.raises(InjectedCrash):
        run_claim("C-001", seed=11, store_path=str(store), crash_at="after_effect_before_checkpoint")
    result = run_claim("C-001", seed=11, store_path=str(store))
    conn = connect(store)
    try:
        effect = get_refund(conn, "C-001")
        assert result.status == "resolved"
        assert effect is not None and int(effect["amount_vnd"]) == 35000
        assert committed_audit_count(conn, "C-001") == 1
    finally:
        conn.close()
