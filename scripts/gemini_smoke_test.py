#!/usr/bin/env python3
"""Quick smoke test for the Gemini adapter."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

try:  # optional convenience, ignore if missing
    from dotenv import load_dotenv  # type: ignore
except ImportError:  # pragma: no cover
    load_dotenv = None


try:
    from codexa.discovery.adapters.gemini import build_gemini_models, DEFAULT_MODEL
except ImportError as exc:  # pragma: no cover - optional dependency
    print(
        "Gemini adapter dependencies missing. Install with `pip install google-genai`.",
        file=sys.stderr,
    )
    raise SystemExit(1) from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model",
        default=os.environ.get("CODEXA_GEMINI_MODEL", DEFAULT_MODEL),
        help="Gemini model id to call (defaults to CODEXA_GEMINI_MODEL or gemini-1.5-flash-latest)",
    )
    default_prompt = (
        "You are Codex Discovery. Respond ONLY with JSON matching this schema: "
        "{\"summary\": str, \"entities\": [], \"responsibilities\": [], "
        "\"dependencies\": [], \"confidence\": float}."
    )
    parser.add_argument(
        "--prompt",
        default=default_prompt,
        help="Prompt body to send. Should request JSON output.",
    )
    args = parser.parse_args()

    if load_dotenv:
        load_dotenv()  # load environment from .env automatically

    api_key = os.getenv("GOOGLE_GENAI_API_KEY")
    if not api_key:
        print("GOOGLE_GENAI_API_KEY is not set.", file=sys.stderr)
        return 1

    models = build_gemini_models(Path.cwd())
    invoker = models.get(f"gemini://{args.model}") or next(iter(models.values()))

    response = invoker(f"gemini://{args.model}", args.prompt)
    try:
        parsed = json.loads(response)
    except json.JSONDecodeError:
        parsed = {"raw": response}

    print("Response:")
    print(json.dumps(parsed, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
