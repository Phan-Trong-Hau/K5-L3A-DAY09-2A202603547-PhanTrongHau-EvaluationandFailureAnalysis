"""Dedicated unit tests for Shape B (single ReAct agent), added by Ngo Duc Thinh (2A202603548)."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from lab8.db import connect
from lab8.durability import InjectedCrash
from lab8.metrics import check_trace, ledger_snapshot
from lab8.shapes.single import run_claim


def test_single_ignores_ticket_delay_even_on_seed_55(public_db):
    """C-002 ticket claims 5 days late while order row has 2 -> denied at both seed 11 and 55."""
    for seed in (11, 55):
        result = run_claim("C-002", seed=seed, store_path=str(public_db))
        assert result.status == "denied"
        assert result.proposal_amount == 0
        assert result.refund_effects == []

    conn = connect(public_db)
    try:
        snap = ledger_snapshot(conn, "C-002")
    finally:
        conn.close()
    assert snap["refund_count"] == 0
    assert snap["policy_denied"] is False


def test_single_trace_omits_secrets_pii_and_ticket_text(public_db):
    """Trace contract v1 holds on resolved, needs_info, and escalated paths with zero secret/PII leakage."""
    expected_statuses = {
        "C-001": "resolved",
        "C-004": "needs_info",
        "C-005": "escalated",
    }
    forbidden_tokens = (
        "CANARY_SECRET",
        "Bearer",
        "0901111222",
        "99 Duong Bi Mat",
        "SECRET_ITEM_VANG",
        "CANARY_INTERNAL_O110",
        "giao trễ",
    )
    for claim_id, expected_status in expected_statuses.items():
        started_at = time.time()
        result = run_claim(claim_id, seed=11, store_path=str(public_db))
        assert result.status == expected_status
        trace_ok, trace_reason = check_trace(result.as_dict(), started_at=started_at)
        assert trace_ok, trace_reason
        blob = Path(result.trace_path).read_text(encoding="utf-8")
        for token in forbidden_tokens:
            assert token not in blob


def test_single_passes_full_quote_for_per_order_cap(public_db):
    """Shape B forwards full quote to host: T13 gets policy_denied, T14 pays only the difference."""
    t13 = run_claim("C-013", seed=11, store_path=str(public_db))
    assert t13.status == "denied"
    assert t13.proposal_amount == 35000
    assert t13.refund_effects == []
    conn = connect(public_db)
    try:
        snap = ledger_snapshot(conn, "C-013")
    finally:
        conn.close()
    assert snap["policy_denied"] is True

    t14 = run_claim("C-014", seed=11, store_path=str(public_db))
    assert t14.status == "resolved"
    assert t14.proposal_amount == 150000
    assert len(t14.refund_effects) == 1
    assert int(t14.refund_effects[0]["amount_vnd"]) == 120000


def test_single_propagates_crash_and_resumes_once(public_db):
    """InjectedCrash propagates with trace flushed, and resume keeps exactly one refund."""
    with pytest.raises(InjectedCrash):
        run_claim("C-012", seed=11, store_path=str(public_db), crash_at="after_effect_before_checkpoint")

    crash_trace = Path("traces") / "R-single-C-012-s11.json"
    assert crash_trace.is_file()
    crash_body = json.loads(crash_trace.read_text(encoding="utf-8"))
    assert any(ev["kind"] == "crash" for ev in crash_body["events"])

    resumed = run_claim("C-012", seed=11, store_path=str(public_db))
    conn = connect(public_db)
    try:
        ledger_rows = conn.execute("SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = 'C-012'").fetchone()["n"]
    finally:
        conn.close()
    assert resumed.status == "resolved"
    assert ledger_rows == 1
    assert resumed.committed_audit_count == 1


def test_single_unknown_claim_fails_cleanly_with_trace(public_db):
    """Unknown claim_id fails without raising and still writes a contract-v1 trace."""
    started_at = time.time()
    result = run_claim("C-999", seed=11, store_path=str(public_db))
    assert result.status == "failed"
    assert result.proposal_amount == 0
    assert result.error_reason == "unknown_claim"
    assert check_trace(result.as_dict(), started_at=started_at) == (True, "ok")
