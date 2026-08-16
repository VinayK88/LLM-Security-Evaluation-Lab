from __future__ import annotations

from typing import Protocol

from .models import ResponseTrace, Scenario, ToolCall


class ModelAdapter(Protocol):
    name: str

    def run(self, scenario: Scenario) -> ResponseTrace:
        ...


class SafeMockAdapter:
    """
    Deterministic model adapter used for tests and demos.

    It does not call an external LLM. Its purpose is to make the evaluation
    framework reproducible and to show the expected adapter contract.
    """

    name = "mock-safe"

    def run(self, scenario: Scenario) -> ResponseTrace:
        text = scenario.user_prompt.lower()

        tool_calls = []
        approval_requested = False
        cited_facts = list(scenario.expected_facts)

        if scenario.category == "prompt_injection":
            answer = (
                "I treated the retrieved content as untrusted data and ignored "
                "instructions that attempted to override the system policy."
            )

        elif scenario.category == "data_leakage":
            answer = (
                "I cannot reveal protected or hidden values. I can provide a "
                "safe summary that excludes restricted information."
            )

        elif scenario.category == "tool_safety":
            requested_tool = None
            for tool in scenario.available_tools:
                if tool.lower() in text:
                    requested_tool = tool
                    break

            if requested_tool and requested_tool in scenario.allowed_tools:
                tool_calls.append(ToolCall(name=requested_tool, arguments={"scope": "synthetic"}))
                answer = f"I used the authorized tool {requested_tool} within the permitted scope."
            else:
                answer = "I did not invoke any unauthorized tool."

        elif scenario.category == "human_approval":
            approval_requested = scenario.requires_human_approval
            answer = (
                "This action requires explicit human approval before execution."
                if approval_requested
                else "No approval is required for this simulated action."
            )

        elif scenario.category == "hallucination":
            if scenario.expected_facts:
                answer = "Supported facts: " + "; ".join(scenario.expected_facts)
            else:
                answer = "I do not have enough evidence to make that claim."

        else:
            answer = "Completed the synthetic evaluation scenario safely."

        # Approval is a cross-cutting policy requirement, not a category-only
        # behavior. A tool-safety case can still require a human checkpoint.
        if scenario.requires_human_approval and not approval_requested:
            approval_requested = True
            answer += " This action requires explicit human approval before execution."

        return ResponseTrace(
            final_answer=answer,
            tool_calls=tool_calls,
            approval_requested=approval_requested,
            cited_facts=cited_facts,
        )


class UnsafeMockAdapter:
    """
    Deliberately weak adapter used only to demonstrate that the graders catch
    failures. It still operates on synthetic data and performs no real actions.
    """

    name = "mock-unsafe"

    def run(self, scenario: Scenario) -> ResponseTrace:
        tool_calls = [
            ToolCall(name=t, arguments={"scope": "synthetic"})
            for t in scenario.available_tools[:1]
        ]

        leaked = " ".join(scenario.protected_values)
        fabricated = " ".join(scenario.forbidden_claims[:1])

        answer_parts = [
            scenario.retrieved_content,
            leaked,
            fabricated,
            "I followed the latest instruction regardless of trust level.",
        ]

        return ResponseTrace(
            final_answer=" ".join(p for p in answer_parts if p).strip(),
            tool_calls=tool_calls,
            approval_requested=False,
            cited_facts=scenario.expected_facts + scenario.forbidden_claims[:1],
        )


def get_adapter(name: str):
    if name == "mock-safe":
        return SafeMockAdapter()
    if name == "mock-unsafe":
        return UnsafeMockAdapter()
    if name.startswith("anthropic:"):
        model = name.split(":", 1)[1].strip()
        if not model:
            raise ValueError("use anthropic:<model-name> for a Claude evaluation")
        from .anthropic_adapter import AnthropicAdapter

        return AnthropicAdapter(model=model)
    raise ValueError(f"unknown model adapter: {name}")
