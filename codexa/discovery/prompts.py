"""Prompt registry for discovery pipeline stages."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Optional

import yaml


DEFAULT_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "default_prompts.yaml"


@dataclass
class PromptTemplate:
    system: str
    user: str


class PromptRegistry:
    """Load and retrieve prompt templates by profile and stage."""

    def __init__(self, prompts: Mapping[str, Mapping[str, PromptTemplate]]) -> None:
        self._prompts = prompts

    @classmethod
    def load(
        cls,
        *,
        path: Path = DEFAULT_PROMPT_PATH,
    ) -> "PromptRegistry":
        if not path.exists():
            raise FileNotFoundError(f"Prompt file not found: {path}")
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        raw_profiles = payload.get("profiles") or {}
        prompts: dict[str, dict[str, PromptTemplate]] = {}
        for profile, stages in raw_profiles.items():
            profile_prompts: dict[str, PromptTemplate] = {}
            for stage, template in (stages or {}).items():
                system = str(template.get("system") or "")
                user = str(template.get("user") or "")
                profile_prompts[stage] = PromptTemplate(system=system, user=user)
            prompts[profile] = profile_prompts
        return cls(prompts)

    def get(self, profile: str, stage: str, default_profile: str = "default") -> PromptTemplate:
        if profile in self._prompts and stage in self._prompts[profile]:
            return self._prompts[profile][stage]
        if default_profile in self._prompts and stage in self._prompts[default_profile]:
            return self._prompts[default_profile][stage]
        raise KeyError(f"Prompt template not found for profile '{profile}', stage '{stage}'")


def render_prompt(template: PromptTemplate, **kwargs: str) -> str:
    system = template.system.format(**kwargs)
    user = template.user.format(**kwargs)
    return f"SYSTEM:\n{system}\n\nUSER:\n{user}"


__all__ = ["PromptRegistry", "PromptTemplate", "render_prompt", "DEFAULT_PROMPT_PATH"]
