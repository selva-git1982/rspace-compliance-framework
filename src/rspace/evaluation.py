"""Explicit, reproducible comparison against a limited baseline.

Baseline: evaluates only authorization, encryption and integrity; missing/false
values fail closed. It does not check lineage, approval, audit or policy version.
This is an illustrative ablation, NOT an industry-standard competitor.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping, Any
from .engine import evaluate

BASELINE_CONTROLS = ('authorization', 'encryption', 'integrity')


def baseline_decision(run: Mapping[str, Any]) -> str:
    controls = run.get('controls')
    if not isinstance(controls, dict):
        return 'BLOCK'
    return 'RELEASE' if all(controls.get(k) is True for k in BASELINE_CONTROLS) else 'BLOCK'


def ground_truth(run: Mapping[str, Any]) -> str:
    """Synthetic oracle: independently specify the six mandatory controls + policy."""
    controls = run.get('controls')
    from .engine import WEIGHTS, POLICY_VERSION
    if not isinstance(controls, dict):
        return 'BLOCK'
    return ('RELEASE' if all(controls.get(k) is True for k in WEIGHTS)
            and run.get('policy_version') == POLICY_VERSION else 'BLOCK')


def confusion(expected: list[str], predicted: list[str]) -> dict:
    if len(expected) != len(predicted):
        raise ValueError('length mismatch')
    tp = sum(e == 'BLOCK' and p == 'BLOCK' for e, p in zip(expected, predicted))
    tn = sum(e == 'RELEASE' and p == 'RELEASE' for e, p in zip(expected, predicted))
    fp = sum(e == 'RELEASE' and p == 'BLOCK' for e, p in zip(expected, predicted))
    fn = sum(e == 'BLOCK' and p == 'RELEASE' for e, p in zip(expected, predicted))
    return dict(tp=tp, tn=tn, fp=fp, fn=fn,
                precision=tp / (tp + fp) if tp + fp else None,
                recall=tp / (tp + fn) if tp + fn else None,
                specificity=tn / (tn + fp) if tn + fp else None,
                accuracy=(tp + tn) / len(expected) if expected else None)


def compare(runs: list[dict]) -> dict:
    expected = [ground_truth(r) for r in runs]
    return {
        'rspace': confusion(expected, [evaluate(r).decision for r in runs]),
        'baseline': confusion(expected, [baseline_decision(r) for r in runs]),
    }
