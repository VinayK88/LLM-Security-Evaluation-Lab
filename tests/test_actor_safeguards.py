import unittest

from app.actor_safeguards import (
    actor_risk_trajectory,
    benchmark_fixture,
    evaluate_actor,
    run_actor_benchmark,
)


class ActorSafeguardsTests(unittest.TestCase):
    def test_persistent_misuse_escalates_before_harm(self):
        fixture = benchmark_fixture()["persistent_misuse"]
        decision = evaluate_actor(fixture)
        self.assertIn(decision.action, {"REVIEW", "RESTRICT"})
        self.assertTrue(decision.detected_before_harm)
        self.assertIsNotNone(decision.first_detection_minute)
        self.assertLess(decision.first_detection_minute, 51)

    def test_security_researcher_is_hard_negative(self):
        fixture = benchmark_fixture()["security_researcher"]
        decision = evaluate_actor(fixture)
        self.assertNotIn(decision.action, {"REVIEW", "RESTRICT"})
        self.assertIn("legitimate_security_research_context", decision.reasons)

    def test_benign_user_is_not_escalated(self):
        decision = evaluate_actor(benchmark_fixture()["benign_user"])
        self.assertIn(decision.action, {"ALLOW", "FRICTION"})

    def test_trajectory_is_ordered_and_bounded(self):
        rows = benchmark_fixture()["persistent_misuse"]
        trajectory = actor_risk_trajectory(rows)
        self.assertEqual([minute for minute, _ in trajectory], sorted(row.minute for row in rows))
        self.assertTrue(all(0.0 <= risk <= 1.0 for _, risk in trajectory))

    def test_benchmark_reports_operational_metrics(self):
        report = run_actor_benchmark()
        metrics = report["metrics"]
        self.assertTrue(metrics["persistent_misuse_detected"])
        self.assertTrue(metrics["pre_harm_detection"])
        self.assertFalse(metrics["researcher_escalated"])
        self.assertFalse(metrics["benign_escalated"])
        self.assertEqual(metrics["hard_negative_false_positive_rate"], 0.0)


if __name__ == "__main__":
    unittest.main()
