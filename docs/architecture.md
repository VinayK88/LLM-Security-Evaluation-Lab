# Production Architecture

## Reference deployment

```text
Benchmark Registry
      |
      v
Evaluation Orchestrator
      |
      +----------+-----------+------------+
      |          |           |            |
      v          v           v            v
 Model A      Model B     Agent A      Agent B
      |          |           |            |
      +----------+-----------+------------+
                 |
                 v
             Trace Store
                 |
       +---------+---------+
       |         |         |
       v         v         v
  Rule grader  Judge LLM  Policy engine
       |         |         |
       +---------+---------+
                 |
                 v
             Scorecard
                 |
       +---------+---------+
       |                   |
       v                   v
   CI release gate     Analyst dashboard
```

## Evaluation contract

A scenario should be versioned and include:

- trusted system policy
- user prompt
- untrusted context
- tool inventory
- allowed tool scopes
- approval requirements
- protected values
- expected facts
- forbidden claims
- grader configuration

## Why traces matter

For agents, text output alone is insufficient.

Capture:

- model messages
- tool selection
- tool arguments
- tool results
- approval checkpoints
- retrieval sources
- final answer
- latency
- token usage
- policy decisions

A final answer can look safe even if the agent attempted an unsafe tool call earlier.

## Grading strategy

Use multiple grader types.

### Deterministic graders

Best for:

- exact secret leakage
- unauthorized tool calls
- missing approval checkpoints
- schema violations
- forbidden actions

### Model-based graders

Useful for:

- subtle hallucination
- instruction-following quality
- nuanced policy compliance
- semantic leakage

Judge models should not be the only source of truth.

## Statistical evaluation

Production release decisions should include:

- benchmark size
- repeated trials for stochastic models
- bootstrap confidence intervals
- category-level regressions
- paired comparisons between model versions

Avoid treating a single aggregate score as sufficient.

## CI gate

Example:

```text
overall >= 90
prompt_injection >= 95
data_leakage == 100
human_approval == 100
no critical scenario regressions
```

## Data governance

Never put real credentials or production secrets into evaluation datasets.

Use synthetic canary values designed specifically to detect leakage.
