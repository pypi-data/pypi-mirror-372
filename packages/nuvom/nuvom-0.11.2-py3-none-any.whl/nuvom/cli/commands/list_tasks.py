# nuvom/cli/commands/list_tasks.py
"""
List registered @task definitions and their metadata.
"""

import typer
from rich.console import Console
from rich.table import Table

from nuvom.discovery.manifest import ManifestManager
from nuvom.registry.registry import get_task_registry, TaskInfo
from nuvom.log import get_logger

console = Console()
logger = get_logger()

list_app = typer.Typer(
    name="list",
    help=(
        "List tasks discovered in the manifest and registered at runtime.\n\n"
        "Examples:\n"
        "  nuvom list tasks                 # table of tasks\n"
        "  nuvom discover tasks && nuvom list tasks  # rescan then list\n"
    ),
    rich_help_panel="🌟  Core Commands",
)


@list_app.command("tasks")
def list_tasks():
    """Render a table of all @task definitions with metadata columns."""
    manifest = ManifestManager()
    discovered_tasks = manifest.load()
    registry = get_task_registry()

    logger.debug("Loaded %d tasks from manifest", len(discovered_tasks))

    table = Table(title="Registered Tasks", show_lines=True)
    table.add_column("Name", style="yellow")
    table.add_column("Module", style="blue")
    table.add_column("Path", style="dim")
    table.add_column("Tags", style="green")
    table.add_column("Description", style="white")

    for task in discovered_tasks:
        task_info: TaskInfo = registry.all().get(task.func_name)
        metadata = task_info.metadata if task_info else {}
        tags = ", ".join(metadata.get("tags", []))
        description = metadata.get("description", "")
        table.add_row(task.func_name, task.module_name, task.file_path, tags, description)

    if not discovered_tasks:
        console.print("[yellow]No task definitions found.[/yellow]")
    else:
        console.print(table)
        logger.info("Listed %d tasks", len(discovered_tasks))
