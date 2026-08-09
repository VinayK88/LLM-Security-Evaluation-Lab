import unittest

from app.graders import (
    grade_approval,
    grade_hallucination,
    grade_secret_leakage,
    grade_tool_authorization,
)
from app.models import ResponseTrace, Scenario, ToolCall


class GraderTests(unittest.TestCase):
    def test_secret_leakage_detected(self):
        s = Scenario(
            id="x",
            category="data_leakage",
            title="x",
            system_policy="",
            user_prompt="",
            protected_values=["SECRET_X"],
        )
        trace = ResponseTrace(final_answer="The value is SECRET_X")
        self.assertFalse(grade_secret_leakage(s, trace).passed)

    def test_unauthorized_tool_detected(self):
        s = Scenario(
            id="x",
            category="tool_safety",
            title="x",
            system_policy="",
            user_prompt="",
            available_tools=["delete_user"],
            allowed_tools=[],
        )
        trace = ResponseTrace(
            final_answer="done",
            tool_calls=[ToolCall(name="delete_user")],
        )
        self.assertFalse(grade_tool_authorization(s, trace).passed)

    def test_missing_approval_detected(self):
        s = Scenario(
            id="x",
            category="human_approval",
            title="x",
            system_policy="",
            user_prompt="",
            requires_human_approval=True,
        )
        trace = ResponseTrace(final_answer="done", approval_requested=False)
        self.assertFalse(grade_approval(s, trace).passed)

    def test_hallucination_detected(self):
        s = Scenario(
            id="x",
            category="hallucination",
            title="x",
            system_policy="",
            user_prompt="",
            forbidden_claims=["malware was confirmed"],
        )
        trace = ResponseTrace(final_answer="Malware was confirmed.")
        self.assertFalse(grade_hallucination(s, trace).passed)


if __name__ == "__main__":
    unittest.main()
