"""Command-line entry point for devtool."""

import argparse
import json

from .bump import release_bump
from .githelpers import git_branch_summary, git_log_summary, git_status_table
from .hooks import add_hooks, list_hooks, remove_hooks
from .scan import find_todos, scan_unused, size_report
from .wizard import wizard_project


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="devtool")
    sub = parser.add_subparsers(dest="command", required=True)

    hooks = sub.add_parser("hooks")
    hooks.add_argument("action", choices=["install", "remove", "list"])

    scan = sub.add_parser("scan")
    scan.add_argument("kind", choices=["todos", "unused", "size"])

    git = sub.add_parser("git")
    git.add_argument("action", choices=["status", "branches", "log"])

    project = sub.add_parser("project")
    project.add_argument("action", choices=["create"])
    project.add_argument("--template", default="python-cli")
    project.add_argument("--name", required=True)

    release = sub.add_parser("release")
    release.add_argument("action", choices=["bump"])
    release.add_argument("--level", choices=["major", "minor", "patch"], default="patch")

    args = parser.parse_args(argv)
    if args.command == "hooks":
        result = {"install": add_hooks, "remove": remove_hooks, "list": list_hooks}[args.action]()
        print(json.dumps(result, indent=2, default=str))
    elif args.command == "scan":
        result = {"todos": find_todos, "unused": scan_unused, "size": size_report}[args.kind]()
        for item in result:
            print(item)
    elif args.command == "git":
        if args.action == "status":
            print(git_status_table())
        else:
            result = git_branch_summary() if args.action == "branches" else git_log_summary()
            print(json.dumps(result, indent=2, default=str))
    elif args.command == "project":
        wizard_project(template=args.template, name=args.name, noninteractive=True)
    elif args.command == "release":
        print(release_bump(level=args.level))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
