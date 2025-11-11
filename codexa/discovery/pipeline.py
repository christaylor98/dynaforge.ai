"""High-level orchestration for the adaptive discovery pipeline."""

from __future__ import annotations

from dataclasses import dataclass, asdict
import json
import logging
import time
from pathlib import Path
from typing import Callable, Dict, Iterable, Mapping, Optional, List

from .ast_parser import ModuleIR, parse_repository
from .model_router import ModelRouter, save_routing_table
from .summarizer import Summarizer, SummaryResult, build_digest_batch_prompt, coerce_stage_output
from .synthesizer import synthesise_subsystems
from .manifest_builder import build_manifest, load_manifest_json
from .reporter import build_report
from .focus import load_user_focus, derive_auto_focus, write_focus_context
from .prompts import PromptRegistry
from .models import build_default_registry
from .compressor import compress_directory, save_symbol_digests, digest_to_prompt
from .usage import log_usage
from hashlib import sha1


ManifestDict = Mapping[str, object]
ModelInvoker = Callable[[str, str], str]

logger = logging.getLogger("codexa.discovery.pipeline")


@dataclass
class DiscoveryContext:
    project_root: Path
    scope: Optional[list[str]] = None
    focus_notes: Optional[str] = None
    previous_manifest: Optional[ManifestDict] = None


class DiscoveryPipeline:
    """Run the staged discovery process end-to-end."""

    def __init__(
        self,
        *,
        project_root: Path,
        model_invokers: Mapping[str, ModelInvoker] | None = None,
        router_kwargs: Optional[Mapping[str, object]] = None,
        prompt_profile: str = "default",
        prompt_registry: Optional[PromptRegistry] = None,
        summarize_mode: str = "code",
        digest_batch_budget: Optional[int] = None,
        digest_batch_max: Optional[int] = None,
        log_to_stdout: bool = True,
    ) -> None:
        self.project_root = project_root.expanduser().resolve()
        if model_invokers is None:
            registry = build_default_registry()
            model_invokers = registry.default().models
        self.model_invokers = dict(model_invokers)
        self.router_kwargs = dict(router_kwargs or {})
        self.prompt_profile = prompt_profile
        self.prompt_registry = prompt_registry or PromptRegistry.load()
        self.summarize_mode = summarize_mode
        self.semantic_digest_map: Dict[str, str] = {}
        self.digest_batch_budget = digest_batch_budget
        self.digest_batch_max = digest_batch_max
        self.log_to_stdout = log_to_stdout

    def run(
        self,
        *,
        context: Optional[DiscoveryContext] = None,
        emit_report: bool = True,
    ) -> Path:
        context = context or DiscoveryContext(project_root=self.project_root)
        run_start = time.perf_counter()

        previous_manifest = context.previous_manifest or load_manifest_json(
            Path(".codexa/discovery/manifest.json")
        )
        user_focus = load_user_focus(context.focus_notes)
        auto_focus = derive_auto_focus(previous_manifest)
        focus_text = self._compose_focus_text(user_focus, auto_focus)

        self._log(
            "🚀 Discovery pipeline started",
        )
        logger.debug(
            "Discovery context resolved: root=%s scope=%s focus_notes=%s summarize_mode=%s profile=%s",
            self.project_root,
            context.scope or [],
            bool(context.focus_notes),
            self.summarize_mode,
            self.prompt_profile,
        )

        self._log("📂 Collecting modules…")
        parse_start = time.perf_counter()
        modules = list(self._parse_sources(context))
        parse_elapsed = time.perf_counter() - parse_start
        self._log(f"   → {len(modules)} modules detected in {parse_elapsed:.2f}s")
        if self.summarize_mode == "digest":
            file_dicts = [asdict(module) for module in modules]
            self._log("🗜️  Building symbol digests…")
            digests = compress_directory(file_dicts)
            save_symbol_digests(digests)
            self.semantic_digest_map = {d.file: digest_to_prompt(d) for d in digests}
            self._log(f"   → {len(self.semantic_digest_map)} digests cached")
            preview = next(iter(self.semantic_digest_map.items()), None)
            if preview:
                file_name, digest = preview
                logger.debug(
                    "Digest preview %s (%d chars)",
                    file_name,
                    len(digest),
                )
        else:
            self.semantic_digest_map = {}
        routing = self._route_modules(modules, previous_manifest, auto_focus)
        if (
            self.summarize_mode == "digest"
            and self.digest_batch_budget
            and self.digest_batch_budget > 0
        ):
            self._log("🧠 Summarising (batched)…")
            semantic_results = self._summarise_semantic_batches(routing, focus_text)
        else:
            self._log("🧠 Summarising…")
            semantic_results = self._summarise_modules(routing, focus_text, stage="semantic")
        self._log(f"   → {len(semantic_results)} semantic summaries ready")

        self._log("🔌 Mapping interfaces…")
        interface_results = self._summarise_modules(routing, focus_text, stage="interface")
        self._log(f"   → {len(interface_results)} interface entries")
        self._log("🧩 Synthesising subsystems…")
        synthesise_subsystems(
            prompt_registry=self.prompt_registry,
            prompt_profile=self.prompt_profile,
            model_invokers=self.model_invokers,
            focus_text=focus_text,
        )
        extra_stats = self._summaries_metrics(semantic_results)
        extra_stats["interface_entries"] = len(interface_results)
        extra_stats["model_policy"] = self.router_kwargs.get("policy_mode", "balanced")
        manifest = build_manifest(extra_stats=extra_stats)
        self._log(
            f"📦 Manifest updated — {len(manifest.modules)} modules, "
            f"{manifest.stats.get('interface_entries', 0)} interface entries",
        )
        manifest_payload = load_manifest_json(Path(".codexa/discovery/manifest.json"))
        new_auto_focus = derive_auto_focus(manifest_payload)
        write_focus_context(user_focus, new_auto_focus)
        if emit_report:
            self._log("📝 Writing report…")
            report_path = build_report()
            self._log(f"📄 Discovery report written to {report_path}")
            self._log(f"✅ Discovery pipeline finished in {time.perf_counter() - run_start:.2f}s")
            return report_path
        self._log(f"✅ Discovery pipeline finished in {time.perf_counter() - run_start:.2f}s (manifest only)")
        return Path(".codexa/discovery/manifest.json")

    def _parse_sources(self, context: DiscoveryContext):
        root = context.project_root
        if context.scope:
            for pattern in context.scope:
                path = (root / pattern).resolve()
                if path.is_dir():
                    yield from parse_repository(path)
                elif path.is_file():
                    module = self._parse_single(path)
                    if module:
                        yield module
            return
        yield from parse_repository(root)

    def _parse_single(self, path: Path) -> Optional[ModuleIR]:
        from .ast_parser import parse_file

        module = parse_file(path)
        if module:
            module.file = str(path.relative_to(self.project_root))
        return module

    def _route_modules(
        self,
        modules: list[ModuleIR],
        previous_manifest: Optional[ManifestDict],
        priority_paths: Iterable[str],
    ):
        router = ModelRouter(**self.router_kwargs)
        decisions = router.route(
            modules,
            previous_manifest,
            priority_paths=priority_paths,
        )
        save_routing_table(decisions)
        tiers: Dict[str, int] = {}
        for decision in decisions:
            tiers[decision.tier] = tiers.get(decision.tier, 0) + 1
        self._log(
            f"🧭 Routed {len(decisions)} modules "
            f"(tier1={tiers.get('tier1', 0)}, tier2={tiers.get('tier2', 0)}, tier3={tiers.get('tier3', 0)})"
        )
        return decisions

    def _summarise_modules(self, routing, focus_text: str, stage: str):
        summariser = Summarizer(
            model_invokers=self.model_invokers,
            focus_text=focus_text,
            prompt_profile=self.prompt_profile,
            prompt_registry=self.prompt_registry,
            stage=stage,
            project_root=self.project_root,
            semantic_digest_map=self.semantic_digest_map if stage == "semantic" else None,
        )
        return summariser.summarise(routing)

    def _summarise_semantic_batches(
        self,
        routing: List[RoutingDecision],
        focus_text: str,
    ) -> List[SummaryResult]:
        summariser = Summarizer(
            model_invokers=self.model_invokers,
            focus_text=focus_text,
            prompt_profile=self.prompt_profile,
            prompt_registry=self.prompt_registry,
            stage="semantic",
            project_root=self.project_root,
            semantic_digest_map=self.semantic_digest_map,
        )

        batches: List[List[RoutingDecision]] = []
        fallback: List[RoutingDecision] = []
        current: List[RoutingDecision] = []
        current_tokens = 0
        max_items = self.digest_batch_max or 20
        token_budget = self.digest_batch_budget or 2000

        for decision in routing:
            digest = self.semantic_digest_map.get(decision.file)
            if not digest:
                fallback.append(decision)
                continue
            est_tokens = max(1, len(digest) // 4)
            if (
                current
                and (len(current) >= max_items or current_tokens + est_tokens > token_budget)
            ):
                batches.append(current)
                current = []
                current_tokens = 0
            current.append(decision)
            current_tokens += est_tokens
        if current:
            batches.append(current)

        results: List[SummaryResult] = []

        if batches:
            self._log(
                f"   • {len(batches)} digest batches queued "
                f"(budget {token_budget} tokens, max {max_items} files)"
            )
        for batch in batches:
            batch_results = self._run_digest_batch(summariser, batch, focus_text)
            results.extend(batch_results)

        if fallback:
            self._log(f"   • {len(fallback)} files sent full-code")
            fallback_results = summariser.summarise(fallback)
            results.extend(fallback_results)

        summariser._write_manifest(results)
        return results

    def _run_digest_batch(
        self,
        summariser: Summarizer,
        batch: List[RoutingDecision],
        focus_text: str,
    ) -> List[SummaryResult]:
        digest_entries = []
        for decision in batch:
            digest = self.semantic_digest_map.get(decision.file)
            if not digest:
                continue
            digest_entries.append((decision, digest))

        if not digest_entries:
            return []

        key_material = "".join(f"{d.file}:{self.semantic_digest_map[d.file]}" for d, _ in digest_entries)
        batch_hash = sha1(key_material.encode("utf-8")).hexdigest()[:16]
        cache_file = summariser.cache_dir / f"semantic_batch__{batch_hash}.json"

        if cache_file.exists():
            payload = json.loads(cache_file.read_text(encoding="utf-8"))
            raw = json.dumps(payload)
            cached = True
        else:
            prompt = build_digest_batch_prompt(
                [(d.file, digest) for d, digest in digest_entries],
                focus_text=focus_text,
            )
            start = time.perf_counter()
            raw = summariser._invoke_model(batch[0].model, prompt)
            latency = time.perf_counter() - start
            payload = json.loads(raw)
            cache_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            cached = False
            log_usage(
                summariser.project_root,
                model=batch[0].model,
                stage="semantic_batch",
                prompt_chars=len(prompt),
                response_chars=len(raw),
                cached=False,
                extra={"batch_size": len(digest_entries)},
            )

        decision_map = {d.file: d for d, _ in digest_entries}
        results: List[SummaryResult] = []

        for item in payload:
            file_path = item.get("file")
            if file_path not in decision_map:
                continue
            decision = decision_map[file_path]
            summary = coerce_stage_output(
                json.dumps(item),
                fallback_file=file_path,
                stage="semantic",
            )
            results.append(
                SummaryResult(
                    file=file_path,
                    model=decision.model,
                    tier=decision.tier,
                    summary=summary,
                    confidence=summary.get("confidence", decision.prev_confidence),
                    cached=cached,
                    latency_s=0.0 if cached else latency,
                )
            )

        if cached:
            log_usage(
                summariser.project_root,
                model=batch[0].model,
                stage="semantic_batch",
                prompt_chars=0,
                response_chars=len(json.dumps(payload)),
                cached=True,
                extra={"batch_size": len(digest_entries)},
            )

        return results

    def _log(self, message: str, *, level: int = logging.INFO) -> None:
        logger.log(level, message)
        if self.log_to_stdout:
            print(message, flush=True)

    @staticmethod
    def _compose_focus_text(user_notes: str, auto_focus: Iterable[str]) -> str:
        sections = []
        if user_notes.strip():
            sections.append(f"User focus notes:\n{user_notes.strip()}")
        auto_list = [item for item in auto_focus if item]
        if auto_list:
            formatted = "\n".join(auto_list)
            sections.append(f"Priority modules from previous run:\n{formatted}")
        return "\n\n".join(sections)

    @staticmethod
    def _summaries_metrics(summaries) -> Dict[str, object]:
        total_latency = 0.0
        cached_hits = 0
        for item in summaries:
            total_latency += getattr(item, "latency_s", 0.0)
            if getattr(item, "cached", False):
                cached_hits += 1
        return {
            "latency_total_s": round(total_latency, 3),
            "cached_modules": cached_hits,
        }


def build_stub_invokers() -> Dict[str, ModelInvoker]:
    """Return fallback model invokers that emit deterministic JSON.

    These stubs allow the pipeline to run in environments where external model
    providers are unavailable.  They should be replaced by real adapters when
    integrating with production model endpoints.
    """

    def _stub(model: str, prompt: str) -> str:
        _ = prompt  # prompt ignored in stub
        payload = {
            "summary": f"Stub summary generated by {model}",
            "entities": [],
            "responsibilities": [],
            "dependencies": [],
            "confidence": 0.5,
        }
        return json.dumps(payload)

    return {
        "local://python-mini": _stub,
        "cloud://gpt-standard": _stub,
        "cloud://gpt-advanced": _stub,
    }


__all__ = ["DiscoveryPipeline", "DiscoveryContext", "build_stub_invokers"]
