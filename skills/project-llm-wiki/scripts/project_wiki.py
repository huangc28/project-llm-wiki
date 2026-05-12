#!/usr/bin/env python3
import argparse
import pathlib
import sys
import textwrap


VERSION = "0.1.0-foundation"


def planned_command(name: str, phase: str) -> int:
    print(f"{name} is planned for {phase}")
    return 2


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

    init = subcommands.add_parser("init", help="planned project-wiki-init mode")
    init.set_defaults(func=lambda _args: planned_command("project-wiki-init", "Phase 2"))

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
