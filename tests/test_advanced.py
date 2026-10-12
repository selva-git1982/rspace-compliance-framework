import copy
import unittest
from rspace.engine import evaluate
from rspace.audit import make_manifest, verify_manifest, append_record, verify_chain
from rspace.advanced import ALL_CHECKS, ablated_decision, evaluate_dataset, multi_seed, aggregate
from rspace.scenarios import scenario_run

class AdvancedTests(unittest.TestCase):
    def test_manifest_verifies(self):
        m = make_manifest(evaluate(scenario_run(1)))
        self.assertTrue(verify_manifest(m))
    def test_manifest_tampering(self):
        m = make_manifest(evaluate(scenario_run(1)))
        m['decision']['evidence']['decision'] = 'BLOCK'
        self.assertFalse(verify_manifest(m))
    def test_chain_detects_tampering(self):
        chain = []
        for i in range(3):
            append_record(chain, make_manifest(evaluate(scenario_run(i))))
        head = chain[-1]['record_sha256']
        self.assertTrue(verify_chain(chain, expected_head=head))
        self.assertFalse(verify_chain(chain[:-1], expected_head=head))
        chain[1]['previous_sha256'] = '0'*64
        self.assertFalse(verify_chain(chain))
    def test_invalid_manifest_rejected(self):
        with self.assertRaises(ValueError):
            append_record([], {'bad': True})
    def test_each_ablation_is_observable(self):
        from rspace.engine import WEIGHTS
        for k in ALL_CHECKS:
            with self.subTest(k=k):
                r = scenario_run(1, k if k in WEIGHTS else 'unapproved_policy')
                self.assertEqual(ablated_decision(r, ALL_CHECKS), 'BLOCK')
                self.assertEqual(ablated_decision(r, [x for x in ALL_CHECKS if x != k]), 'RELEASE')
    def test_comparison_has_expected_methods(self):
        rows = evaluate_dataset([scenario_run(1), scenario_run(2, 'missing_lineage')])
        self.assertEqual(rows['rspace']['fn'], 0)
        self.assertEqual(rows['limited_baseline']['fn'], 1)
        self.assertIn('without_lineage', rows)
    def test_reproducibility(self):
        a = multi_seed(sizes=(20,), rates=(.3,), seeds=(1,2))
        self.assertEqual(a, multi_seed(sizes=(20,), rates=(.3,), seeds=(1,2)))
        self.assertEqual(len(aggregate(a)), 9)
    def test_zero_faults(self):
        rows = multi_seed(sizes=(10,), rates=(0,), seeds=(1,))
        self.assertIsNone(rows[0]['recall'])
    def test_missing_control_blocks(self):
        r = scenario_run(1)
        del r['controls']['lineage']
        self.assertEqual(ablated_decision(r, ALL_CHECKS), 'BLOCK')

if __name__ == '__main__':
    unittest.main()
