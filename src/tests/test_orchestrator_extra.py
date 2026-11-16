"""Extra orchestrator-shape (Shape C) tests, prepared for Lê Hồng Quân (2A202603705).

Guarantees the orchestrator must keep beyond the T01-T14 matrix:
1. The handoff to the read-only investigator carries only allowlisted tools and
   no parent context (no write tool, no secret).
2. The ticket's claimed delay never changes the quote.
3. The trace never leaks the ticket text, the parent secret or auth headers.
"""

from __future__ import annotations

import json
from pathlib import Path

from lab8.db import connect, init_store
from lab8.metrics import ledger_snapshot
from lab8.shapes import SHAPES
from tests.conftest import CLAIMS, WORLD


def _store(tmp_path, name: str):
    path = tmp_path / name
    init_store(path, WORLD, CLAIMS).close()
    return path


def test_orchestrator_handoff_is_allowlist_only(tmp_path):
    """The investigator gets read tools only; the write tool and secrets stay behind."""
    result = SHAPES["orchestrator"]("C-001", seed=11, store_path=str(_store(tmp_path, "c001.sqlite")))
    assert result.status == "resolved"
    body = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))
    handoffs = [event["payload"] for event in body["events"] if event["kind"] == "handoff"]
    assert handoffs, "orchestrator must log the handoff it built"
    for handoff in handoffs:
        assert "issue_refund" not in handoff.get("allowed_tools", [])
        blob = json.dumps(handoff, ensure_ascii=False)
        assert "CANARY_SECRET" not in blob
        assert "Bearer" not in blob


def test_orchestrator_quotes_from_order_row_not_ticket(tmp_path):
    """C-002: ticket claims 5 days late; the order row says 2 -> quote 0 -> denied."""
    store = _store(tmp_path, "c002.sqlite")
    result = SHAPES["orchestrator"]("C-002", seed=11, store_path=str(store))
    assert result.status == "denied"
    assert result.proposal_amount == 0
    assert result.refund_effects == []
    conn = connect(store)
    try:
        snap = ledger_snapshot(conn, "C-002")
    finally:
        conn.close()
    assert snap["refund_count"] == 0
    assert snap["policy_denied"] is False


def test_orchestrator_trace_has_no_ticket_or_secret(tmp_path):
    """Trace contract v1: no secret, no header, no raw user text in the trace."""
    result = SHAPES["orchestrator"]("C-001", seed=11, store_path=str(_store(tmp_path, "c001.sqlite")))
    body = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))
    blob = json.dumps(body, ensure_ascii=False)
    assert body["run_id"] == result.run_id
    assert isinstance(body["events"], list)
    assert "CANARY_SECRET_PARENT_C-001" not in blob
    assert "Bearer" not in blob
    assert "giao trễ" not in blob
