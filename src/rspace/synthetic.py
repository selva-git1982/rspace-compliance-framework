"""Deterministic synthetic runs; no clinical or employer data."""
import random
from .engine import WEIGHTS, POLICY_VERSION


def make_run(i: int, *, fault: str | None = None) -> dict:
    controls = {key: True for key in WEIGHTS}
    if fault in controls:
        controls[fault] = False
    if fault == "missing_lineage":
        del controls["lineage"]
    return {"run_id": f"synthetic-{i:07d}", "policy_version":
            "unapproved" if fault == "unapproved_policy" else POLICY_VERSION,
            "controls": controls, "synthetic": True}


def generate(n: int, *, seed: int = 42, fault_rate: float = 0.2):
    if n < 0 or not 0 <= fault_rate <= 1:
        raise ValueError("Invalid n or fault_rate")
    rng = random.Random(seed)
    faults = list(WEIGHTS) + ["missing_lineage", "unapproved_policy"]
    for i in range(n):
        fault = rng.choice(faults) if rng.random() < fault_rate else None
        yield make_run(i, fault=fault), fault
