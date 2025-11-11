"""Codexa Text-Frame integration layer."""

from __future__ import annotations

import asyncio
import logging
import os
import re
import shutil
import sys
from functools import partial
from pathlib import Path

from rich.markup import escape

from codexa import config_tools
from codexa.discovery import DiscoveryContext, DiscoveryPipeline, load_focus_context


def _inject_text_frame_path() -> None:
    candidates = []
    env_path = os.environ.get("TEXT_FRAME_PATH")
    if env_path:
        candidates.append(Path(env_path).expanduser())
    repo_default = Path(__file__).resolve().parents[3] / "text-frame"
    candidates.append(repo_default)

    for base in candidates:
        if not base:
            continue
        src = base / "src" if (base / "src").exists() else base
        if src.exists():
            sys_path = str(src)
            if sys_path not in sys.path:
                sys.path.append(sys_path)
            return


_inject_text_frame_path()

logger = logging.getLogger("codexa.tui")
LOG_PATH = Path(".codexa/logs/codexa_tui.log")
_ENV_LINE_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$")


class PromptCancelled(Exception):
    """Raised when a pending prompt is cancelled by the user."""


def _format_env_value(value: str) -> str:
    """Return a .env-safe representation of a value."""

    if value == "":
        return '""'
    if re.search(r"[\s#\"]", value):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return value


def _persist_env_value(root: Path, key: str, value: str) -> Path:
    """Ensure `key=value` exists in the project .env file."""

    env_path = root / ".env"
    lines: list[str] = []
    if env_path.exists():
        contents = env_path.read_text(encoding="utf-8")
        lines = contents.splitlines()
    replacement = f"{key}={_format_env_value(value)}"
    for idx, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[idx] = replacement
            break
    else:
        lines.append(replacement)
    text = "\n".join(line.rstrip() for line in lines)
    if text and not text.endswith("\n"):
        text += "\n"
    env_path.write_text(text, encoding="utf-8")
    return env_path


def _parse_env_value(raw: str) -> str:
    raw = raw.strip()
    if not raw:
        return ""
    if raw.startswith("#"):
        return ""
    quote = raw[0]
    if (quote == '"' and raw.endswith('"')) or (quote == "'" and raw.endswith("'")):
        body = raw[1:-1]
        body = body.replace("\\\"", '"').replace("\\'", "'").replace("\\\\", "\\")
        return body
    return raw.split(" #", 1)[0].strip()


def _load_env_value(root: Path, key: str) -> str | None:
    env_path = root / ".env"
    if not env_path.exists():
        return None
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if not line or line.lstrip().startswith("#"):
            continue
        match = _ENV_LINE_RE.match(line)
        if not match:
            continue
        name, raw_value = match.groups()
        if name == key:
            value = _parse_env_value(raw_value)
            return value
    return None


def _configure_logging() -> None:
    if logging.getLogger().handlers:
        return
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    log_level_name = os.environ.get("CODEXA_TUI_LOG", "DEBUG")
    level = getattr(logging, log_level_name.upper(), logging.DEBUG)
    handlers: list[logging.Handler] = [
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
    ]
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=handlers,
    )
    logger.info("Logging initialised at %s; file=%s", logging.getLevelName(level), LOG_PATH)

try:
    from text_frame import AppShell, Job
except ImportError as exc:  # pragma: no cover - runtime safeguard
    raise SystemExit(
        "Text-Frame is not installed. Install it with `pip install -e ../text-frame` "
        "or set TEXT_FRAME_PATH to the cloned repository."
    ) from exc

from scripts import discovery_bootstrap


class CodexaShell(AppShell):
    """Text-Frame shell with Codexa-specific helper commands."""

    def __init__(self, title: str = "Codexa", **kwargs) -> None:
        super().__init__(title, **kwargs)
        self._pending_prompt: asyncio.Future[str] | None = None
        self._pending_prompt_label: str | None = None
        self._pending_prompt_secret = False

    async def on_mount(self) -> None:  # type: ignore[override]
        await super().on_mount()
        if getattr(self, "output", None):
            self.output.update("Type /help for available commands.")

    async def command_status(self, job: Job) -> None:
        if not getattr(self, "output", None):
            await job.complete("Output widget missing")
            return
        await job.progress_update(0, "Collecting job status…")
        lines = ["Jobs:"]
        jobs = list(self.jobs.jobs.values())
        if not jobs:
            self.update_text_log("No jobs have been scheduled yet.")
            await job.complete("No jobs scheduled")
            return
        for managed_job in jobs:
            lines.append(
                f"• {managed_job.name} — {managed_job.status} ({managed_job.progress}% {managed_job.message})"
            )
        self.output.update("\n".join(lines))
        await job.complete("Reported job status")

    async def command_help(self, job: Job) -> None:
        if not getattr(self, "output", None):
            await job.complete("Output widget missing")
            return
        await job.progress_update(0, "Rendering help…")
        help_lines = [
            "Commands:",
            "  /discover — bootstrap discovery artifacts via scripts/discovery_bootstrap.py",
            "    • seeds .codexa/discovery/config.yaml when missing",
            "    • streams progress updates and reports manifest status",
            "  /discover-next — run `codexa discover-next --model-adapter gemini --summarize-mode digest`",
            "    • auto-loads GOOGLE_GENAI_API_KEY from environment/.env",
            "    • validates the key and prompts (type /cancel to abort) if missing/invalid",
            "    • persists new keys to .env for future runs",
            "    • uses Gemini digest batching (budget 2000 tokens, 20 files per batch)",
            "Meta:",
            "  /status — show queued/running/completed jobs",
            "  /help — show this message",
            "  /quit or /exit — exit the shell",
        ]
        self.clear_text_log()
        self.update_text_log("\n".join(help_lines))
        await job.complete("Displayed help")

    async def command_quit(self, job: Job) -> None:
        if getattr(self, "output", None):
            self.output.update("Shutting down Codexa shell…")
        await job.complete("Exiting Codexa shell")
        self.exit()

    async def prompt_for_value(self, label: str, *, secret: bool = False) -> str:
        """Request a value from the user, suspending command handling."""

        if self._pending_prompt is not None:
            raise RuntimeError("Another prompt is already active.")
        loop = asyncio.get_running_loop()
        future: asyncio.Future[str] = loop.create_future()
        self._pending_prompt = future
        self._pending_prompt_label = label
        self._pending_prompt_secret = secret
        guidance = f"{label} required — enter a value or /cancel."
        if getattr(self, "output", None):
            self.output.update(guidance)
        if self.text_log:
            self.text_log.write(f"[yellow]{escape(guidance)}[/]")
        try:
            return await future
        finally:
            self._pending_prompt = None
            self._pending_prompt_label = None
            self._pending_prompt_secret = False

    async def on_input_submitted(self, event: "Input.Submitted") -> None:  # type: ignore[override]
        value = event.value.strip()
        if getattr(self, "prompt", None):
            self.prompt.value = ""
        pending = self._pending_prompt
        if pending is not None:
            label = self._pending_prompt_label or "value"
            if not value:
                if getattr(self, "output", None):
                    self.output.update(f"{label} cannot be empty.")
                return
            token = value.lower()
            if token in {"/cancel", "cancel"}:
                if not pending.done():
                    pending.set_exception(PromptCancelled(f"{label} prompt cancelled"))
                if getattr(self, "output", None):
                    self.output.update(f"Cancelled input for {label}.")
                if self.text_log:
                    self.text_log.write(f"[red]{label} prompt cancelled.[/]")
                return
            display = "••••" if self._pending_prompt_secret else escape(value)
            if self.text_log:
                self.text_log.write(f"[green]{label} captured:[/] {display}")
            if getattr(self, "output", None):
                self.output.update(f"Captured value for {label}.")
            if not pending.done():
                pending.set_result(value)
            return
        await super().on_input_submitted(event)


def _threadsafe_progress(job: Job, loop: asyncio.AbstractEventLoop):
    def emit(percent: int, message: str = "") -> None:
        asyncio.run_coroutine_threadsafe(job.progress_update(percent, message), loop)

    return emit


def _ensure_discovery_config(root: Path) -> Path:
    """Ensure `.codexa/discovery/config.yaml` exists, seeding from docs if needed."""
    codexa_config = root / ".codexa/discovery/config.yaml"
    if codexa_config.exists():
        return codexa_config

    fallback = root / "docs/discovery/config.yaml"
    if fallback.exists():
        codexa_config.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(fallback, codexa_config)
        logger.info(
            "Seeded discovery config from %s to %s", fallback.relative_to(root), codexa_config.relative_to(root)
        )
        return codexa_config

    return _bootstrap_discovery_config(root)


def _bootstrap_discovery_config(root: Path) -> Path:
    """Generate a starter discovery config when none exists yet."""
    codexa_config = root / ".codexa/discovery/config.yaml"
    try:
        recommendation = config_tools.generate_config_recommendation(root)
    except Exception as exc:  # pragma: no cover - defensive
        raise FileNotFoundError(
            "Unable to synthesise a discovery config automatically; supply docs/discovery/config.yaml manually."
        ) from exc

    try:
        written = config_tools.write_config_yaml(
            recommendation["yaml"],
            codexa_config,
            force=False,
        )
    except FileExistsError:
        return codexa_config
    except Exception as exc:  # pragma: no cover - defensive
        raise FileNotFoundError(f"Failed to write discovery config to {codexa_config}") from exc

    logger.info(
        "Auto-generated discovery config at %s (languages: %s)",
        written.relative_to(root),
        ", ".join(
            entry["language"] for entry in recommendation["summary"].get("language_sample", []) if entry.get("language")
        )
        or "unknown",
    )
    return written


async def discover_job(job: Job, project_root: Path | None = None) -> None:
    """Execute the synchronous bootstrapper in a worker thread and stream progress."""

    loop = asyncio.get_running_loop()
    root = project_root or Path.cwd()
    progress_callback = _threadsafe_progress(job, loop)
    _ensure_discovery_config(root)

    def _run() -> dict:
        return discovery_bootstrap.run_discovery(
            project_root=root,
            progress_callback=progress_callback,
        )

    await job.progress_update(2, "Starting discovery…")
    result = await asyncio.to_thread(_run)
    manifest_rel = result["paths"].get("manifest", "?.yaml")
    await job.complete(f"Discovery finished — {manifest_rel}")


def _run_discover_next_pipeline(project_root: Path):
    """Execute the adaptive discovery pipeline using the Gemini adapter."""

    try:
        from codexa.discovery.adapters.gemini import build_gemini_models  # local import to avoid hard dependency
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError(
            "Gemini adapter requires the `google-genai` package. Install it with `pip install google-genai`."
        ) from exc

    adapter_models = build_gemini_models(project_root)
    gemini_model = next(iter(adapter_models.keys()))
    router_kwargs = {
        "model_map": {
            "tier1": gemini_model,
            "tier2": gemini_model,
            "tier3": gemini_model,
        }
    }
    pipeline = DiscoveryPipeline(
        project_root=project_root,
        model_invokers=adapter_models,
        router_kwargs=router_kwargs,
        prompt_profile="default",
        summarize_mode="digest",
        digest_batch_budget=2000,
        digest_batch_max=20,
    )
    context = DiscoveryContext(project_root=project_root, scope=None, focus_notes=None)
    artifact_path = pipeline.run(context=context, emit_report=True)
    manifest_path = project_root / ".codexa/discovery/manifest.json"
    focus_ctx = load_focus_context()
    return artifact_path, manifest_path, focus_ctx


async def discover_next_job(
    job: Job,
    *,
    shell: CodexaShell,
    project_root: Path | None = None,
) -> None:
    """Run `codexa discover-next` with Gemini defaults, prompting for config as needed."""

    root = project_root or Path.cwd()
    await job.progress_update(1, "Preparing Gemini discovery…")
    _ensure_discovery_config(root)
    try:
        await _ensure_google_api_key(shell, root)
    except PromptCancelled as exc:
        await job.complete(str(exc))
        return

    await job.progress_update(5, "Invoking adaptive discovery pipeline…")

    def _run():
        return _run_discover_next_pipeline(root)

    try:
        artifact_path, manifest_path, focus_ctx = await asyncio.to_thread(_run)
    except Exception as exc:  # pragma: no cover - surfaced in UI
        logger.exception("discover-next job failed", exc_info=exc)
        raise

    rel_report = _safe_rel_path(artifact_path, root)
    rel_manifest = _safe_rel_path(manifest_path, root)
    await job.complete(f"Discovery-next report: {rel_report}")
    if shell.text_log:
        shell.text_log.write(f"[green]Manifest updated:[/] {escape(rel_manifest)}")
        if focus_ctx and focus_ctx.auto_focus:
            shell.text_log.write("[blue]Suggested focus targets:[/]")
            for entry in focus_ctx.auto_focus:
                shell.text_log.write(f"  • {escape(entry)}")
        if focus_ctx and focus_ctx.user_notes.strip():
            shell.text_log.write("[blue]User focus notes retained for future runs.[/]")


def _safe_rel_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _validate_google_api_key(key: str) -> None:
    """Issue a lightweight API call to confirm the Gemini key works."""

    try:
        from google import genai
        from google.genai.errors import ClientError
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError(
            "google-genai is required to validate GOOGLE_GENAI_API_KEY. Install it with `pip install google-genai`."
        ) from exc

    client = genai.Client(api_key=key)
    try:
        client.models.list(page_size=1)
    except ClientError as exc:
        raise RuntimeError(exc) from exc


async def _ensure_google_api_key(shell: CodexaShell, root: Path) -> str:
    """Ensure GOOGLE_GENAI_API_KEY exists, sourcing .env and validating before use."""

    var_name = "GOOGLE_GENAI_API_KEY"
    invalid_values: set[str] = set()

    while True:
        source = "environment"
        key = os.environ.get(var_name)
        key_from_prompt = False

        if not key or key in invalid_values:
            key = _load_env_value(root, var_name)
            source = ".env"
            if key in invalid_values:
                key = None

        if not key:
            if shell.text_log:
                shell.text_log.write(
                    "[yellow]GOOGLE_GENAI_API_KEY missing. Provide a key or type /cancel.[/]"
                )
            try:
                key = await shell.prompt_for_value(var_name, secret=True)
            except PromptCancelled:
                raise
            if not key:
                continue
            key_from_prompt = True
            source = "prompt"

        try:
            await asyncio.to_thread(_validate_google_api_key, key)
        except Exception as exc:  # pragma: no cover - depends on remote API
            invalid_values.add(key)
            os.environ.pop(var_name, None)
            warning = f"{var_name} validation failed from {source}: {exc}"
            if shell.text_log:
                shell.text_log.write(f"[red]{escape(warning)}[/]")
            if source == ".env" and shell.text_log:
                shell.text_log.write(
                    "[yellow]Update the stored key in .env or enter a new one to continue.[/]"
                )
            continue

        os.environ[var_name] = key
        if key_from_prompt:
            try:
                env_path = _persist_env_value(root, var_name, key)
                if shell.text_log:
                    shell.text_log.write(
                        f"[cyan]Saved {var_name} to {escape(str(env_path.relative_to(root)))}[/]"
                    )
            except Exception as exc:  # pragma: no cover - best-effort persistence
                logger.warning("Failed to persist %s: %s", var_name, exc)
        elif source == ".env" and shell.text_log:
            shell.text_log.write(f"[green]Loaded {var_name} from .env[/]")

        return key


def main() -> None:
    _configure_logging()
    app = CodexaShell("Codexa")
    app.add_command("/discover", discover_job)
    app.add_command("/discover-next", partial(discover_next_job, shell=app))
    app.add_command("/quit", app.command_quit, tracked=False)
    app.add_command("/exit", app.command_quit, tracked=False)
    app.add_command("/status", app.command_status, tracked=False)
    app.add_command("/help", app.command_help, tracked=False)
    app.add_command("?", app.command_help, tracked=False)
    app.enable_history = True
    app.run()


if __name__ == "__main__":
    main()
