"""Release version bumping and changelog helpers."""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class Version:
    """SemVer-compatible version."""
    major: int = 0
    minor: int = 1
    patch: int = 0
    prerelease: str | None = None

    def __str__(self) -> str:
        base = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            base += f"-{self.prerelease}"
        return base

    @classmethod
    def parse(cls, text: str) -> "Version":
        m = re.match(r"(\d+)\.(\d+)\.(\d+)(?:-(.+))?", text.strip())
        if not m:
            raise ValueError(f"Invalid version string: {text}")
        v = cls(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        if m.group(4):
            v.prerelease = m.group(4)
        return v

    def bump_major(self) -> "Version":
        return Version(self.major + 1, 0, 0)

    def bump_minor(self) -> "Version":
        return Version(self.major, self.minor + 1, 0)

    def bump_patch(self) -> "Version":
        return Version(self.major, self.minor, self.patch + 1)


@dataclass
class ChangelogEntry:
    version: Version
    date: str
    changes: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        lines = [f"## [{self.version}] - {self.date}"]
        for c in self.changes:
            lines.append(f"- {c}")
        return "\n".join(lines)


def release_bump(cwd: Path | str | None = None, level: str = "patch",
                 file: str = "VERSION") -> Version:
    """Read current version from file, bump it, write back.

    level: 'major', 'minor', or 'patch'
    """
    cwd = Path(cwd or Path.cwd())
    vfile = cwd / file
    current_text = vfile.read_text().strip() if vfile.exists() else "0.1.0"
    current = Version.parse(current_text)

    if level == "major":
        new = current.bump_major()
    elif level == "minor":
        new = current.bump_minor()
    else:
        new = current.bump_patch()

    vfile.write_text(str(new) + "\n")
    return new


def read_version(cwd: Path | str | None = None, file: str = "VERSION") -> Version:
    """Read the current version from a file."""
    cwd = Path(cwd or Path.cwd())
    vfile = cwd / file
    text = vfile.read_text().strip() if vfile.exists() else "0.1.0"
    return Version.parse(text)
