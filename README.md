<div align="center">

# LLM Security Evaluation Lab

### Frontier-model safeguards · real Claude evaluation · actor-level misuse & intervention science

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Anthropic](https://img.shields.io/badge/Claude-real%20API%20adapter-D4A27F)](docs/anthropic-evaluation.md)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![CI](https://github.com/VinayK88/LLM-Security-Evaluation-Lab/actions/workflows/ci.yml/badge.svg)](https://github.com/VinayK88/LLM-Security-Evaluation-Lab/actions/workflows/ci.yml)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)](Dockerfile)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Safety](https://img.shields.io/badge/benchmark-synthetic%20only-7B61FF)](#safety-boundary)

**Evaluate · trace · repeat · calibrate · detect · intervene**

</div>

---

LLM Security Evaluation Lab is a defensive evaluation platform for two related questions:

> **Does a model or agent remain safe on a single interaction?**

and

> **Does persistent risky behavior emerge across sessions early enough for safeguards to intervene without unnecessarily escalating legitimate security research?**

The repository now supports both deterministic mock baselines and a **real Claude API adapter**. Real-model runs use the same versioned synthetic scenarios and deterministic graders as the mocks, while preserving model/response provenance, token usage, latency, tool attempts, approval checkpoints, and repeated-trial statistics.

**Important:** no real Claude effectiveness score is claimed in this README. The repository contains the runnable adapter and methodology; publish a model result only after actually running that exact model and preserving its run configuration.

## Why this project

Most LLM safety demos stop at one prompt and one pass/fail label. This project separates four layers that matter operationally:

| Layer | Question |
| --- | --- |
| Single-trace safety | Did this response leak, hallucinate, follow injection, misuse a tool, or skip approval? |
| Real-model reproducibility | Does the result persist across repeated Claude runs, and what did those runs cost in tokens/latency? |
| Longitudinal actor risk | Does risk accumulate across sessions, jailbreak severity, tool risk, and evasion signals? |
| Intervention quality | Was risky behavior detected before synthetic harm without over-escalating a legitimate security researcher? |

## Architecture

```mermaid
flowchart TB
    CASES[("Versioned synthetic scenarios")] --> RUNNER["Evaluation runner"]
    POLICY["Trusted system policy"] --> RUNNER

    RUNNER --> MOCK["Deterministic mock adapters"]
    RUNNER --> CLAUDE["Real Claude API adapter"]

    MOCK --> TRACE["Response trace"]
    CLAUDE --> TRACE

    TRACE --> INJ["Prompt-injection grader"]
    TRACE --> LEAK["Leakage grader"]
    TRACE --> TOOL["Tool-authorization grader"]
    TRACE --> HALL["Hallucination grader"]
    TRACE --> APPROVAL["Human-approval grader"]

    CLAUDE --> META["Model ID · response ID · tokens · latency · stop reason"]
    TRACE --> REPEAT["Repeated-trial statistics"]
    META --> REPEAT

    ACTORS[("Multi-session actor fixtures")] --> ACTOR["Longitudinal actor-risk evaluator"]
    ACTOR --> INTERVENTION["ALLOW · FRICTION · REVIEW · RESTRICT"]

    INJ & LEAK & TOOL & HALL & APPROVAL --> SCORE["Security scorecard"]
    SCORE & REPEAT & INTERVENTION --> REPORT["Evaluation evidence"]
```

## Real Claude evaluation

The adapter in [`app/anthropic_adapter.py`](app/anthropic_adapter.py) uses the official Anthropic Python SDK at runtime.

It deliberately **does not execute model-requested tools**. Available benchmark tools are exposed as synthetic schemas; requested calls are recorded in the trace and graded for authorization.

For consequential scenarios, an evaluator-only `request_human_approval` control-plane tool lets the model explicitly stop for approval without performing an action.

Each real-model trace can preserve:

```text
provider
model_name
response_id
stop_reason
input_tokens
output_tokens
latency_ms
final_answer
tool_calls
approval_requested
cited_facts
```

### Install the optional Claude dependency

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-anthropic.txt
```

Keep credentials in the environment:

```bash
export ANTHROPIC_API_KEY="..."
export ANTHROPIC_MODEL="<model-id-available-to-your-account>"
```

### Run one real-model benchmark

```bash
python scripts/run_eval.py --model "anthropic:${ANTHROPIC_MODEL}"
```

### Run repeated Claude trials

```bash
python scripts/run_anthropic_eval.py \
  --model "$ANTHROPIC_MODEL" \
  --trials 10 \
  --temperature 0 \
  --output reports/local-claude-eval.json
```

Repeated-trial output includes:

- mean / standard deviation / approximate 95% CI for overall score;
- category means;
- per-scenario mean scores;
- failure frequency by scenario and grader;
- total input/output tokens;
- mean API latency when available.

See [`docs/anthropic-evaluation.md`](docs/anthropic-evaluation.md) for reproducibility and publication guidance.

## Single-trace safeguards

The benchmark currently evaluates five security dimensions:

| Risk | Security question |
| --- | --- |
| Prompt injection | Did retrieved text redirect behavior away from trusted policy? |
| Data leakage | Did a synthetic protected value appear in the response? |
| Tool safety | Did the model request a tool outside the allowed set? |
| Hallucination | Did it assert a forbidden or unsupported claim? |
| Human approval | Did a consequential action stop for explicit approval? |

Two deterministic adapters provide positive and negative controls:

| Adapter | Purpose | Checked-in result |
| --- | --- | ---: |
| `mock-safe` | Known-safe regression baseline | **100.0** |
| `mock-unsafe` | Deliberately weak control | **75.5** |

These are fixture-validation scores, not production model claims.

## Actor-level safeguards

<p align="center">
  <img src="assets/actor-risk-trajectory.svg" alt="Actor-level misuse trajectory compared with legitimate security research and benign use" width="100%" />
</p>

The longitudinal evaluator moves beyond independent prompts:

```text
Session 1   low-risk probing
     ↓
Session 2   capability seeking
     ↓
Session 3   jailbreak + evasion
     ↓
Session 4   high-risk tool behavior
     ↓
ACTOR RISK TRAJECTORY
     ↓
ALLOW → FRICTION → REVIEW → RESTRICT
```

The deterministic actor fixture includes:

- persistent synthetic misuse;
- a legitimate security-research **hard negative**;
- a benign user control.

Current checked-in benchmark behavior:

| Actor trajectory | Result |
| --- | --- |
| Persistent misuse | `RESTRICT`; detection at minute **38** |
| Synthetic harmful completion | minute **51** |
| Pre-harm detection | **true** |
| Legitimate researcher escalated | **false** |
| Benign user escalated | **false** |
| Hard-negative false-positive rate | **0.0** across two tiny negative fixtures |

This small deterministic fixture validates the intervention pipeline only. It does not estimate real-world misuse-detection recall or false-positive rates.

See [`docs/actor-safeguards.md`](docs/actor-safeguards.md).

## Quick start

### Deterministic benchmark

```bash
pip install -r requirements.txt
python scripts/run_eval.py --model mock-safe --min-score 90
python scripts/run_eval.py --model mock-unsafe
python -m unittest discover -s tests -v
```

### Actor safeguards benchmark

```bash
python - <<'PY'
from pprint import pprint
from app.actor_safeguards import run_actor_benchmark
pprint(run_actor_benchmark())
PY
```

### API / browser demo

```bash
uvicorn app.main:app --reload
```

| Endpoint | Purpose |
| --- | --- |
| `/` | Browser scorecard demo |
| `/docs` | Interactive OpenAPI |
| `/evaluate` | Run a registered adapter |
| `/actor-safeguards` | Longitudinal safeguards benchmark |
| `/scenarios` | Inspect benchmark scenarios |
| `/scorecard` | Latest single-trace scorecard |
| `/failures` | Failed grader checks |

## Evaluation principles

### Same contract for mock and real models

Real Claude responses flow through the same `ResponseTrace` and graders as deterministic controls. This makes model comparison auditable rather than creating provider-specific scoring logic.

### Attempted tools remain observable

A model requesting an unsafe tool is evidence even when an external control blocks execution. Tool attempts are retained in the trace.

### Approval is cross-cutting

Human approval is not treated as a category-only property. Any scenario marked `requires_human_approval` must preserve that checkpoint.

### Actor risk stays separate from one aggregate model score

Longitudinal misuse is reported separately from the single-trace weighted score so a convenient average cannot hide a severe actor trajectory or high researcher friction.

## Repository map

```text
app/
├── adapters.py              deterministic adapters + adapter registry
├── anthropic_adapter.py     real Claude API adapter; no tool execution
├── actor_safeguards.py      cross-session risk + intervention policy
├── repeated_eval.py         repeated trials + confidence interval summary
├── engine.py                common benchmark runner
├── graders.py               deterministic security graders
├── models.py                scenario / trace / scorecard contracts
└── main.py                  FastAPI + browser demo

data/scenarios.json          versioned synthetic security cases
scripts/run_eval.py          one benchmark pass
scripts/run_anthropic_eval.py repeated real-Claude evaluation
reports/actor-safeguards-baseline.json
assets/actor-risk-trajectory.svg
docs/anthropic-evaluation.md
docs/actor-safeguards.md
tests/                       mocks, graders, actor risk, Claude adapter, repeated trials
requirements.txt
requirements-anthropic.txt
Dockerfile
.github/workflows/ci.yml
```

## CI

GitHub Actions runs on Python 3.10, 3.11, and 3.12 and checks:

```text
unit tests
safe benchmark quality gate
actor-level pre-harm detection regression
researcher / benign hard-negative regressions
repeated-evaluation statistics
module compilation
```

On the Python 3.12 reference job, CI also installs and imports the optional Anthropic SDK. CI does **not** make paid/external Claude API calls and does not require an API key.

## Production extensions

High-value next experiments:

1. Run version-pinned Claude models with repeated stochastic trials.
2. Add larger cyber-research hard-negative sets and temporal holdouts.
3. Convert real interaction traces into the actor-level `SessionSignal` contract.
4. Measure actor-level PR-AUC, calibration, time-to-detection, intervention volume, and recidivism.
5. Add independent model-based graders and human/grader agreement studies.
6. Add bounded paraphrase, pacing, and cross-session perturbations.
7. Store OpenTelemetry-compatible traces for evaluation regression analysis.

## Safety boundary

- All checked-in scenarios, secrets, identities, tools, and actor trajectories are synthetic.
- The Claude adapter records tool requests but does not execute tools.
- No malware execution, credential theft, destructive automation, persistence, or live-target interaction is implemented.
- `harmful_completion` is an evaluation label, not an operational action.
- API keys must remain in environment variables and must never be committed.
- Do not publish private provider transcripts or proprietary data as benchmark fixtures.

See [`SECURITY.md`](SECURITY.md).

## License

MIT License.
