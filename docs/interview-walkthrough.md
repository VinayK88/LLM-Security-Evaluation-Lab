# Interview Walkthrough

## 60-second answer

"I built an LLM security evaluation lab because production agentic systems need measurable release criteria, not just ad hoc prompt testing. Each benchmark scenario defines trusted policy, user input, untrusted retrieved content, protected values, available and authorized tools, and whether human approval is required.

The runner captures the entire agent trace, then independent graders evaluate prompt-injection resistance, data leakage, tool authorization, hallucination, and approval compliance. I produce per-category scores and an overall scorecard, and the CLI can enforce a minimum threshold so the same benchmark becomes a CI quality gate.

For production, I would add real model adapters, judge-model grading for semantic failures, repeated stochastic trials, confidence intervals, benchmark versioning, and OpenTelemetry traces."

## Why this is better than prompt-only testing

Prompt-only testing checks:

```text
input -> output
```

Agent evaluation checks:

```text
input
  |
  v
reasoning workflow
  |
  +--> retrieval
  |
  +--> tool selection
  |
  +--> tool arguments
  |
  +--> approval gate
  |
  v
final output
```

Security failures can happen anywhere in that trace.

## Useful interview point

A model that improves answer quality can still regress on:

- secret leakage
- tool restraint
- refusal behavior
- approval compliance

So quality and safety metrics must be tracked independently.
