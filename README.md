# devtool

**Developer workflow automation toolkit — git hooks, project scaffolding, and code scanners in one pip install.**

Hooks to enforce code quality, a wizard to scaffold new projects, scanners to find TODOs and unused files, and helpers for git status and release versioning. Everything you reach for across projects, packaged as one CLI.

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

```
Branch: unknown

Nothing to commit, working tree clean
```

*devtool git status — formatted table output, zero dependencies.*

## Quickstart

```bash
pip install -e .
```

```bash
# Install git hooks for the current repo
devtool hooks install

# Scan for TODO/FIXME/HACK comments
devtool scan todos

# Find large files bloating the repo
devtool scan size

# Find unused files
devtool scan unused

# Generate a new project from a template
devtool project create --template python-cli --name mytool

# Show git status as a formatted table
devtool git status

# Bump version
devtool release bump --level patch
```

## What it does

### Git hooks
Install pre-commit, pre-push, and commit-msg hooks with one command. Hooks check formatting (black/isort if available), Python syntax, and enforce commit message conventions (`type(scope): description`).

```bash
devtool hooks install
devtool hooks list
devtool hooks remove
```

### Project scaffolding wizard
Generate new project structures from templates — no copy-pasting from old repos.

- `python-cli` — CLI tool with argparse, pyproject.toml, tests, README
- `python-lib` — library with typed code, tests, docs skeleton

```bash
devtool project create --template python-cli --name mytool
devtool project create --template python-lib --name mylib
```

### Code quality scanners

**Find TODOs and FIXMEs:**
```bash
devtool scan todos
# Returns: file:line  TAG: message
```

**Find large files:**
```bash
devtool scan size
# Returns: path  size  extension  lines
```

**Find unused files:**
```bash
devtool scan unused
# Returns files with no imports, sorted by age
```

### Git helpers
```bash
devtool git status      # Formatted table: branch, staged, modified, untracked
devtool git branches    # List branches with current marker
devtool git log         # Last N commits with author, date, subject, stats
```

### Release helpers
```bash
devtool release bump --level patch   # 0.1.0 -> 0.1.1
devtool bump --level minor   # 0.1.0 -> 0.2.0
devtool release bump --level major   # 0.1.0 -> 1.0.0
```

## Installation

```bash
git clone https://github.com/yourusername/devtool.git
cd devtool
pip install -e .
```

Requires Python 3.9+. No external dependencies — uses only the standard library plus Click for the CLI.

```bash
pip install click
```

## Programmatic use

```python
from devtool import (
    git_status_table, git_branch_summary, git_log_summary,
    scan_unused, find_todos, size_report,
    add_hooks, remove_hooks, list_hooks,
    release_bump, read_version,
    wizard_project,
)

# Git
print(git_status_table())
branches = git_branch_summary()
commits = git_log_summary(n=5)

# Scanners
todos = find_todos()
unused = scan_unused()
sizes = size_report(top_n=10)

# Hooks
add_hooks(["pre-commit", "commit-msg"])

# Release
v = release_bump(level="patch")

# Wizard
wizard_project(template="python-cli", name="mytool", noninteractive=True)
```

## Project structure

```
devtool/
├── __init__.py      # Public API exports
├── cli.py           # Click CLI entry point
├── hooks.py         # Git hook installation (pre-commit, pre-push, commit-msg)
├── wizard.py        # Interactive project scaffolding templates
├── githelpers.py    # Git status, branches, log — formatted output
├── scan.py          # TODO scanner, unused file detector, size reporter
└── bump.py          # Version bumping and changelog helpers
```

## Requirements

- Python 3.9+
- Click 8.0+ (CLI framework)

```bash
pip install click
```

## License

MIT License — see [LICENSE](LICENSE).
