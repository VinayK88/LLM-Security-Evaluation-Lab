from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from .actor_safeguards import run_actor_benchmark
from .dataset import load_scenarios
from .engine import evaluate
from .models import EvalRequest, Scorecard


app = FastAPI(
    title="LLM Security Evaluation Lab",
    version="0.2.0",
    description=(
        "Defensive evaluation framework for LLM application security, "
        "longitudinal actor-level misuse detection, and safeguards intervention science."
    ),
)

_last_scorecard: Scorecard | None = None


@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>LLM Security Evaluation Lab</title>
  <style>
    body { font-family: ui-sans-serif, system-ui; max-width: 1000px; margin: 40px auto; padding: 0 20px; }
    button { padding:10px 16px; margin-right:8px; cursor:pointer; }
    pre { background:#111; color:#eee; padding:16px; border-radius:8px; overflow:auto; }
    .score { font-size:48px; font-weight:700; margin:12px 0; }
  </style>
</head>
<body>
  <h1>LLM Security Evaluation Lab</h1>
  <p>Prompt injection · leakage · tool safety · actor-level misuse · jailbreak severity · intervention evaluation</p>

  <button onclick="run('mock-safe')">Evaluate safe mock</button>
  <button onclick="run('mock-unsafe')">Evaluate unsafe mock</button>
  <button onclick="runActors()">Run actor safeguards benchmark</button>

  <div id="score" class="score">—</div>
  <pre id="result">Run an evaluation to generate a scorecard.</pre>

<script>
async function run(model) {
  const r = await fetch('/evaluate', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({model})
  });
  const data = await r.json();
  document.getElementById('score').textContent = data.overall_score + '/100';
  document.getElementById('result').textContent = JSON.stringify(data, null, 2);
}
async function runActors() {
  const r = await fetch('/actor-safeguards');
  const data = await r.json();
  const m = data.metrics;
  document.getElementById('score').textContent = m.pre_harm_detection ? 'PRE-HARM' : 'MISSED';
  document.getElementById('result').textContent = JSON.stringify(data, null, 2);
}
</script>
</body>
</html>
"""


@app.post("/evaluate")
def run_evaluation(req: EvalRequest):
    global _last_scorecard
    try:
        _last_scorecard = evaluate(req.model)
        return _last_scorecard.model_dump()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/actor-safeguards")
def actor_safeguards():
    return run_actor_benchmark()


@app.get("/scenarios")
def scenarios():
    return [s.model_dump() for s in load_scenarios()]


@app.get("/scorecard")
def scorecard():
    if _last_scorecard is None:
        raise HTTPException(status_code=404, detail="no evaluation has been run")
    return _last_scorecard.model_dump()


@app.get("/failures")
def failures():
    if _last_scorecard is None:
        raise HTTPException(status_code=404, detail="no evaluation has been run")

    result = []
    for scenario in _last_scorecard.scenario_results:
        for check in scenario.checks:
            if not check.passed:
                result.append({
                    "scenario_id": scenario.scenario_id,
                    "scenario_category": scenario.category,
                    "check": check.name,
                    "category": check.category,
                    "reason": check.reason,
                })
    return result
