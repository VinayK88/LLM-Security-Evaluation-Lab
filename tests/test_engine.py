import unittest

from app.engine import evaluate


class EngineTests(unittest.TestCase):
    def test_safe_model_scores_high(self):
        scorecard = evaluate("mock-safe")
        self.assertGreaterEqual(scorecard.overall_score, 90.0)

    def test_unsafe_model_scores_lower(self):
        safe = evaluate("mock-safe")
        unsafe = evaluate("mock-unsafe")
        self.assertLess(unsafe.overall_score, safe.overall_score)

    def test_scorecard_has_categories(self):
        scorecard = evaluate("mock-safe")
        for category in [
            "prompt_injection",
            "data_leakage",
            "tool_safety",
            "hallucination",
            "human_approval",
        ]:
            self.assertIn(category, scorecard.category_scores)


if __name__ == "__main__":
    unittest.main()
