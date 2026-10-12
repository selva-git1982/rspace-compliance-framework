"""Deterministic fail-closed policy evaluation for synthetic pipeline runs."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from hashlib import sha256
import json
from typing import Mapping, Any

WEIGHTS = {"authorization": 5, "encryption": 5, "integrity": 5,
           "lineage": 3, "validation_approval": 5, "audit_trail": 4}
POLICY_VERSION = "rspace-demo-v1"


def canonical_bytes(obj: Mapping[str, Any]) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(obj: Mapping[str, Any]) -> str:
    return sha256(canonical_bytes(obj)).hexdigest()


@dataclass(frozen=True)
class Decision:
    run_id: str
    policy_version: str
    decision: str
    risk_percent: float
    outcomes: dict[str, str]
    evidence: dict[str, Any]
    evidence_sha256: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate(run: Mapping[str, Any], *, policy_version: str = POLICY_VERSION) -> Decision:
    if not isinstance(run.get("run_id"), str) or not run["run_id"].strip():
        raise ValueError("run_id must be a non-empty string")
    observations = run.get("controls", {})
    if not isinstance(observations, dict):
        observations = {}
    outcomes = {key: ("pass" if observations.get(key) is True else
                      "fail" if observations.get(key) is False else "unknown")
                for key in WEIGHTS}
    version_ok = run.get("policy_version") == policy_version
    total_weight = sum(WEIGHTS.values())
    failed_weight = sum(weight for key, weight in WEIGHTS.items() if outcomes[key] != "pass")
    risk = 100.0 * failed_weight / total_weight
    release = failed_weight == 0 and version_ok
    evidence = {
        "run_id": run["run_id"], "policy_version_expected": policy_version,
        "policy_version_observed": run.get("policy_version"),
        "policy_version_approved": version_ok,
        "control_outcomes": outcomes,
        "decision": "RELEASE" if release else "BLOCK",
        "risk_percent": round(risk, 6),
        "source_digest": digest(run),
        "schema_version": "1.0",
    }
    # Hash only the canonical payload; do not embed the hash in its own digest input.
    return Decision(run["run_id"], policy_version, evidence["decision"],
                    evidence["risk_percent"], outcomes, evidence, digest(evidence))


def verify_evidence(evidence: Mapping[str, Any], expected_sha256: str) -> bool:
    return digest(evidence) == expected_sha256
