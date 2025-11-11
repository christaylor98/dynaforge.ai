"""Gemini Generative AI model adapter."""

from __future__ import annotations

import json
import os
import time
from collections import deque
from pathlib import Path
from typing import Mapping


try:  # pragma: no cover - optional dependency
    from google import genai
    from google.genai.errors import ClientError
    from tenacity import retry, stop_after_attempt, wait_random_exponential
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "Gemini adapter requires the `google-genai` package. Install it with "
        "`pip install google-genai` before selecting --model-adapter gemini."
    ) from exc


DEFAULT_MODEL = os.environ.get("CODEXA_GEMINI_MODEL", "gemini-1.5-flash-latest")
MAX_ATTEMPTS = int(os.environ.get("CODEXA_GEMINI_MAX_ATTEMPTS", "3"))
MAX_RPM = int(os.environ.get("CODEXA_GEMINI_MAX_RPM", "28"))


def build_gemini_models(project_root: Path) -> Mapping[str, callable]:
    api_key = os.getenv("GOOGLE_GENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GOOGLE_GENAI_API_KEY is not set. Export your Gemini API key before running discovery."
        )

    client = genai.Client(api_key=api_key)
    adapter = _GeminiAdapter(client=client, default_model=DEFAULT_MODEL)
    return {
        f"gemini://{DEFAULT_MODEL}": adapter.invoke,
    }


class _GeminiAdapter:
    def __init__(self, *, client: "genai.Client", default_model: str) -> None:
        self.client = client
        self.default_model = default_model

    @retry(stop=stop_after_attempt(MAX_ATTEMPTS), wait=wait_random_exponential(min=2, max=15))
    def invoke(self, model: str, prompt: str) -> str:
        model_id = model.replace("gemini://", "") if model else self.default_model
        contents = [
            {
                "role": "user",
                "parts": [
                    {
                        "text": (
                            "You are Codex Discovery. Respond ONLY with valid JSON matching the schema "
                            "requested in the prompt. Do not include prose.\n\n" + prompt
                        )
                    }
                ],
            }
        ]

        _RATE_LIMITER.acquire()
        try:
            response = self.client.models.generate_content(
                model=model_id,
                contents=contents,
                config={"response_mime_type": "application/json"},
            )
        except ClientError as exc:
            message = str(exc)
            if "JSON mode is not enabled" in message or "response_mime_type" in message:
                response = self.client.models.generate_content(
                    model=model_id,
                    contents=contents,
                )
            else:
                retry_delay = _extract_retry_delay(exc) or 5.0
                time.sleep(retry_delay)
                raise RuntimeError(f"Gemini API error (retry after {retry_delay}s): {exc}") from exc

        text = _extract_text(response)
        text = text.strip()
        if text.startswith("```") and text.endswith("```"):
            lines = text.splitlines()
            if len(lines) >= 2:
                text = "\n".join(lines[1:-1]).strip()
        if not text:
            raise RuntimeError("Gemini returned an empty response.")

        try:
            json.loads(text)
        except json.JSONDecodeError as exc:
            preview = text[:500]
            raise RuntimeError(
                "Gemini response was not valid JSON. Preview:\n" + preview
            ) from exc
        return text


def _extract_text(response: "genai.types.GenerateContentResponse") -> str:
    if not response or not getattr(response, "candidates", None):
        return ""
    parts = []
    for candidate in response.candidates:
        md = getattr(candidate, "content", None)
        if not md:
            continue
        for part in getattr(md, "parts", []):
            text = getattr(part, "text", "")
            if text:
                parts.append(text)
    return "".join(parts)


def _extract_retry_delay(exc: ClientError) -> float:
    details = getattr(exc, "details", []) or []
    for detail in details:
        if isinstance(detail, dict) and detail.get("@type", "").endswith("RetryInfo"):
            delay = detail.get("retryDelay") or detail.get("retry_delay")
            if isinstance(delay, str) and delay.endswith("s"):
                try:
                    return float(delay[:-1])
                except ValueError:
                    continue
    return 5.0


__all__ = ["build_gemini_models"]
class _RateLimiter:
    def __init__(self, max_per_minute: int) -> None:
        self.max_per_minute = max_per_minute
        self.timestamps = deque()

    def acquire(self) -> None:
        if self.max_per_minute <= 0:
            return
        now = time.time()
        window = 60.0
        timestamps = self.timestamps
        while timestamps and now - timestamps[0] > window:
            timestamps.popleft()
        if len(timestamps) >= self.max_per_minute:
            sleep_for = window - (now - timestamps[0]) + 0.25
            time.sleep(max(0.5, sleep_for))
            self.acquire()
            return
        timestamps.append(time.time())


_RATE_LIMITER = _RateLimiter(MAX_RPM)
