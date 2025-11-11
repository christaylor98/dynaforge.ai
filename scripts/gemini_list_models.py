#!/usr/bin/env python3
"""List available Gemini models using google-genai."""

from __future__ import annotations

import os
import sys

try:  # pragma: no cover - optional dependency
    from google import genai
except ImportError:
    print(
        "google-genai is not installed. Run `pip install google-genai` in your environment.",
        file=sys.stderr,
    )
    sys.exit(1)


def main() -> int:
    api_key = os.getenv("GOOGLE_GENAI_API_KEY")
    if not api_key:
        print("GOOGLE_GENAI_API_KEY is not set.", file=sys.stderr)
        return 1

    client = genai.Client(api_key=api_key)
    models = client.models.list()

    print("Available Gemini models:")
    for model in models:
        name = getattr(model, "name", "<unknown>")
        supported = ", ".join(getattr(model, "supported_generation_methods", []) or [])
        print(f"- {name} (supports: {supported})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
