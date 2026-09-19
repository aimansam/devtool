"""devtool -- Developer workflow automation toolkit.

Hooks, git helpers, code quality scanners, scaffolding wizards, and
release automation -- tools developers actually use daily.
"""

__version__ = "1.0.0"
__all__ = [
    "add_hooks", "remove_hooks", "list_hooks",
    "git_status_table", "git_branch_summary", "git_log_summary",
    "scan_unused", "find_todos", "size_report",
    "release_bump", "wizard_project",
]

from .hooks import add_hooks, remove_hooks, list_hooks
from .githelpers import git_status_table, git_branch_summary, git_log_summary
from .scan import scan_unused, find_todos, size_report
from .bump import release_bump
from .wizard import wizard_project
