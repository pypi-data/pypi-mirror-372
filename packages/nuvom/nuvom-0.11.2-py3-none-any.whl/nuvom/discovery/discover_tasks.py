# nuvom/discovery/discover_tasks.py

"""
Core logic to scan a directory tree and discover all @task definitions.
Returns a list of TaskReference objects representing discovered tasks.
Supports filtering files via include and exclude glob patterns.
"""

from typing import List
from pathlib import Path
from nuvom.discovery.walker import get_python_files
from nuvom.discovery.parser import find_task_defs
from nuvom.discovery.compute_path import compute_module_path
from nuvom.discovery.reference import TaskReference


def discover_tasks(
    root_path: str = ".",
    include: List[str] = [],
    exclude: List[str] = []
) -> List[TaskReference]:
    task_refs: List[TaskReference] = []
    files = get_python_files(root_path, include, exclude)

    root = Path(root_path).resolve()
    for file in files:
        task_names = find_task_defs(file)
        for name in task_names:
            module_path = compute_module_path(file, root_path=root)
            task_refs.append(TaskReference(str(file), name, module_path))

    return task_refs
