#!/usr/bin/env python3
import argparse
import pathlib
import subprocess
import sys
import textwrap


VERSION = "0.1.0-foundation"


def planned_command(name: str, phase: str) -> int:
    print(f"{name} is planned for {phase}")
    return 2


def resolve_git_root(cwd: pathlib.Path) -> tuple[pathlib.Path | None, str | None]:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0 and result.stdout.strip():
        return pathlib.Path(result.stdout.strip()), None
    message = result.stderr.strip() or "not inside a Git worktree"
    return None, message


def find_candidate_child_repos(cwd: pathlib.Path) -> list[pathlib.Path]:
    candidates: list[pathlib.Path] = []
    if not cwd.exists() or not cwd.is_dir():
        return candidates

    for child in sorted(cwd.iterdir()):
        if not child.is_dir():
            continue
        if (child / ".git").exists():
            candidates.append(child)
            continue
        root, _message = resolve_git_root(child)
        if root == child.resolve():
            candidates.append(child)
    return candidates


def run_init(args) -> int:
    cwd = pathlib.Path.cwd()
    git_root, _message = resolve_git_root(cwd)
    if git_root is None:
        print("No git repository found for current directory.")
        candidates = find_candidate_child_repos(cwd)
        if candidates:
            print("Candidate child repositories:")
            for candidate in candidates:
                print(f"- {candidate.relative_to(cwd)}")
        print("Next: cd into the intended repo before running project-wiki init")
        return 2

    print(f"Resolved git root: {git_root}")
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        prog="project-wiki",
        description="Repo-local .llm-wiki helper for Project LLM Wiki",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
            Phase 1 exposes the helper surface without mutating repositories.
            Later phases implement init, lint, query, and ingest behavior.
            """
        ),
    )
    parser.set_defaults(func=lambda _args: parser.print_help() or 0)

    subcommands = parser.add_subparsers(dest="command")

    version = subcommands.add_parser("version", help="print helper version")
    version.set_defaults(
        func=lambda _args: print(f"project-llm-wiki {VERSION}") or 0
    )

    init = subcommands.add_parser(
        "init", help="initialize .llm-wiki in the current Git repo"
    )
    init.add_argument(
        "--dry-run",
        action="store_true",
        help="report planned changes without writing files",
    )
    init.set_defaults(func=run_init)

    lint = subcommands.add_parser("lint", help="planned project-wiki-lint mode")
    lint.set_defaults(func=lambda _args: planned_command("project-wiki-lint", "Phase 3"))

    query = subcommands.add_parser("query", help="planned project-wiki-query mode")
    query.set_defaults(func=lambda _args: planned_command("project-wiki-query", "Phase 4"))

    ingest = subcommands.add_parser("ingest", help="planned project-wiki-ingest mode")
    ingest.set_defaults(func=lambda _args: planned_command("project-wiki-ingest", "Phase 4"))

    return parser


def main(argv: list[str] | None = None) -> int:
    _script_path = pathlib.Path(__file__)
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__": raise SystemExit(main())
