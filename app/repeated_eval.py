from __future__ import annotations

from collections import Counter, defaultdict
from math import sqrt
from statistics import mean, stdev
from typing import Callable

from .engine import evaluate_with_adapter
from .models import Scorecard


def _ci95(values: list[float]) -> tuple[float, float]:
    if not values:
        return (0.0, 0.0)
    center = mean(values)
    if len(values) == 1:
        return (round(center, 4), round(center, 4))
    margin = 1.96 * stdev(values) / sqrt(len(values))
    return (round(center - margin, 4), round(center + margin, 4))


def summarize_trials(scorecards: list[Scorecard]) -> dict[str, object]:
    if not scorecards:
        raise ValueError("at least one scorecard is required")

    overall_scores = [scorecard.overall_score for scorecard in scorecards]
    category_values: dict[str, list[float]] = defaultdict(list)
    scenario_scores: dict[str, list[float]] = defaultdict(list)
    failure_counts: Counter[str] = Counter()
    latencies: list[float] = []
    total_input_tokens = 0
    total_output_tokens = 0

    for scorecard in scorecards:
        for category, score in scorecard.category_scores.items():
            category_values[category].append(score)
        for scenario in scorecard.scenario_results:
            scenario_scores[scenario.scenario_id].append(scenario.score)
            for check in scenario.checks:
                if not check.passed:
                    failure_counts[f"{scenario.scenario_id}:{check.name}"] += 1
            trace = scenario.trace
            if trace.latency_ms is not None:
                latencies.append(trace.latency_ms)
            total_input_tokens += trace.input_tokens or 0
            total_output_tokens += trace.output_tokens or 0

    low, high = _ci95(overall_scores)
    return {
        "model": scorecards[0].model,
        "trials": len(scorecards),
        "overall": {
            "mean": round(mean(overall_scores), 4),
            "stdev": round(stdev(overall_scores), 4) if len(overall_scores) > 1 else 0.0,
            "ci95_low": low,
            "ci95_high": high,
            "min": min(overall_scores),
            "max": max(overall_scores),
        },
        "category_means": {
            category: round(mean(values), 4)
            for category, values in sorted(category_values.items())
        },
        "scenario_mean_scores": {
            scenario_id: round(mean(values), 4)
            for scenario_id, values in sorted(scenario_scores.items())
        },
        "failure_frequency": dict(sorted(failure_counts.items())),
        "usage": {
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "mean_latency_ms": round(mean(latencies), 2) if latencies else None,
        },
        "trial_overall_scores": overall_scores,
        "interpretation": (
            "Repeated-trial statistics describe this benchmark run only. "
            "They are not production safety or misuse-detection claims."
        ),
    }


def run_repeated_evaluation(
    adapter_factory: Callable[[], object],
    *,
    trials: int = 3,
) -> dict[str, object]:
    if trials < 1:
        raise ValueError("trials must be at least 1")

    scorecards: list[Scorecard] = []
    for _ in range(trials):
        adapter = adapter_factory()
        label = getattr(adapter, "name", "custom-adapter")
        scorecards.append(evaluate_with_adapter(adapter, model_label=label))

    return summarize_trials(scorecards)
