import unittest
from rspace.engine import evaluate, WEIGHTS
from rspace.evaluation import baseline_decision, ground_truth, compare, confusion
from rspace.scenarios import scenario_run, scenario_dataset, FAULTS


class EvaluationTests(unittest.TestCase):
    def test_every_fault_blocks_rspace(self):
        for fault in FAULTS:
            with self.subTest(fault=fault):
                run = scenario_run(0, fault)
                self.assertEqual(ground_truth(run), 'BLOCK')
                self.assertEqual(evaluate(run).decision, 'BLOCK')

    def test_clean_releases(self):
        run = scenario_run(0)
        self.assertEqual(ground_truth(run), 'RELEASE')
        self.assertEqual(evaluate(run).decision, 'RELEASE')
        self.assertEqual(baseline_decision(run), 'RELEASE')

    def test_baseline_misses_audit_failure(self):
        run = scenario_run(0, 'audit_trail')
        self.assertEqual(baseline_decision(run), 'RELEASE')
        self.assertEqual(evaluate(run).decision, 'BLOCK')

    def test_baseline_misses_policy_failure(self):
        self.assertEqual(baseline_decision(scenario_run(0, 'unapproved_policy')), 'RELEASE')

    def test_dataset_determinism(self):
        self.assertEqual(scenario_dataset(100, seed=17), scenario_dataset(100, seed=17))

    def test_dataset_validation(self):
        for args in [(-1, 0.2), (10, -0.1), (10, 1.1)]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                scenario_dataset(args[0], fault_rate=args[1])

    def test_confusion(self):
        expected = ['BLOCK', 'BLOCK', 'RELEASE', 'RELEASE']
        predicted = ['BLOCK', 'RELEASE', 'BLOCK', 'RELEASE']
        result = confusion(expected, predicted)
        self.assertEqual([result[k] for k in ('tp', 'tn', 'fp', 'fn')], [1, 1, 1, 1])

    def test_comparison_no_rspace_misses(self):
        metrics = compare(scenario_dataset(500, seed=10, fault_rate=0.5))
        self.assertEqual(metrics['rspace']['fn'], 0)
        self.assertEqual(metrics['rspace']['fp'], 0)
        self.assertGreater(metrics['baseline']['fn'], 0)

    def test_unknown_fault_rejected(self):
        with self.assertRaises(ValueError):
            scenario_run(0, 'not_a_real_fault')


if __name__ == '__main__':
    unittest.main()
