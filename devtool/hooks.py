"""Git pre-commit hooks installer and manager."""

from __future__ import annotations
import os
import stat
import subprocess
from pathlib import Path
from typing import Sequence

GIT_HOOKS_DIR = ".git/hooks"
HOOK_SCRIPTS = {
    "pre-commit": r"""#!/usr/bin/env bash
set -e
echo "⇒ Running pre-commit checks..."
# Format check (if black/isort available)
if command -v black &>/dev/null; then
    black --check --diff . || { echo "FAILED: black format check"; exit 1; }
fi
if command -v isort &>/dev/null; then
    isort --check-only --diff . || { echo "FAILED: isort check"; exit 1; }
fi
# Python syntax check
if command -v python3 &>/dev/null; then
    python3 -m py_compile $(git diff --name-only --diff-filter=ACMR -- '*.py' | tr '\n' ' ') 2>/dev/null || true
fi
echo "✓ Pre-commit checks passed"
""",
    "pre-push": r"""#!/usr/bin/env bash
set -e
echo "⇒ Running pre-push checks..."
if command -v pytest &>/dev/null; then
    pytest -x -q 2>/dev/null || { echo "FAILED: tests"; exit 1; }
fi
echo "✓ Pre-push checks passed"
""",
    "commit-msg": r"""#!/usr/bin/env bash
COMMIT_MSG_FILE=$1
COMMIT_MSG=$(cat "$COMMIT_MSG_FILE")
if ! echo "$COMMIT_MSG" | grep -qE '^(feat|fix|docs|style|refactor|test|chore|perf|ci|build|revert)\('; then
    echo "Commit message must start with a type: feat(.), fix(.), docs(.), etc."
    echo "Examples: feat(auth): add login, fix(bug): resolve crash"
    exit 1
fi
""",
}


def _git_dir(cwd: Path | None = None) -> Path | None:
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=cwd or Path.cwd(),
            capture_output=True, text=True, timeout=5,
        )
        if r.returncode == 0:
            return Path(r.stdout.strip())
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def add_hooks(cwd: Path | str | None = None, hooks: Sequence[str] | None = None) -> dict[str, bool]:
    """Install git hooks. Returns {hook_name: success}."""
    if hooks is None:
        hooks = list(HOOK_SCRIPTS.keys())
    git_dir = _git_dir(cwd)
    if git_dir is None:
        return {h: False for h in hooks}
    results: dict[str, bool] = {}
    for hook in hooks:
        if hook not in HOOK_SCRIPTS:
            results[hook] = False
            continue
        hook_path = git_dir / hook
        try:
            hook_path.write_text(HOOK_SCRIPTS[hook])
            hook_path.chmod(stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
            results[hook] = True
        except OSError:
            results[hook] = False
    return results


def remove_hooks(cwd: Path | str | None = None, hooks: Sequence[str] | None = None) -> dict[str, bool]:
    """Remove git hooks. Returns {hook_name: removed}."""
    if hooks is None:
        hooks = list(HOOK_SCRIPTS.keys())
    git_dir = _git_dir(cwd)
    if git_dir is None:
        return {h: False for h in hooks}
    results: dict[str, bool] = {}
    for hook in hooks:
        hook_path = git_dir / hook
        try:
            if hook_path.exists():
                hook_path.unlink()
            results[hook] = True
        except OSError:
            results[hook] = False
    return results


def list_hooks(cwd: Path | str | None = None) -> dict[str, bool]:
    """List installed git hooks. Returns {hook_name: exists}."""
    git_dir = _git_dir(cwd)
    if git_dir is None:
        return {}
    results: dict[str, bool] = {}
    for hook in HOOK_SCRIPTS:
        results[hook] = (git_dir / hook).exists()
    return results
