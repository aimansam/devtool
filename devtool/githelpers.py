"""Git status, branch, and log summary tools."""

from __future__ import annotations
import subprocess
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class GitStatus:
    """Parsed git status output."""
    branch: str = ""
    ahead: int = 0
    behind: int = 0
    staged: list[str] = field(default_factory=list)
    unstaged: list[str] = field(default_factory=list)
    untracked: list[str] = field(default_factory=list)
    modified: list[str] = field(default_factory=list)
    deleted: list[str] = field(default_factory=list)
    renamed: list[tuple[str, str]] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.staged or self.unstaged or self.untracked)

    @property
    def summary(self) -> str:
        parts = []
        if self.branch:
            parts.append(f"On branch {self.branch}")
            if self.ahead:
                parts[-1] += f" (+{self.ahead})"
            if self.behind:
                parts[-1] += f" (-{self.behind})"
        if self.staged:
            parts.append(f"{len(self.staged)} staged")
        if self.unstaged:
            parts.append(f"{len(self.unstaged)} modified")
        if self.untracked:
            parts.append(f"{len(self.untracked)} untracked")
        return " | ".join(parts) if parts else "Clean working tree"


def git_status(cwd: Path | str | None = None) -> GitStatus:
    """Run git status and return a structured result."""
    cwd = Path(cwd or Path.cwd())
    try:
        r = subprocess.run(
            ["git", "status", "--porcelain", "-b"],
            cwd=cwd, capture_output=True, text=True, timeout=10,
        )
        if r.returncode != 0:
            return GitStatus()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return GitStatus()

    lines = r.stdout.strip().split("\n")
    if not lines or lines[0] == "":
        return GitStatus()

    status = GitStatus()

    # Branch line
    branch_line = lines[0]
    if branch_line.startswith("##"):
        parts = branch_line[3:].split()
        if parts:
            status.branch = parts[0]
            for p in parts[1:]:
                if p.startswith("ahead"):
                    status.ahead = int(p.split("=")[-1])
                elif p.startswith("behind"):
                    status.behind = int(p.split("=")[-1])

    # Status lines
    for line in lines[1:]:
        if not line or len(line) < 3:
            continue
        st = line[:2]
        fname = line[3:]
        if st == "??":
            status.untracked.append(fname)
        elif st[0] == "A":
            status.staged.append(fname)
        elif st[1] == "A":
            status.staged.append(fname)
        elif st[0] == "M":
            status.staged.append(fname)
        elif st[1] == "M":
            status.unstaged.append(fname)
        elif st[0] == "D":
            status.deleted.append(fname)
        elif st[1] == "D":
            status.deleted.append(fname)
        elif "R" in st:
            old = fname.split(" -> ")[0] if " -> " in fname else fname
            new = fname.split(" -> ")[1] if " -> " in fname else fname
            status.renamed.append((old, new))
        else:
            status.unstaged.append(fname)

    status.modified = status.unstaged
    return status


def git_branch_summary(cwd: Path | str | None = None, all_branches: bool = False) -> list[dict[str, Any]]:
    """Get branch list with tracking info."""
    cwd = Path(cwd or Path.cwd())
    try:
        flags = ["--all"] if all_branches else []
        r = subprocess.run(
            ["git", "branch", *flags],
            cwd=cwd, capture_output=True, text=True, timeout=10,
        )
        if r.returncode != 0:
            return []
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []

    branches: list[dict[str, Any]] = []
    for line in r.stdout.strip().split("\n"):
        if not line:
            continue
        current = line.startswith("* ")
        name = line.lstrip("* ").strip()
        branches.append({"name": name, "current": current})
    return branches


def git_log_summary(cwd: Path | str | None = None, n: int = 10) -> list[dict[str, Any]]:
    """Get last n commits with stats."""
    cwd = Path(cwd or Path.cwd())
    try:
        r = subprocess.run(
            ["git", "log", f"-{n}", "--format=%H|||%an|||%ae|||%ad|||%s",
             "--date=short", "--numstat"],
            cwd=cwd, capture_output=True, text=True, timeout=10,
        )
        if r.returncode != 0:
            return []
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []

    commits: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for line in r.stdout.strip().split("\n"):
        if "|||" in line and len(line.split("|||")) == 5:
            h, an, ae, ad, subj = line.split("|||")
            current = {
                "hash": h[:7],
                "author": an,
                "author_email": ae,
                "date": ad,
                "subject": subj,
                "stats": {"files": 0, "insertions": 0, "deletions": 0},
            }
            commits.append(current)
        elif line and current is not None and line.strip() and not line.startswith("Binary"):
            parts = line.split()
            if len(parts) >= 3:
                try:
                    current["stats"]["files"] += 1
                    current["stats"]["insertions"] += int(parts[0])
                    current["stats"]["deletions"] += int(parts[1])
                except ValueError:
                    pass
    return commits


def git_status_table(cwd: Path | str | None = None) -> str:
    """Return a formatted table of git status."""
    s = git_status(cwd)
    lines = []
    lines.append(f"Branch: {s.branch or 'unknown'}")
    if s.ahead or s.behind:
        flags = []
        if s.ahead:
            flags.append(f"+{s.ahead}")
        if s.behind:
            flags.append(f"-{s.behind}")
        lines[-1] += f"  ({' '.join(flags)})"
    lines.append("")
    if s.staged:
        lines.append(f"Staged ({len(s.staged)}):")
        for f in s.staged[:20]:
            lines.append(f"  A  {f}")
        if len(s.staged) > 20:
            lines.append(f"  ... and {len(s.staged) - 20} more")
    if s.modified or s.unstaged:
        lines.append(f"Modified ({len(s.unstaged)}):")
        for f in s.unstaged[:20]:
            lines.append(f"  M  {f}")
        if len(s.unstaged) > 20:
            lines.append(f"  ... and {len(s.unstaged) - 20} more")
    if s.untracked:
        lines.append(f"Untracked ({len(s.untracked)}):")
        for f in s.untracked[:20]:
            lines.append(f"  ?  {f}")
        if len(s.untracked) > 20:
            lines.append(f"  ... and {len(s.untracked) - 20} more")
    if not s.has_changes:
        lines.append("Nothing to commit, working tree clean")
    return "\n".join(lines)
