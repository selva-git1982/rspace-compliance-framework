import copy
import unittest
from rspace.engine import evaluate, verify_evidence, WEIGHTS
from rspace.synthetic import make_run, generate

class EngineTests(unittest.TestCase):
    def test_all_pass(self):
        d = evaluate(make_run(1)); self.assertEqual(d.decision, "RELEASE"); self.assertEqual(d.risk_percent, 0)
    def test_each_control_failure_blocks(self):
        for key in WEIGHTS:
            with self.subTest(key=key):
                self.assertEqual(evaluate(make_run(1, fault=key)).decision, "BLOCK")
    def test_missing_lineage_blocks(self):
        d = evaluate(make_run(1, fault="missing_lineage"))
        self.assertEqual(d.outcomes["lineage"], "unknown"); self.assertEqual(d.decision, "BLOCK")
    def test_unapproved_policy_blocks(self):
        self.assertEqual(evaluate(make_run(1, fault="unapproved_policy")).decision, "BLOCK")
    def test_missing_authorization_blocks(self):
        run = make_run(1); del run["controls"]["authorization"]
        self.assertEqual(evaluate(run).decision, "BLOCK")
    def test_evidence_tampering_detected(self):
        d = evaluate(make_run(1)); self.assertTrue(verify_evidence(d.evidence, d.evidence_sha256))
        changed = copy.deepcopy(d.evidence); changed["decision"] = "BLOCK"
        self.assertFalse(verify_evidence(changed, d.evidence_sha256))
    def test_deterministic(self):
        self.assertEqual(evaluate(make_run(1)).evidence_sha256, evaluate(make_run(1)).evidence_sha256)
    def test_synthetic_reproducibility(self):
        self.assertEqual(list(generate(20, seed=4)), list(generate(20, seed=4)))
    def test_invalid_run_id(self):
        with self.assertRaises(ValueError): evaluate({"controls": {}})

if __name__ == "__main__": unittest.main()
