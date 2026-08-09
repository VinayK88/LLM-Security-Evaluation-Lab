from __future__ import annotations

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    name: str
    arguments: Dict[str, str] = Field(default_factory=dict)


class Scenario(BaseModel):
    id: str
    category: str
    title: str
    system_policy: str
    user_prompt: str
    retrieved_content: str = ""
    protected_values: List[str] = Field(default_factory=list)
    available_tools: List[str] = Field(default_factory=list)
    allowed_tools: List[str] = Field(default_factory=list)
    requires_human_approval: bool = False
    expected_facts: List[str] = Field(default_factory=list)
    forbidden_claims: List[str] = Field(default_factory=list)


class ResponseTrace(BaseModel):
    final_answer: str
    tool_calls: List[ToolCall] = Field(default_factory=list)
    approval_requested: bool = False
    cited_facts: List[str] = Field(default_factory=list)


class CheckResult(BaseModel):
    name: str
    category: str
    passed: bool
    reason: str


class ScenarioResult(BaseModel):
    scenario_id: str
    category: str
    checks: List[CheckResult]
    score: float
    trace: ResponseTrace


class Scorecard(BaseModel):
    model: str
    overall_score: float
    category_scores: Dict[str, float]
    scenario_results: List[ScenarioResult]


class EvalRequest(BaseModel):
    model: str = "mock-safe"
