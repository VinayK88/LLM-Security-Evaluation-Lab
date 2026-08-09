from __future__ import annotations

import argparse
import json
import sys

from app.engine import evaluate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="mock-safe", choices=["mock-safe", "mock-unsafe"])
    parser.add_argument("--min-score", type=float, default=0.0)
    args = parser.parse_args()

    scorecard = evaluate(args.model)
    print(json.dumps(scorecard.model_dump(), indent=2))

    if scorecard.overall_score < args.min_score:
        print(
            f"\nFAILED quality gate: {scorecard.overall_score} < {args.min_score}",
            file=sys.stderr,
        )
        raise SystemExit(2)


if __name__ == "__main__":
    main()
