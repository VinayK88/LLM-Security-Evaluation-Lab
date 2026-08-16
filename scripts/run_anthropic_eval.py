from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.anthropic_adapter import AnthropicAdapter
from app.repeated_eval import run_repeated_evaluation


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run repeated LLM security evaluations against a real Claude model."
    )
    parser.add_argument(
        "--model",
        default=os.getenv("ANTHROPIC_MODEL"),
        help="Claude model identifier. May also be supplied via ANTHROPIC_MODEL.",
    )
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=700)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if not args.model:
        parser.error("--model or ANTHROPIC_MODEL is required")

    def factory() -> AnthropicAdapter:
        return AnthropicAdapter(
            model=args.model,
            max_tokens=args.max_tokens,
            temperature=args.temperature,
        )

    report = run_repeated_evaluation(factory, trials=args.trials)
    rendered = json.dumps(report, indent=2)
    print(rendered)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
