# Real Claude evaluation methodology

This repository supports controlled evaluation of real Claude API responses against the same synthetic security scenarios used by the deterministic baselines.

## Design goals

The real-model path is intentionally separate from the checked-in mock baselines:

- API credentials are read only from `ANTHROPIC_API_KEY`.
- The model identifier is supplied at runtime with `--model` or `ANTHROPIC_MODEL` so the repository does not silently claim results for a model that was never run.
- Synthetic tools are exposed as schemas but are **never executed**.
- Tool requests, approval checkpoints, response IDs, stop reasons, token usage, and latency are recorded in the response trace.
- Repeated trials are summarized with mean, standard deviation, and a simple 95% confidence interval.
- No real-model score is checked into the repository unless it was actually produced and the model/version/run settings are preserved with it.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-anthropic.txt
```

Set credentials in the environment rather than in source files:

```bash
export ANTHROPIC_API_KEY="..."
export ANTHROPIC_MODEL="<model-id-available-to-your-account>"
```

## One benchmark pass

```bash
python scripts/run_eval.py --model "anthropic:${ANTHROPIC_MODEL}"
```

## Repeated trials

```bash
python scripts/run_anthropic_eval.py \
  --model "$ANTHROPIC_MODEL" \
  --trials 10 \
  --temperature 0 \
  --output reports/local-claude-eval.json
```

`reports/local-claude-eval.json` should normally remain local unless you intentionally want to publish that exact run. Before publishing a real-model result, preserve:

- model identifier;
- trial count;
- temperature and max tokens;
- benchmark commit SHA;
- timestamp;
- category-level results;
- failure frequency;
- token usage and latency;
- any API/provider configuration that could affect behavior.

## What the adapter sends

For every scenario, the adapter sends the scenario's `system_policy` as the Claude system prompt and the synthetic `user_prompt` as the user message. When retrieved content exists, it is placed behind an explicit text boundary. The adapter does not add real secrets, production telemetry, or external resources.

Available scenario tools are converted into synthetic tool schemas. Claude may request a tool, but the evaluator only records the request. It does not execute the tool. For scenarios that require explicit human approval, an evaluator-only `request_human_approval` control-plane tool is also exposed; using it records an approval checkpoint without performing an action.

## Statistical interpretation

Repeated trials are useful because model behavior may vary even when prompts and settings are held constant. The report includes:

- overall score mean and standard deviation;
- approximate 95% confidence interval around the trial mean;
- category means;
- mean scenario scores;
- failure frequency by scenario/check;
- total input/output tokens;
- mean API latency when available.

These statistics describe the included synthetic benchmark only. They do not establish production jailbreak resistance, misuse-detection recall, or real-world safety.

## Actor-level safeguards

The longitudinal actor benchmark remains intentionally deterministic today. A future extension can convert real Claude interaction traces into `SessionSignal` objects and evaluate cross-session risk, time-to-detection, researcher friction, and intervention policy without changing the existing actor-level contract.

## Safety and privacy

Do not run proprietary conversations, customer data, malware payloads, credentials, or sensitive incident material through this benchmark. The included scenarios are synthetic and designed for defensive evaluation. Do not commit `ANTHROPIC_API_KEY`, raw private API transcripts, or provider account metadata.
