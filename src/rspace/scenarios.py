"""Deterministic synthetic fault injection for controlled experiments."""
from __future__ import annotations
import random
from .engine import WEIGHTS, POLICY_VERSION

FAULTS = tuple(WEIGHTS) + ('missing_lineage', 'unapproved_policy', 'multiple_controls', 'missing_all_controls')


def scenario_run(index: int, fault: str | None = None) -> dict:
    if fault is not None and fault not in FAULTS:
        raise ValueError(f'Unknown fault: {fault}')
    controls = {k: True for k in WEIGHTS}
    version = POLICY_VERSION
    if fault in WEIGHTS:
        controls[fault] = False
    elif fault == 'missing_lineage':
        controls.pop('lineage')
    elif fault == 'unapproved_policy':
        version = 'unapproved'
    elif fault == 'multiple_controls':
        controls['authorization'] = False
        controls['audit_trail'] = False
    elif fault == 'missing_all_controls':
        controls = {}
    return {'run_id': f'scenario-{index:07d}', 'policy_version': version,
            'controls': controls, 'synthetic': True}


def scenario_dataset(n: int, *, seed: int = 42, fault_rate: float = 0.2) -> list[dict]:
    if n < 0 or not 0 <= fault_rate <= 1:
        raise ValueError('n must be nonnegative and fault_rate between 0 and 1')
    rng = random.Random(seed)
    return [scenario_run(i, rng.choice(FAULTS) if rng.random() < fault_rate else None)
            for i in range(n)]
