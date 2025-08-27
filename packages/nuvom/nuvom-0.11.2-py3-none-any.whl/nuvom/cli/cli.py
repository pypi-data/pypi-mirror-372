# nuvom/cli/cli.py

import typer
import threading
import time
from pathlib import Path
from rich.console import Console

from nuvom import __version__
from nuvom.config import get_settings
from nuvom.worker import start_worker_pool
from nuvom.result_store import get_result, get_error
from nuvom.cli.commands import discover_tasks, list_tasks, inspect_job, history, runtestworker, plugin
from nuvom.log import get_logger

logger = get_logger()

console = Console()
app = typer.Typer(
    add_completion=False,
    help=(
        "Nuvom – lightweight, plugin-first task-queue.\n\n"
        "Common commands:\n"
        "  nuvom discover tasks       # scan & update manifest\n\n"
        "  nuvom runworker            # start local workers\n\n"
        "  nuvom inspect job <id> -f table|json|raw\n\n"
        "  nuvom history recent --limit 10\n\n"
    ),
    rich_help_panel="🌟  Core Commands",
)

@app.command(rich_help_panel="📦  Misc")
def version():
    """Show current Nuvom version."""
    console.print(f"[bold green]NUVOM v{__version__}[/bold green]")

@app.command(rich_help_panel="📦  Misc")
def config():
    """Print current settings loaded from .env / env vars."""
    settings = get_settings()
    console.print("[bold green]Nuvom Configuration:[/bold green]")
    for key, val in settings.summary().items():
        console.print(f"[cyan]{key}[/cyan] = {val}")

@app.command(rich_help_panel="🌟  Core Commands")
def runworker(
    dev: bool = typer.Option(
        False,
        "--dev",
        help="Enable hot-reload on manifest changes (best for local dev)",
        )
    ):
    """Start worker pool in the foreground."""
    
    console.print("[yellow]🚀 Starting worker...[/yellow]")
    logger.info("Starting worker pool with dev=%s", dev)

    observer = None
    if dev:
        from nuvom.watcher import ManifestChangeHandler
        from watchdog.observers import Observer

        manifest_path = Path(".nuvom/manifest.json").resolve()
        handler = ManifestChangeHandler(manifest_path)
        observer = Observer()
        observer.schedule(handler, manifest_path.parent, recursive=False)
        observer.start()
        console.print("[blue]🌀 Dev mode active — watching manifest for changes...[/blue]")
        logger.debug("Manifest watcher started on %s", manifest_path)

    try:
        start_worker_pool()
    finally:
        if observer:
            observer.stop()
            observer.join()
            logger.debug("Manifest watcher stopped")
            
 
@app.command(rich_help_panel="🌟  Core Commands")
def runscheduler(
    poll: float = typer.Option(
        1.0,
        "--poll",
        "-p",
        help="Polling interval (seconds) between checks for due jobs."
    ),
    batch: int = typer.Option(
        100,
        "--batch",
        "-b",
        help="Maximum number of schedules dispatched per iteration."
    ),
    jitter: float = typer.Option(
        0.0,
        "--jitter",
        "-j",
        help="Optional random jitter (seconds) to reduce sync across replicas."
    ),
):
    """
    Start the scheduler worker in the foreground.

    Examples:
        nuvom runscheduler
        nuvom runscheduler --poll 2.0 --batch 50 --jitter 0.5
    """
    from nuvom.scheduler.worker import SchedulerWorker

    console.print("[yellow]⏳ Starting scheduler worker...[/yellow]")
    logger.info(
        "Starting scheduler worker (poll=%.3fs, batch=%d, jitter=%.3fs)",
        poll, batch, jitter
    )

    worker = SchedulerWorker(
        poll_interval=poll,
        batch_size=batch,
        jitter=jitter,
    )

    try:
        # Foreground blocking mode
        worker.start(background=False)
    except KeyboardInterrupt:
        console.print("\n[cyan]🛑 Stopping scheduler worker (KeyboardInterrupt)...[/cyan]")
        logger.info("Scheduler worker shutdown requested by user.")
        worker.stop()      
            

@app.command(rich_help_panel="🌟  Core Commands")
def status(job_id: str):
    """
    Quick one-off status check (success / failure / pending).

    Example:
        nuvom status a1b2c3d4
    """
    error = get_error(job_id)
    if error:
        console.print(f"[bold red]❌ FAILED:[/bold red] {error}")
        logger.warning("Job %s failed: %s", job_id, error)
        return

    result = get_result(job_id)
    if result is not None:
        console.print(f"[bold green]✅ SUCCESS:[/bold green] {result}")
        logger.info("Job %s succeeded: %s", job_id, result)
        return

    console.print("[cyan]🕒 PENDING[/cyan]")
    logger.info("Job %s is pending", job_id)

#  ------ sub-apps (now displayed under dedicated help panels) --------------
app.add_typer(discover_tasks.discover_app,  name="discover",)
app.add_typer(list_tasks.list_app,          name="list",    )
app.add_typer(inspect_job.inspect_app,      name="inspect", )
app.add_typer(history.history_app,          name="history", )
app.add_typer(runtestworker.runtest_app,    name="runtestworker", rich_help_panel="⚙  Dev Tools")
app.add_typer(plugin.plugin_app,            name="plugin",        rich_help_panel="🔌 Plugins")

def main():
    app()
