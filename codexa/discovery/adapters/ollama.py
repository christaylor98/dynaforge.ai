"""Ollama local model adapter."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Mapping

try:  # pragma: no cover - optional dependency
    import requests
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "Ollama adapter requires the `requests` package. Install it with `pip install requests` "
        "before selecting --model-adapter ollama."
    ) from exc


DEFAULT_MODEL = os.environ.get("CODEXA_OLLAMA_MODEL", "qwen2.5-coder:latest")
DEFAULT_HOST = os.environ.get("CODEXA_OLLAMA_HOST", "http://localhost:11434")


def build_ollama_models(project_root: Path) -> Mapping[str, callable]:
    adapter = _OllamaAdapter(host=DEFAULT_HOST, default_model=DEFAULT_MODEL)
    return {
        f"ollama://{DEFAULT_MODEL}": adapter.invoke,
    }


class _OllamaAdapter:
    def __init__(self, *, host: str, default_model: str) -> None:
        self.host = host.rstrip("/")
        self.default_model = default_model
        self.session = requests.Session()

    def invoke(self, model: str, prompt: str) -> str:
        model_name = model.replace("ollama://", "") if model else self.default_model
        url = f"{self.host}/api/generate"
        body = {
            "model": model_name,
            "prompt": (
                "You are Codex Discovery. Respond ONLY with valid JSON matching the schema "
                "requested in the prompt. Do not include prose.\n\n" + prompt
            ),
            "stream": False,
        }

        try:
            response = self.session.post(url, json=body, timeout=1800)
        except requests.RequestException as exc:  # pragma: no cover
            raise RuntimeError(
                f"Failed to contact Ollama at {self.host}. Ensure the server is running."
            ) from exc

        if response.status_code >= 400:
            raise RuntimeError(
                f"Ollama returned status {response.status_code}: {response.text[:200]}"
            )

        payload = response.json()
        text = (payload.get("response") or "").strip()
        if text.startswith("```") and text.endswith("```"):
            lines = text.splitlines()
            if len(lines) >= 2:
                text = "\n".join(lines[1:-1]).strip()
        if not text:
            raise RuntimeError("Ollama returned an empty response.")

        try:
            json.loads(text)
        except json.JSONDecodeError as exc:
            preview = text[:500]
            raise RuntimeError(
                "Ollama response was not valid JSON. Preview:\n" + preview
            ) from exc
        return text


__all__ = ["build_ollama_models"]
