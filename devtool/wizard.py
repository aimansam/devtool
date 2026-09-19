"""Interactive project scaffolding wizard."""

from __future__ import annotations
import os
import subprocess
import sys
from pathlib import Path
from typing import Callable

TEMPLATES: dict[str, dict] = {
    "python-cli": {
        "description": "Python CLI tool with argparse, tests, README",
        "files": {
            "pyproject.toml": """[project]
name = "{{name}}"
version = "0.1.0"
description = "{{description}}"
requires-python = ">=3.9"
dependencies = []

[project.scripts]
{{name}} = "{{module}}.main:main"

[tool.pytest.ini_options]
testpaths = ["tests"]
""",
            "README.md": """# {{name}}

{{description}}

## Install

```bash
pip install -e .
```

## Usage

```bash
{{name}} --help
```
""",
            "tests/__init__.py": "",
            "tests/test_main.py": """from {{module}}.main import main

def test_main_help():
    result = main(["--help"])
    assert result == 0
""",
            "{{module}}/__init__.py": "",
            "{{module}}/main.py": """import argparse
import sys

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="{{name}}", description="{{description}}")
    parser.parse_args(argv)
    print("Hello from {{name}}!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
""",
        },
    },
    "python-lib": {
        "description": "Python library with tests, typed code, and docs",
        "files": {
            "pyproject.toml": """[project]
name = "{{name}}"
version = "0.1.0"
description = "{{description}}"
requires-python = ">=3.9"
dependencies = []

[project.optional-dependencies]
dev = ["pytest", "mypy", "black", "ruff"]

[tool.pytest.ini_options]
testpaths = ["tests"]
""",
            "README.md": """# {{name}}

{{description}}

## Install

```bash
pip install -e ".[dev]"
```

## Test

```bash
pytest
```

## Type check

```bash
mypy src/
```
""",
            "src/{{module}}/__init__.py": "",
            "tests/__init__.py": "",
            "tests/test_{{module}}.py": """from {{module}} import __version__

def test_version():
    assert __version__
""",
        },
    },
}


def _prompt(msg: str, default: str = "") -> str:
    prompt = f"{msg}"
    if default:
        prompt += f" [{default}]"
    prompt += ": "
    while True:
        try:
            val = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            sys.exit(0)
        if val:
            return val
        if default:
            return default


def wizard_project(cwd: Path | str | None = None, noninteractive: bool = False,
                   template: str = "python-cli", name: str = "", description: str = "") -> Path | None:
    """Scaffold a new project from a template.

    In noninteractive mode, requires name and description.
    """
    cwd = Path(cwd or Path.cwd())
    tmpl = TEMPLATES.get(template)
    if tmpl is None:
        print(f"Unknown template: {template}")
        print(f"Available: {list(TEMPLATES.keys())}")
        return None

    if noninteractive:
        if not name:
            print("Error: --name is required in noninteractive mode")
            return None
        desc = description or tmpl["description"]
    else:
        print(f"Template: {template}")
        print(f"Description: {tmpl['description']}")
        name = _prompt("Project name", name or cwd.name)
        desc = _prompt("Short description", desc or "")

    if not name or not name.replace("-", "").replace("_", "").isidentifier():
        print(f"Invalid project name: {name}")
        return None

    module = name.replace("-", "_").replace(" ", "_")

    out_dir = cwd / name
    if out_dir.exists():
        print(f"Directory already exists: {out_dir}")
        return None
    out_dir.mkdir(parents=True, exist_ok=True)

    for fname, content in tmpl["files"].items():
        rendered = content.replace("{{name}}", name).replace("{{module}}", module).replace("{{description}}", desc)
        fpath = out_dir / fname
        fpath.parent.mkdir(parents=True, exist_ok=True)
        fpath.write_text(rendered)
        print(f"  + {fname}")

    print(f"\nProject created: {out_dir}")
    print(f"  cd {name} && pip install -e .")
    return out_dir
