from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.engine import evaluate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        default="mock-safe",
        help="mock-safe, mock-unsafe, or anthropic:<model-name>",
    )
    parser.add_argument("--min-score", type=float, default=0.0)
    args = parser.parse_args()

    try:
        scorecard = evaluate(args.model)
    except (ValueError, RuntimeError) as exc:
        parser.error(str(exc))

    print(json.dumps(scorecard.model_dump(), indent=2))

    if scorecard.overall_score < args.min_score:
        print(
            f"\nFAILED quality gate: {scorecard.overall_score} < {args.min_score}",
            file=sys.stderr,
        )
        raise SystemExit(2)


if __name__ == "__main__":
    main()
