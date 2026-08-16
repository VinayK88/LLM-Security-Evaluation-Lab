import unittest

from app.adapters import SafeMockAdapter
from app.repeated_eval import run_repeated_evaluation


class RepeatedEvaluationTests(unittest.TestCase):
    def test_repeated_safe_mock_is_stable(self):
        report = run_repeated_evaluation(lambda: SafeMockAdapter(), trials=3)
        self.assertEqual(report["trials"], 3)
        self.assertEqual(report["overall"]["mean"], 100.0)
        self.assertEqual(report["overall"]["stdev"], 0.0)
        self.assertEqual(report["overall"]["ci95_low"], 100.0)
        self.assertEqual(report["overall"]["ci95_high"], 100.0)
        self.assertEqual(report["failure_frequency"], {})

    def test_requires_positive_trial_count(self):
        with self.assertRaises(ValueError):
            run_repeated_evaluation(lambda: SafeMockAdapter(), trials=0)


if __name__ == "__main__":
    unittest.main()
