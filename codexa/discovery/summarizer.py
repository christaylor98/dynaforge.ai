"""Semantic summarisation orchestrator.

Routes files to the appropriate language model (as determined by the routing
table) and captures structured JSON summaries suitable for manifest merging.
The module is model-provider agnostic; callers supply a mapping of model IDs
to callables that implement their preferred API surface.
"""

from __future__ import annotations

import json
import os
import textwrap
import time
from dataclasses import dataclass, asdict
from hashlib import sha1
import logging
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional

from .model_router import RoutingDecision, load_routing_table
from .prompts import PromptRegistry, render_prompt
from .usage import log_usage


CACHE_DIR = Path(".codexa/discovery/cache/ai")
DEFAULT_OUTPUT_PATHS: Dict[str, Path] = {
    "semantic": Path(".codexa/discovery/manifest_semantic.json"),
    "interface": Path(".codexa/discovery/manifest_surface.json"),
    "architecture": Path(".codexa/discovery/manifest_system.json"),
}


ModelInvoker = Callable[[str, str], str]
logger = logging.getLogger("codexa.discovery.summarizer")


@dataclass
class SummaryResult:
    file: str
    model: str
    tier: str
    summary: Dict[str, Any]
    confidence: float
    cached: bool
    latency_s: float

    def to_manifest_entry(self) -> Dict[str, Any]:
        entry = dict(self.summary)
        entry.update(
            {
                "file": self.file,
                "model": self.model,
                "tier": self.tier,
                "confidence": self.confidence,
                "latency_s": self.latency_s,
                "cached": self.cached,
            }
        )
        return entry


class Summarizer:
    """Execute semantic summaries for routed files."""

    def __init__(
        self,
        *,
        cache_dir: Path = CACHE_DIR,
        model_invokers: Optional[Mapping[str, ModelInvoker]] = None,
        focus_text: str | None = None,
        prompt_profile: str = "default",
        prompt_registry: Optional[PromptRegistry] = None,
        stage: str = "semantic",
        manifest_path: Optional[Path] = None,
        project_root: Optional[Path] = None,
        semantic_digest_map: Optional[Mapping[str, str]] = None,
    ) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        default_path = DEFAULT_OUTPUT_PATHS.get(stage, DEFAULT_OUTPUT_PATHS["semantic"])
        self.manifest_path = manifest_path or default_path
        self.model_invokers = dict(model_invokers or {})
        self.focus_text = focus_text or ""
        self.prompt_profile = prompt_profile
        self.prompt_registry = prompt_registry or PromptRegistry.load()
        self.stage = stage
        self.project_root = (project_root or Path.cwd()).expanduser().resolve()
        self.semantic_digest_map = dict(semantic_digest_map or {})

    def summarise(self, routing: Iterable[RoutingDecision]) -> List[SummaryResult]:
        queue = list(routing)
        if not queue:
            logger.info("No routing decisions supplied for stage=%s", self.stage)
            self._write_manifest([])
            return []
        logger.info(
            "Summarising %d modules (stage=%s, manifest=%s)",
            len(queue),
            self.stage,
            self.manifest_path,
        )
        results: List[SummaryResult] = []
        for decision in queue:
            logger.debug(
                "Summarising file=%s model=%s tier=%s stage=%s",
                decision.file,
                decision.model,
                decision.tier,
                self.stage,
            )
            result = self._run_single(decision)
            results.append(result)
        self._write_manifest(results)
        return results

    def _run_single(self, decision: RoutingDecision) -> SummaryResult:
        cache_file = self.cache_dir / f"{self._cache_key(decision)}.json"
        if cache_file.exists():
            payload = json.loads(cache_file.read_text(encoding="utf-8"))
            confidence = float(payload.get("confidence", decision.prev_confidence))
            logger.debug("Cache hit for %s (%s)", decision.file, cache_file)
            log_usage(
                self.project_root,
                model=decision.model,
                stage=self.stage,
                prompt_chars=0,
                response_chars=len(json.dumps(payload)),
                cached=True,
            )
            return SummaryResult(
                file=decision.file,
                model=decision.model,
                tier=decision.tier,
                summary=payload,
                confidence=confidence,
                cached=True,
                latency_s=0.0,
            )

        if self.stage == "semantic" and decision.file in self.semantic_digest_map:
            content = self.semantic_digest_map[decision.file]
            content_kind = "digest"
            logger.debug("Using digest content for %s", decision.file)
        else:
            content = self._read_source(decision.file)
            content_kind = "code"
        prompt = build_semantic_prompt(
            decision.file,
            content,
            focus_text=self.focus_text,
            profile=self.prompt_profile,
            registry=self.prompt_registry,
            stage=self.stage,
            content_kind=content_kind,
        )
        start = time.perf_counter()
        raw = self._invoke_model(decision.model, prompt)
        latency = time.perf_counter() - start

        summary = coerce_stage_output(
            raw,
            fallback_file=decision.file,
            stage=self.stage,
        )
        confidence = float(summary.get("confidence", decision.prev_confidence))
        cache_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")

        log_usage(
            self.project_root,
            model=decision.model,
            stage=self.stage,
            prompt_chars=len(prompt),
            response_chars=len(raw),
            cached=False,
        )
        return SummaryResult(
            file=decision.file,
            model=decision.model,
            tier=decision.tier,
            summary=summary,
            confidence=confidence,
            cached=False,
            latency_s=round(latency, 3),
        )

    def _invoke_model(self, model: str, prompt: str) -> str:
        invoker = self.model_invokers.get(model)
        if invoker is None:
            raise RuntimeError(
                f"No model invoker registered for '{model}'. Configure the "
                "Summarizer with a model_invokers mapping before running discovery."
            )
        return invoker(model, prompt)

    def _cache_key(self, decision: RoutingDecision) -> str:
        safe_stage = self.stage.replace(":", "_").replace("/", "_")
        safe_file = decision.file.replace("/", "_")
        safe_model = (
            decision.model.replace(":", "_").replace("/", "_")
            if decision.model
            else "model"
        )
        key = f"{safe_stage}__{safe_file}__{safe_model}"
        if self.stage == "semantic" and decision.file in self.semantic_digest_map:
            digest = self.semantic_digest_map[decision.file]
            key += "__" + sha1(digest.encode("utf-8")).hexdigest()[:10]
        return key

    @staticmethod
    def _read_source(path: str) -> str:
        file_path = Path(path)
        if not file_path.is_file():
            file_path = Path.cwd() / path
        try:
            return file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return ""

    def _write_manifest(self, results: Iterable[SummaryResult]) -> None:
        entries = [result.to_manifest_entry() for result in results]
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self.manifest_path.write_text(json.dumps(entries, indent=2), encoding="utf-8")
        logger.info(
            "Wrote %d %s summaries to %s",
            len(entries),
            self.stage,
            self.manifest_path,
        )


def build_semantic_prompt(
    path: str,
    content: str,
    *,
    focus_text: str = "",
    profile: str = "default",
    registry: Optional[PromptRegistry] = None,
    stage: str = "semantic",
    module_summaries: str = "",
    content_kind: str = "code",
) -> str:
    if content_kind == "digest":
        snippet = content
    else:
        snippet = content[:4000]
        if len(content) > len(snippet):
            snippet += "\n\n# [truncated]"
    focus_block = f"Focus directives:\n{focus_text}\n\n" if focus_text else ""
    registry = registry or PromptRegistry.load()
    template = registry.get(profile, stage)
    return render_prompt(
        template,
        path=path,
        snippet=snippet,
        focus_block=focus_block,
        module_summaries=module_summaries,
    )


def coerce_stage_output(raw: str, *, fallback_file: str, stage: str) -> Dict[str, Any]:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        payload = {}

    if stage == "interface":
        return _normalise_interface_payload(payload, fallback_file)
    if stage == "architecture":
        return _normalise_architecture_payload(payload, fallback_file)
    return _normalise_semantic_payload(payload, fallback_file)


def run_semantic_stage(
    *,
    routing_path: Path = Path(".codexa/discovery/routing_table.json"),
    model_invokers: Optional[Mapping[str, ModelInvoker]] = None,
) -> List[SummaryResult]:
    routing = load_routing_table(routing_path)
    summariser = Summarizer(model_invokers=model_invokers, stage="semantic")
    return summariser.summarise(routing)


def build_digest_batch_prompt(entries: List[tuple[str, str]], focus_text: str = "") -> str:
    lines = []
    for idx, (file_path, digest) in enumerate(entries, start=1):
        lines.append(f"{idx}. file: {file_path}\n   digest: {digest}")
    focus_block = f"Focus directives: {focus_text}\n\n" if focus_text else ""
    return (
        "You are CodeDiscover performing semantic discovery. "
        "For each file digest below, return a JSON array where each entry matches the schema: "
        "{\"file\": str, \"summary\": str, \"entities\": [], \"responsibilities\": [], \"dependencies\": [], \"confidence\": 0.0-1.0}.\n\n"
        f"{focus_block}Digests:\n" + "\n".join(lines)
    )


def _normalise_semantic_payload(payload: Dict[str, Any], fallback: str) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        payload = {}
    summary = str(payload.get("summary") or "").strip()
    if not summary:
        summary = f"Summary unavailable for {fallback}"
    result = {
        "summary": summary,
        "entities": list(payload.get("entities") or []),
        "responsibilities": list(payload.get("responsibilities") or []),
        "dependencies": list(payload.get("dependencies") or []),
        "confidence": float(payload.get("confidence") or 0.5),
    }
    return result


def _normalise_interface_payload(payload: Dict[str, Any], fallback: str) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        payload = {}
    return {
        "summary": str(payload.get("summary") or f"Interface summary unavailable for {fallback}"),
        "cli_commands": list(payload.get("cli_commands") or []),
        "api_endpoints": list(payload.get("api_endpoints") or []),
        "config_files": list(payload.get("config_files") or []),
        "test_cases": list(payload.get("test_cases") or []),
        "doc_examples": list(payload.get("doc_examples") or []),
        "confidence": float(payload.get("confidence") or 0.5),
    }


def _normalise_architecture_payload(payload: Dict[str, Any], fallback: str) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        payload = {}
    return {
        "subsystem": str(payload.get("subsystem") or fallback),
        "purpose": str(payload.get("purpose") or ""),
        "modules": list(payload.get("modules") or []),
        "depends_on": list(payload.get("depends_on") or []),
        "interacts_with": list(payload.get("interacts_with") or []),
        "risks": list(payload.get("risks") or []),
        "entry_points": list(payload.get("entry_points") or []),
        "confidence": float(payload.get("confidence") or 0.5),
    }


__all__ = [
    "SummaryResult",
    "Summarizer",
    "build_semantic_prompt",
    "build_digest_batch_prompt",
    "coerce_stage_output",
    "run_semantic_stage",
]
