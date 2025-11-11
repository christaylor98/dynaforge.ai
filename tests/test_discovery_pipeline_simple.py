import json
from pathlib import Path

import pytest

from codexa.discovery.model_router import RoutingDecision
from codexa.discovery.summarizer import Summarizer
from codexa.discovery.manifest_builder import build_manifest
from codexa.discovery.pipeline import DiscoveryPipeline, DiscoveryContext


def _stub_invoker(model: str, prompt: str) -> str:
    _ = (model, prompt)
    return json.dumps(
        {
            "summary": "Stub summary",
            "entities": ["Foo"],
            "responsibilities": ["demo"],
            "dependencies": ["bar"],
            "confidence": 0.9,
        }
    )


def _interface_stub(model: str, prompt: str) -> str:
    _ = (model, prompt)
    return json.dumps(
        {
            "summary": "Interface summary",
            "cli_commands": ["demo"],
            "api_endpoints": [],
            "config_files": [],
            "test_cases": [],
            "doc_examples": [],
            "confidence": 0.8,
        }
    )


def test_summarizer_writes_manifest(tmp_path: Path) -> None:
    source = tmp_path / "module.py"
    source.write_text("def demo():\n    return 1\n", encoding="utf-8")

    cache_dir = tmp_path / "cache"
    manifest_path = tmp_path / "semantic.json"

    summariser = Summarizer(
        cache_dir=cache_dir,
        manifest_path=manifest_path,
        model_invokers={"local://stub": _stub_invoker},
        focus_text="",
        prompt_profile="default",
        stage="semantic",
        project_root=tmp_path,
        semantic_digest_map={str(source): "DIGEST"},
    )

    decision = RoutingDecision(
        file=str(source),
        tier="tier1",
        model="local://stub",
        complexity=0.1,
        prev_confidence=0.5,
        rationale="test",
    )

    results = summariser.summarise([decision])

    assert len(results) == 1
    assert manifest_path.exists()
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert payload[0]["summary"] == "Stub summary"
    # cache hit returns cached flag
    cached_results = summariser.summarise([decision])
    assert cached_results[0].cached is True


def test_manifest_builder_merges_interface(tmp_path: Path) -> None:
    semantic = [
        {
            "file": "module.py",
            "summary": "semantic",
            "entities": [],
            "responsibilities": [],
            "dependencies": [],
            "confidence": 0.9,
            "model": "local://stub",
            "tier": "tier1",
            "latency_s": 0.0,
            "cached": False,
        }
    ]
    interface = [
        {
            "file": "module.py",
            "summary": "interface",
            "cli_commands": ["demo"],
            "api_endpoints": ["/demo"],
            "config_files": [],
            "test_cases": [],
            "doc_examples": [],
            "confidence": 0.8,
        }
    ]

    semantic_path = tmp_path / "semantic.json"
    interface_path = tmp_path / "interface.json"
    system_path = tmp_path / "system.json"
    semantic_path.write_text(json.dumps(semantic), encoding="utf-8")
    interface_path.write_text(json.dumps(interface), encoding="utf-8")
    system_path.write_text(json.dumps({"subsystems": []}), encoding="utf-8")

    manifest = build_manifest(
        semantic_path=semantic_path,
        interface_path=interface_path,
        system_path=system_path,
        output_path=tmp_path / "manifest.json",
    )

    assert manifest.stats["interface_entries"] == 1
    assert manifest.stats["interface_cli_commands"] == 1
    assert manifest.interfaces[0]["cli_commands"] == ["demo"]


def test_pipeline_runs_with_stub(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # create minimal python file
    root = tmp_path / "project"
    root.mkdir()
    (root / "demo.py").write_text("print('hello')\n", encoding="utf-8")

    # force summariser to use custom stub for interface stage
    from codexa.discovery import pipeline as pipeline_module

    def _summarise_modules(self, routing, focus_text: str, stage: str):  # noqa: ANN001
        if stage == "interface":
            summariser = Summarizer(
                model_invokers={
                    "local://python-mini": _interface_stub,
                    "cloud://gpt-standard": _interface_stub,
                    "cloud://gpt-advanced": _interface_stub,
                },
                prompt_profile=self.prompt_profile,
                prompt_registry=self.prompt_registry,
                stage=stage,
                project_root=self.project_root,
                semantic_digest_map=self.semantic_digest_map,
            )
        else:
            summariser = Summarizer(
                model_invokers={
                    "local://python-mini": _stub_invoker,
                    "cloud://gpt-standard": _stub_invoker,
                    "cloud://gpt-advanced": _stub_invoker,
                },
                prompt_profile=self.prompt_profile,
                prompt_registry=self.prompt_registry,
                stage=stage,
                project_root=self.project_root,
                semantic_digest_map=self.semantic_digest_map,
            )
        return summariser.summarise(routing)

    monkeypatch.setattr(pipeline_module.DiscoveryPipeline, "_summarise_modules", _summarise_modules, raising=False)

    monkeypatch.chdir(root)
    pipeline = DiscoveryPipeline(
        project_root=root,
        model_invokers={
            "local://python-mini": _stub_invoker,
            "cloud://gpt-standard": _stub_invoker,
            "cloud://gpt-advanced": _stub_invoker,
        },
    )
    output = pipeline.run(context=DiscoveryContext(project_root=root), emit_report=False)

    manifest_path = root / ".codexa" / "discovery" / "manifest.json"
    assert manifest_path.exists()
    assert output.resolve() == manifest_path.resolve()


def test_summarizer_uses_digest(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    file_path = tmp_path / "sample.py"
    file_path.write_text("raise RuntimeError('should not read file')\n", encoding="utf-8")

    manifest_path = tmp_path / "out.json"
    digest_string = "F:sample.py | L:python | C: | Fns:foo | Imps:os | Met:loc10,fc1,cc0,ic1,cd0.0"

    summariser = Summarizer(
        manifest_path=manifest_path,
        model_invokers={"local://stub": _stub_invoker},
        stage="semantic",
        project_root=tmp_path,
        semantic_digest_map={str(file_path): digest_string},
    )

    # ensure file read would fail if attempted
    monkeypatch.setattr(Summarizer, "_read_source", lambda *_: (_ for _ in ()).throw(AssertionError("should not read file")))

    decision = RoutingDecision(
        file=str(file_path),
        tier="tier1",
        model="local://stub",
        complexity=0.0,
        prev_confidence=0.2,
        rationale="digest",
    )

    summariser.summarise([decision])
    assert manifest_path.exists()
