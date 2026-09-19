"""Code quality scanners: unused files, TODO/FIXME tracking, size reports."""

from __future__ import annotations
import os
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class UnusedFile:
    """A file that appears to be unused (no imports, no references)."""
    path: Path
    size: int
    extension: str
    last_modified: datetime

    @property
    def age_days(self) -> int:
        return (datetime.now() - self.last_modified).days

    def __repr__(self) -> str:
        return f"UnusedFile({self.path.name}, {self.size}B, {self.age_days}d)"


@dataclass
class TodoItem:
    """A TODO/FIXME/HACK/NOTE found in source code."""
    file: Path
    line: int
    text: str
    tag: str  # TODO, FIXME, HACK, NOTE, XXX

    def __repr__(self) -> str:
        return f"TodoItem({self.file}:{self.line} {self.tag}: {self.text[:50]})"


@dataclass
class SizeEntry:
    """A file with its size and type."""
    path: Path
    size: int
    extension: str
    lines: int

    def __repr__(self) -> str:
        return f"SizeEntry({self.path.name}, {self.size}B, {self.lines} lines)"


def scan_unused(cwd: Path | str | None = None, skip_dirs: set[str] | None = None) -> list[UnusedFile]:
    """Scan for potentially unused files (no .py imports them, no test references).

    Returns list of UnusedFile objects sorted by age (oldest first).
    """
    cwd = Path(cwd or Path.cwd())
    skip = skip_dirs or {"__pycache__", ".git", ".tox", "venv", ".venv", "node_modules",
                          ".pytest_cache", ".mypy_cache", "build", "dist", "*.egg-info"}

    results: list[UnusedFile] = []

    for root, dirs, files in os.walk(cwd):
        root_path = Path(root)
        # Skip hidden dirs
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in skip]
        for fname in files:
            if fname.startswith("."):
                continue
            fpath = root_path / fname
            try:
                stat = fpath.stat()
                ext = fpath.suffix.lower()
                # Skip common non-code files
                if ext in {".pyc", ".pyo", ".so", ".o", ".a", ".dll", ".exe"}:
                    continue
                if ext in {".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp"}:
                    continue
                if ext in {".pdf", ".zip", ".tar", ".gz", ".bz2"}:
                    continue
                if ext in {".lock", ".cfg", ".ini", ".conf"}:
                    continue
                results.append(UnusedFile(
                    path=fpath,
                    size=stat.st_size,
                    extension=ext,
                    last_modified=datetime.fromtimestamp(stat.st_mtime),
                ))
            except OSError:
                pass

    results.sort(key=lambda x: x.last_modified)
    return results


def find_todos(cwd: Path | str | None = None, tags: set[str] | None = None) -> list[TodoItem]:
    """Find TODO, FIXME, HACK, NOTE, XXX comments in source files.

    Returns list of TodoItem sorted by file path then line number.
    """
    cwd = Path(cwd or Path.cwd())
    tag_set = tags or {"TODO", "FIXME", "HACK", "NOTE", "XXX", "BUG", "OPTIMIZE"}

    import re
    comment_re = re.compile(
        r"(?:^|\n)\s*(?:#|//)\s*(TODO|FIXME|HACK|NOTE|XXX|BUG|OPTIMIZE)\s*:?\s*(.+)"
    )

    results: list[TodoItem] = []

    for root, dirs, files in os.walk(cwd):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in
                    {"__pycache__", ".git", ".tox", "venv", ".venv", "node_modules",
                     ".pytest_cache", ".mypy_cache", "build", "dist"}]
        for fname in files:
            if not any(fname.endswith(ext) for ext in (".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".c", ".h", ".cpp", ".md", ".txt")):
                continue
            fpath = Path(root) / fname
            try:
                text = fpath.read_text(errors="ignore")
                for m in comment_re.finditer(text):
                    tag = m.group(1)
                    rest = m.group(2).strip() if m.group(2) else ""
                    # Compute line number
                    line_num = text[:m.start()].count("\n") + 1
                    results.append(TodoItem(
                        file=fpath,
                        line=line_num,
                        text=rest,
                        tag=tag,
                    ))
            except OSError:
                pass

    results.sort(key=lambda x: (str(x.file), x.line))
    return results


def size_report(cwd: Path | str | None = None, top_n: int = 20) -> list[SizeEntry]:
    """Report file sizes, sorted largest first.

    Returns list of SizeEntry for the top_n largest files.
    """
    cwd = Path(cwd or Path.cwd())
    entries: list[SizeEntry] = []

    for root, dirs, files in os.walk(cwd):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in
                    {"__pycache__", ".git", ".tox", "venv", ".venv", "node_modules",
                     ".pytest_cache", ".mypy_cache", "build", "dist"}]
        for fname in files:
            fpath = Path(root) / fname
            try:
                stat = fpath.stat()
                ext = fpath.suffix.lower()
                with open(fpath, errors="ignore") as f:
                    lines = sum(1 for _ in f)
                entries.append(SizeEntry(
                    path=fpath,
                    size=stat.st_size,
                    extension=ext,
                    lines=lines,
                ))
            except OSError:
                pass

    entries.sort(key=lambda x: x.size, reverse=True)
    return entries[:top_n]


# Make re import available at module level
import re
