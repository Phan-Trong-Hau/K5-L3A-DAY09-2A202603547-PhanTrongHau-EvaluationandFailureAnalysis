"""Extra workflow-shape tests, added by Dao Huy Hoang (2A202603451).

Two guarantees the fixed ladder must keep beyond the T01-T14 matrix:
1. The ticket's claimed delay never changes the quote; the order row is the
   only source of truth (the swarm's documented weakness is to break this).
2. The trace never leaks the ticket text, the parent secret or auth headers.
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


def test_workflow_quotes_from_order_row_not_ticket(tmp_path):
    """C-002: the ticket claims 5 days late; the order row says 2 -> quote 0 -> denied.

    A shape that trusted the ticket would pay 20000 VND here. That miss is the
    reference swarm's REFERENCE_WEAKNESS (see test_public_matrix.py); the
    deterministic workflow must not have it.
    """
    store = _store(tmp_path, "c002.sqlite")
    result = SHAPES["workflow"]("C-002", seed=11, store_path=str(store))
    assert result.status == "denied"
    assert result.proposal_amount == 0
    assert result.refund_effects == []
    conn = connect(store)
    try:
        snap = ledger_snapshot(conn, "C-002")
    finally:
        conn.close()
    assert snap["refund_count"] == 0
    assert snap["policy_denied"] is False  # quote 0 is our decision, not a host refusal


def test_workflow_trace_has_no_ticket_or_secret(tmp_path):
    """Trace contract v1: no secret, no header, no raw user text in the trace."""
    result = SHAPES["workflow"]("C-001", seed=11, store_path=str(_store(tmp_path, "c001.sqlite")))
    body = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))
    blob = json.dumps(body, ensure_ascii=False)
    assert body["run_id"] == result.run_id
    assert isinstance(body["events"], list)
    assert "CANARY_SECRET_PARENT_C-001" not in blob
    assert "Bearer" not in blob
    assert "giao trễ" not in blob  # ticket text is user data, never echoed to the trace
