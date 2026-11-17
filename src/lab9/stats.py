"""Classifier calibration and paired reliability statistics for Lab09.

FAIL is the positive class: a judge's job is to find failures. Bootstrap units
are items, with seeds averaged within each item before resampling.
"""
from __future__ import annotations

import math
from collections.abc import Sequence

POS = 'FAIL'


def confusion(human: Sequence[str], judge: Sequence[str]) -> dict[str, int]:
    """Return tp/fp/fn/tn with FAIL as positive."""
    if len(human) != len(judge):
        raise ValueError('label lengths differ')
    counts = dict.fromkeys(('tp', 'fp', 'fn', 'tn'), 0)
    for h, j in zip(human, judge):
        h, j = str(h).strip().upper(), str(j).strip().upper()
        if h not in ('FAIL', 'PASS') or j not in ('FAIL', 'PASS'):
            raise ValueError('labels must be PASS or FAIL')
        key = ('tp' if j == POS else 'fn') if h == POS else ('fp' if j == POS else 'tn')
        counts[key] += 1
    return counts


def precision_recall(human: Sequence[str], judge: Sequence[str]) -> tuple[float, float]:
    c = confusion(human, judge)
    predicted, actual = c['tp'] + c['fp'], c['tp'] + c['fn']
    return (c['tp'] / predicted if predicted else 0.0,
            c['tp'] / actual if actual else 0.0)


def cohen_kappa(human: Sequence[str], judge: Sequence[str]) -> float:
    """Raise ValueError when agreement is undefined, including constant agreement."""
    c = confusion(human, judge)
    n = sum(c.values())
    if not n:
        raise ValueError('kappa undefined for empty labels')
    observed = (c['tp'] + c['tn']) / n
    human_positive = (c['tp'] + c['fn']) / n
    judge_positive = (c['tp'] + c['fp']) / n
    expected = human_positive * judge_positive + (1 - human_positive) * (1 - judge_positive)
    if expected == 1:
        raise ValueError('kappa undefined when expected agreement is 1')
    return (observed - expected) / (1 - expected)


def rogan_gladen(observed_rate: float, sensitivity: float, specificity: float) -> float:
    """Correct observed failure prevalence; clip to [0, 1]."""
    if any(not math.isfinite(v) or not 0 <= v <= 1
           for v in (observed_rate, sensitivity, specificity)):
        raise ValueError('rates must be finite probabilities')
    denominator = sensitivity + specificity - 1
    if denominator <= 0:
        raise ValueError('sensitivity + specificity must exceed 1')
    return min(1.0, max(0.0, (observed_rate + specificity - 1) / denominator))


def paired_bootstrap(a: Sequence[float], b: Sequence[float], *, n_resamples: int = 1000,
                     rng: int = 2027, confidence: float = 0.95) -> tuple[float, float, float]:
    """Return mean(a-b), lower CI, upper CI, resampling matched items together."""
    import numpy as np
    from scipy.stats import bootstrap

    if len(a) != len(b) or len(a) == 0:
        raise ValueError('paired samples must have equal nonzero length')
    x, y = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if x.ndim != 1 or y.ndim != 1 or not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError('samples must be finite one-dimensional sequences')
    if n_resamples <= 0 or not 0 < confidence < 1:
        raise ValueError('invalid bootstrap parameters')
    if np.array_equal(x, y):
        return 0.0, 0.0, 0.0
    if len(x) == 1:
        delta = float(x[0] - y[0])
        return delta, delta, delta
    result = bootstrap((x, y), lambda x, y, axis: np.mean(x - y, axis=axis),
                       paired=True, method='percentile', n_resamples=n_resamples,
                       confidence_level=confidence, rng=np.random.default_rng(rng))
    return float(np.mean(x - y)), float(result.confidence_interval.low), float(result.confidence_interval.high)


def _validate_counts(n: int, c: int, k: int) -> None:
    if any(not isinstance(v, int) or isinstance(v, bool) for v in (n, c, k)):
        raise ValueError('counts must be integers')
    if not 0 <= c <= n or not 1 <= k <= n:
        raise ValueError('require 0 <= c <= n and 1 <= k <= n')


def pass_at_k(n: int, c: int, k: int) -> float:
    """P(at least one success): 1 - C(n-c,k)/C(n,k)."""
    _validate_counts(n, c, k)
    return 1 - math.comb(n - c, k) / math.comb(n, k) if n - c >= k else 1.0


def pass_hat_k(n: int, c: int, k: int) -> float:
    """P(all k succeed): C(c,k)/C(n,k). Undefined when k > n."""
    _validate_counts(n, c, k)
    return math.comb(c, k) / math.comb(n, k) if c >= k else 0.0
