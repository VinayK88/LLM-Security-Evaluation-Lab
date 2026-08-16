from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)


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

    # Optional provenance for real-model evaluation. Mock adapters leave these
    # unset so deterministic tests remain dependency-free.
    provider: Optional[str] = None
    model_name: Optional[str] = None
    response_id: Optional[str] = None
    stop_reason: Optional[str] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    latency_ms: Optional[float] = None


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
