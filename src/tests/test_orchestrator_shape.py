"""Orchestrator shape (shape C): read-only investigators, sanitized handoff, trace on every return path."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from lab8.db import connect
from lab8.durability import InjectedCrash
from lab8.handoff import ALLOWED_FIELDS, READONLY_TOOLS
from lab8.shapes import orchestrator
from lab8.shapes.orchestrator import INVESTIGATOR_TOOLS


def _run(store: Path, claim_id: str, *, seed: int = 11, crash_at: str | None = None):
    return orchestrator.run_claim(claim_id, seed=seed, store_path=str(store), crash_at=crash_at)


def _events(result) -> list[dict]:
    body = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))
    return body["events"]


def test_investigator_tools_are_all_read_only():
    assert set(INVESTIGATOR_TOOLS) <= READONLY_TOOLS


def test_handoff_in_trace_keeps_only_allowlisted_fields_and_no_secret(public_db):
    result = _run(public_db, "C-001")
    events = _events(result)
    handoff = next(event["payload"] for event in events if event["kind"] == "handoff")
    assert set(handoff) <= ALLOWED_FIELDS
    text = json.dumps(events, ensure_ascii=False)
    assert "CANARY_SECRET" not in text
    assert "Bearer" not in text


def test_needs_info_path_still_writes_a_trace_for_this_run(public_db):
    result = _run(public_db, "C-004")
    assert result.status == "needs_info"
    assert result.run_id in Path(result.trace_path).name
    body = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))
    assert body["run_id"] == result.run_id
    assert isinstance(body["events"], list)


def test_escalated_trace_does_not_contain_order_pii_or_internal_notes(public_db):
    result = _run(public_db, "C-005")
    assert result.status == "escalated"
    text = Path(result.trace_path).read_text(encoding="utf-8")
    for forbidden in ("0901111222", "99 Duong Bi Mat", "SECRET_ITEM_VANG", "CANARY_INTERNAL_O110"):
        assert forbidden not in text


def test_denied_by_approval_gate_refunds_nothing(public_db):
    result = _run(public_db, "C-007")
    assert result.status == "denied"
    assert result.refund_effects == []
    assert result.committed_audit_count == 0


def test_quote_is_full_entitlement_and_host_pays_only_the_difference(public_db):
    result = _run(public_db, "C-014")
    assert result.proposal_amount == 150000
    assert result.status == "resolved"
    assert int(result.refund_effects[0]["amount_vnd"]) == 120000


def test_crash_propagates_and_resume_keeps_one_refund(public_db):
    with pytest.raises(InjectedCrash):
        _run(public_db, "C-012", crash_at="after_effect_before_checkpoint")
    resumed = _run(public_db, "C-012")
    conn = connect(public_db)
    try:
        ledger_rows = conn.execute("SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = 'C-012'").fetchone()["n"]
    finally:
        conn.close()
    assert resumed.status == "resolved"
    assert ledger_rows == 1
    assert resumed.committed_audit_count == 1
