"""Codex MCP model adapter."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Mapping

try:
    from agents import Agent, Runner
    from agents.mcp import MCPServerStdio
except ImportError as exc:  # pragma: no cover - optional dependency
    raise ImportError(
        "Codex MCP adapter requires the `openai-agents` package. Install it with "
        "`pip install openai-agents` or include it in your environment."
    ) from exc

DEFAULT_CODEX_COMMAND = os.environ.get("CODEXA_CODEX_COMMAND", "npx")
DEFAULT_CODEX_ARGS = os.environ.get("CODEXA_CODEX_ARGS", "-y codex mcp").split()


def build_codex_mcp_models(project_root: Path) -> Mapping[str, callable]:
    adapter = _CodexMCPAdapter(project_root=project_root)
    return {
        "codex://gpt-5": adapter.invoke,
    }


class _CodexMCPAdapter:
    def __init__(self, *, project_root: Path) -> None:
        self.project_root = Path(project_root).expanduser().resolve()

    def invoke(self, model: str, prompt: str) -> str:
        return asyncio.run(self._run(model=model, prompt=prompt))

    async def _run(self, *, model: str, prompt: str) -> str:
        params = {
            "command": DEFAULT_CODEX_COMMAND,
            "args": DEFAULT_CODEX_ARGS,
            "cwd": str(self.project_root),
        }

        async with MCPServerStdio(
            name="Codex CLI",
            params=params,
            client_session_timeout_seconds=3600,
        ) as codex_mcp:
            agent = Agent(
                name="Codex Summarizer",
                instructions=(
                    "You are Codex summarising code. Respond with JSON only. "
                    "Do not add prose or explanations outside the JSON object provided."
                ),
                model=model or "gpt-5",
                mcp_servers=[codex_mcp],
            )

            result = await Runner.run(agent, prompt, max_turns=1)
            output = (result.final_output or "").strip()
            if not output:
                raise RuntimeError("Codex MCP returned an empty response.")
            return output

