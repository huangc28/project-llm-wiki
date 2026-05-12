#!/usr/bin/env python3
import argparse
import pathlib
import subprocess
import sys
import textwrap


VERSION = "0.1.0-foundation"
WIKI_ROOT = pathlib.Path(".llm-wiki")
REQUIRED_DIRECTORIES = tuple(
    pathlib.Path(path)
    for path in (
        ".llm-wiki",
        ".llm-wiki/raw",
        ".llm-wiki/raw/curated",
        ".llm-wiki/architecture",
        ".llm-wiki/domain",
        ".llm-wiki/decisions",
        ".llm-wiki/operations",
        ".llm-wiki/features",
        ".llm-wiki/summaries",
    )
)
REQUIRED_FILES = tuple(
    pathlib.Path(path)
    for path in (
        ".llm-wiki/README.md",
        ".llm-wiki/AGENTS.md",
        ".llm-wiki/index.md",
        ".llm-wiki/log.md",
        ".llm-wiki/raw/README.md",
        ".llm-wiki/raw/curated/README.md",
        ".llm-wiki/features/ideas.md",
        ".llm-wiki/summaries/repo-overview.md",
        ".llm-wiki/architecture/.gitkeep",
        ".llm-wiki/domain/.gitkeep",
        ".llm-wiki/decisions/.gitkeep",
        ".llm-wiki/operations/.gitkeep",
    )
)
RECOMMENDED_INDEX_LINKS = ("[[features/ideas]]", "[[summaries/repo-overview]]")
GENERATED_FILES = {
    pathlib.Path(".llm-wiki/summaries/repo-overview.md"),
    pathlib.Path(".llm-wiki/architecture/.gitkeep"),
    pathlib.Path(".llm-wiki/domain/.gitkeep"),
    pathlib.Path(".llm-wiki/decisions/.gitkeep"),
    pathlib.Path(".llm-wiki/operations/.gitkeep"),
}


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


def template_root() -> pathlib.Path:
    return (
        pathlib.Path(__file__).resolve().parent.parent
        / "assets"
        / "templates"
        / "llm-wiki"
    )


def template_asset_for(relative_path: pathlib.Path) -> pathlib.Path | None:
    if relative_path in GENERATED_FILES:
        return None
    return template_root() / relative_path.relative_to(WIKI_ROOT)


def find_missing_template_assets() -> list[pathlib.Path]:
    missing: list[pathlib.Path] = []
    for relative_path in REQUIRED_FILES:
        asset = template_asset_for(relative_path)
        if asset is not None and not asset.is_file():
            missing.append(asset)
    return missing


def find_init_conflicts(git_root: pathlib.Path) -> list[str]:
    conflicts: list[str] = []
    for relative_path in REQUIRED_DIRECTORIES:
        path = git_root / relative_path
        if path.exists() and not path.is_dir():
            conflicts.append(
                f"{relative_path.as_posix()}: expected directory, found file"
            )
    for relative_path in REQUIRED_FILES:
        path = git_root / relative_path
        if path.exists() and not path.is_file():
            conflicts.append(
                f"{relative_path.as_posix()}: expected file, found directory"
            )
    return conflicts


def collect_missing_index_links(git_root: pathlib.Path) -> list[str]:
    index_path = git_root / ".llm-wiki" / "index.md"
    if not index_path.is_file():
        return []

    index_text = index_path.read_text(encoding="utf-8")
    return [link for link in RECOMMENDED_INDEX_LINKS if link not in index_text]


def collect_init_paths(
    git_root: pathlib.Path,
) -> tuple[list[pathlib.Path], list[pathlib.Path]]:
    create: list[pathlib.Path] = []
    skip: list[pathlib.Path] = []
    for relative_path in (*REQUIRED_DIRECTORIES, *REQUIRED_FILES):
        if (git_root / relative_path).exists():
            skip.append(relative_path)
        else:
            create.append(relative_path)
    return create, skip


def create_file_if_missing(path: pathlib.Path, content: str) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def build_generated_file_content(relative_path: pathlib.Path) -> str:
    if relative_path.name == ".gitkeep":
        return ""
    if relative_path == pathlib.Path(".llm-wiki/summaries/repo-overview.md"):
        return textwrap.dedent(
            """\
            # Repo Overview

            This page is created by project-wiki init and populated by the
            template content plan.

            Current repository files are authoritative when they disagree with this wiki.
            """
        )
    return ""


def read_init_file_content(relative_path: pathlib.Path) -> str:
    asset = template_asset_for(relative_path)
    if asset is None:
        return build_generated_file_content(relative_path)
    return asset.read_text(encoding="utf-8")


def apply_init_plan(
    git_root: pathlib.Path,
) -> tuple[list[pathlib.Path], list[pathlib.Path]]:
    created: list[pathlib.Path] = []
    skipped: list[pathlib.Path] = []

    for relative_path in REQUIRED_DIRECTORIES:
        path = git_root / relative_path
        if path.exists():
            skipped.append(relative_path)
            continue
        path.mkdir(parents=True, exist_ok=True)
        created.append(relative_path)

    for relative_path in REQUIRED_FILES:
        path = git_root / relative_path
        content = read_init_file_content(relative_path)
        if create_file_if_missing(path, content):
            created.append(relative_path)
        else:
            skipped.append(relative_path)

    return created, skipped


def print_path_section(heading: str, paths: list[pathlib.Path]) -> None:
    print(heading)
    if not paths:
        print("- (none)")
        return
    for path in paths:
        print(f"- {path.as_posix()}")


def print_text_section(heading: str, items: list[str]) -> None:
    print(heading)
    if not items:
        print("- (none)")
        return
    for item in items:
        print(f"- {item}")


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
    conflicts = find_init_conflicts(git_root)
    missing_index_links = collect_missing_index_links(git_root)
    if conflicts:
        print_text_section("Conflicts:", conflicts)
        return 2

    would_create, would_skip = collect_init_paths(git_root)
    if args.dry_run:
        print_path_section("Would create paths:", would_create)
        print_path_section("Would skip existing paths:", would_skip)
        if missing_index_links:
            print_text_section("Missing recommended index links:", missing_index_links)
        print("Next: review .llm-wiki/index.md")
        return 0

    missing_templates = find_missing_template_assets()
    if missing_templates:
        print_path_section("Template assets missing:", missing_templates)
        return 2

    created, skipped = apply_init_plan(git_root)
    print_path_section("Created paths:", created)
    print_path_section("Skipped existing paths:", skipped)
    if missing_index_links:
        print_text_section("Missing recommended index links:", missing_index_links)
    print("Next: review .llm-wiki/index.md")
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
