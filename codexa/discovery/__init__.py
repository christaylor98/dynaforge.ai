"""
Discovery tooling for Codexa.

The subpackage exposes helpers for generating discovery artifacts,
computing blast radii, and orchestrating the `codexa discover` command.
"""

from .blast_radius import BlastRadiusPlanner, BlastRadiusResult, DiscoveryRunRecord
from .analyzers import build_repository_insights
from .ast_parser import ModuleIR, parse_repository
from .model_router import ModelRouter, RoutingDecision
from .summarizer import Summarizer
from .manifest_builder import build_manifest
from .reporter import build_report
from .synthesizer import SubsystemSynthesizer, synthesise_subsystems
from .focus import (
    FocusContext,
    DEFAULT_FOCUS_NOTES,
    FOCUS_CONTEXT_PATH,
    load_focus_context,
    load_user_focus,
)
from .pipeline import DiscoveryPipeline, DiscoveryContext, build_stub_invokers
from .models import build_default_registry, ModelRegistry, AdapterConfig
from .prompts import PromptRegistry, PromptTemplate, render_prompt
from .compressor import compress_directory, save_symbol_digests, digest_to_prompt

__all__ = [
    "BlastRadiusPlanner",
    "BlastRadiusResult",
    "DiscoveryRunRecord",
    "build_repository_insights",
    "ModuleIR",
    "parse_repository",
    "ModelRouter",
    "RoutingDecision",
    "Summarizer",
    "build_manifest",
    "build_report",
    "SubsystemSynthesizer",
    "synthesise_subsystems",
    "DiscoveryPipeline",
    "DiscoveryContext",
    "build_stub_invokers",
    "build_default_registry",
    "ModelRegistry",
    "AdapterConfig",
    "FocusContext",
    "DEFAULT_FOCUS_NOTES",
    "FOCUS_CONTEXT_PATH",
    "load_focus_context",
    "load_user_focus",
    "PromptRegistry",
    "PromptTemplate",
    "render_prompt",
    "compress_directory",
    "save_symbol_digests",
    "digest_to_prompt",
]
