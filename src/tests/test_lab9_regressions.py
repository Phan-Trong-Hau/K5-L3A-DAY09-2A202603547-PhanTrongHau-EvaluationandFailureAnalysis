"""Trace-derived regressions: detect the first bad decision and a fluent false claim."""
from types import SimpleNamespace

import pytest

from lab8.shapes import SHAPES

pytestmark = pytest.mark.student


@pytest.fixture(autouse=True)
def restore_shape_registry():
    before = SHAPES.copy()
    yield
    SHAPES.clear()
    SHAPES.update(before)


def test_lab9_trace_ticket_override_regression():
    from lab9.graders import DbFactKept, ProposalAmountCorrect
    from lab9.trace_case import investigate

    broken = investigate('seeded_regression', 'C-002', 11)
    fixed = investigate('fixed', 'C-002', 11)
    for case, expected in ((broken, False), (fixed, True)):
        ctx = SimpleNamespace(output=case['trial'], expected_output=case['label'])
        assert DbFactKept().evaluate(ctx).value is expected
        assert ProposalAmountCorrect().evaluate(ctx).value is expected
        assert case['trial']['lab8_pass'] is expected


def test_lab9_misreport_correct_ledger_is_still_a_failure():
    from lab9.graders import ReplyLedgerConsistent
    from lab9.trace_case import investigate
    from lab9.variant_agent import make_shape

    SHAPES['test_misreport'] = make_shape('test_misreport', {'no_override', 'misreport'})
    try:
        broken = investigate('test_misreport', 'C-008', 11)
        fixed = investigate('fixed', 'C-008', 11)
        for case, expected in ((broken, False), (fixed, True)):
            assert case['trial']['snapshot']['refund_vnd'] == 20000
            ctx = SimpleNamespace(output=case['trial'], expected_output=case['label'])
            assert ReplyLedgerConsistent().evaluate(ctx).value is expected
    finally:
        SHAPES.pop('test_misreport', None)


def test_lab9_honest_paraphrase_has_no_reply_false_alarm():
    from lab9.graders import ReplyLedgerConsistent
    from lab9.trace_case import investigate

    case = investigate('honest_refactor', 'C-008', 11)
    ctx = SimpleNamespace(output=case['trial'], expected_output=case['label'])
    assert ReplyLedgerConsistent().evaluate(ctx).value is True
