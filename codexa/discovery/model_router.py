"""Model routing for the discovery pipeline.

The router evaluates module complexity metrics and historical confidence
values to select the most appropriate model tier for downstream analysis.
The implementation is intentionally deterministic so that repeated runs
with identical inputs resolve to the same routing decisions.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
import json
import logging
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional

from .ast_parser import ModuleIR


DEFAULT_ROUTING_PATH = Path(".codexa/discovery/routing_table.json")
logger = logging.getLogger("codexa.discovery.router")


@dataclass
class RoutingDecision:
    file: str
    tier: str
    model: str
    complexity: float
    prev_confidence: float
    rationale: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


class ModelRouter:
    """Score modules and assign the preferred model tier."""

    def __init__(
        self,
        *,
        thresholds: Mapping[str, float] | None = None,
        model_map: Mapping[str, str] | None = None,
        policy_mode: str = "balanced",
    ) -> None:
        self.thresholds = {
            "tier1": 0.3,
            "tier2": 0.7,
        }
        if thresholds:
            self.thresholds.update(thresholds)
        self.model_map = {
            "tier1": "local://python-mini",
            "tier2": "cloud://gpt-standard",
            "tier3": "cloud://gpt-advanced",
        }
        if model_map:
            self.model_map.update(model_map)
        self.policy_mode = policy_mode

    def route(
        self,
        modules: Iterable[ModuleIR],
        previous_manifest: Optional[Mapping[str, object]] = None,
        priority_paths: Optional[Iterable[str]] = None,
    ) -> List[RoutingDecision]:
        prev_conf = self._index_confidence(previous_manifest)
        priority = {path for path in (priority_paths or [])}
        decisions: List[RoutingDecision] = []
        for module in modules:
            confidence = prev_conf.get(module.file, 0.8)
            score = self._complexity_score(module, confidence)
            if module.file in priority:
                score = min(score + 0.2, 1.0)
            tier, rationale = self._choose_tier(score)
            decisions.append(
                RoutingDecision(
                    file=module.file,
                    tier=tier,
                    model=self.model_map[tier],
                    complexity=round(score, 3),
                    prev_confidence=round(confidence, 3),
                    rationale=rationale,
                )
            )
        if decisions:
            tier_counts: Dict[str, int] = {}
            for decision in decisions:
                tier_counts[decision.tier] = tier_counts.get(decision.tier, 0) + 1
            logger.info(
                "Route completed for %d modules (policy=%s)", len(decisions), self.policy_mode
            )
            logger.debug("Tier breakdown: %s", tier_counts)
        else:
            logger.info("Route completed with no modules selected.")
        return decisions

    def _index_confidence(
        self, manifest: Optional[Mapping[str, object]]
    ) -> Dict[str, float]:
        if not manifest:
            return {}
        results: Dict[str, float] = {}
        for entry in manifest.get("modules", []):
            if not isinstance(entry, Mapping):
                continue
            path = entry.get("file")
            confidence = entry.get("confidence")
            if isinstance(path, str) and isinstance(confidence, (int, float)):
                results[path] = float(confidence)
        return results

    def _complexity_score(self, module: ModuleIR, prev_conf: float) -> float:
        metrics = module.complexity
        loc_score = min(metrics.loc / 1200.0, 1.0)
        block_score = min(metrics.avg_block_size / 20.0, 1.0)
        import_score = min(metrics.import_count / 15.0, 1.0)
        entity_score = min(
            (metrics.function_count + metrics.class_count) / 40.0, 1.0
        )
        doc_penalty = 1.0 - metrics.docstring_density
        history_penalty = 1.0 - max(min(prev_conf, 1.0), 0.0)
        raw = (
            0.3 * loc_score
            + 0.2 * block_score
            + 0.15 * import_score
            + 0.15 * entity_score
            + 0.1 * doc_penalty
            + 0.1 * history_penalty
        )
        return max(0.0, min(raw, 1.0))

    def _choose_tier(self, score: float) -> tuple[str, str]:
        tier1 = self.thresholds.get("tier1", 0.3)
        tier2 = self.thresholds.get("tier2", 0.7)
        if self.policy_mode == "conservative":
            tier1 *= 0.8
            tier2 *= 0.8
        elif self.policy_mode == "aggressive":
            tier1 *= 1.1
            tier2 *= 1.1

        if score < tier1:
            return "tier1", "Low structural complexity"
        if score < tier2:
            return "tier2", "Moderate complexity"
        return "tier3", "High complexity"


def save_routing_table(
    decisions: Iterable[RoutingDecision],
    path: Path = DEFAULT_ROUTING_PATH,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    table = [decision.to_dict() for decision in decisions]
    path.write_text(json.dumps(table, indent=2), encoding="utf-8")


def load_routing_table(path: Path = DEFAULT_ROUTING_PATH) -> List[RoutingDecision]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    results: List[RoutingDecision] = []
    for entry in payload:
        if not isinstance(entry, Mapping):
            continue
        try:
            results.append(
                RoutingDecision(
                    file=str(entry.get("file")),
                    tier=str(entry.get("tier")),
                    model=str(entry.get("model")),
                    complexity=float(entry.get("complexity", 0.0)),
                    prev_confidence=float(entry.get("prev_confidence", 0.0)),
                    rationale=str(entry.get("rationale", "")),
                )
            )
        except (TypeError, ValueError):
            continue
    return results


__all__ = [
    "RoutingDecision",
    "ModelRouter",
    "save_routing_table",
    "load_routing_table",
]
