import asyncio
import logging
from pathlib import Path

from text_frame import app, job


LOG_FILE = Path(__file__).with_suffix(".log")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="w"),
    ],
)


async def indexed_scan(job_ctx: job.Job):
    """Tracked job that reports incremental progress and a closing message."""
    for idx in range(0, 101, 20):
        await asyncio.sleep(0.2)
        await job_ctx.progress_update(idx, f"scanning chunk {idx // 20 + 1}")
    await job_ctx.complete("Scan finished cleanly.")


async def show_help(job_ctx: job.Job):
    """Untracked command; still completes but never appears in the JobTable."""
    await job_ctx.progress_update(0, "Listing commands…")
    await asyncio.sleep(0.1)
    await job_ctx.complete("Commands: scan, help")


if __name__ == "__main__":
    shell = app.AppShell("Tracked/Untracked Demo")
    shell.add_command("scan", indexed_scan, tracked=True)
    shell.add_command("help", show_help, tracked=False)
    shell.run()
