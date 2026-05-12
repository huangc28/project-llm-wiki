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
TEMPLATE_FILES = tuple(
    relative_path
    for relative_path in REQUIRED_FILES
    if relative_path not in GENERATED_FILES
)


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
    return pathlib.Path(__file__).resolve().parents[1] / "assets" / "templates" / "llm-wiki"


def load_template_contents() -> tuple[dict[str, str], list[str]]:
    root = template_root()
    contents: dict[str, str] = {}
    missing: list[str] = []
    for target_path in TEMPLATE_FILES:
        template_relative_path = target_path.relative_to(WIKI_ROOT)
        template_path = root / template_relative_path
        if template_path.is_file():
            contents[target_path.as_posix()] = template_path.read_text(
                encoding="utf-8"
            )
        else:
            missing.append(template_relative_path.as_posix())
    return contents, missing


def format_source_status(sources: list[str]) -> str:
    return ", ".join(sources) if sources else "none"


def build_repo_overview(repo_root: pathlib.Path) -> tuple[str, list[str], list[str]]:
    found: list[str] = []
    skipped: list[str] = []
    for source_name in ("README.md", "AGENTS.md"):
        if (repo_root / source_name).is_file():
            found.append(source_name)
        else:
            skipped.append(source_name)

    content = "\n".join(
        [
            "# Repo Overview",
            "",
            "This page was seeded during project-wiki init.",
            "",
            f"Sources found: {format_source_status(found)}",
            f"Sources skipped: {format_source_status(skipped)}",
            "",
            "Current repository files are authoritative when they disagree with this wiki.",
            "",
        ]
    )
    return content, found, skipped


def build_init_file_contents(
    repo_root: pathlib.Path, template_contents: dict[str, str]
) -> tuple[dict[str, str], list[str], list[str]]:
    repo_overview, found_sources, skipped_sources = build_repo_overview(repo_root)
    contents = dict(template_contents)
    contents[".llm-wiki/summaries/repo-overview.md"] = repo_overview
    contents[".llm-wiki/architecture/.gitkeep"] = ""
    contents[".llm-wiki/domain/.gitkeep"] = ""
    contents[".llm-wiki/decisions/.gitkeep"] = ""
    contents[".llm-wiki/operations/.gitkeep"] = ""
    return contents, found_sources, skipped_sources


def path_is_under(path: pathlib.Path, root: pathlib.Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve())
    except ValueError:
        return False
    return True


def find_init_conflicts(git_root: pathlib.Path) -> list[str]:
    conflicts: list[str] = []
    for relative_path in REQUIRED_DIRECTORIES:
        path = git_root / relative_path
        if path.is_symlink():
            conflicts.append(
                f"{relative_path.as_posix()}: expected real directory, found symlink"
            )
        elif path.exists() and not path.is_dir():
            conflicts.append(
                f"{relative_path.as_posix()}: expected directory, found file"
            )
        elif path.exists() and not path_is_under(path, git_root):
            conflicts.append(f"{relative_path.as_posix()}: resolves outside git root")
    for relative_path in REQUIRED_FILES:
        path = git_root / relative_path
        if path.is_symlink():
            conflicts.append(
                f"{relative_path.as_posix()}: expected real file, found symlink"
            )
        elif path.exists() and not path.is_file():
            conflicts.append(
                f"{relative_path.as_posix()}: expected file, found directory"
            )
        elif path.exists() and not path_is_under(path, git_root):
            conflicts.append(f"{relative_path.as_posix()}: resolves outside git root")
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


def apply_init_plan(
    git_root: pathlib.Path, file_contents: dict[str, str]
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
        content = file_contents[relative_path.as_posix()]
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


def print_source_status(found: list[str], skipped: list[str]) -> None:
    print(f"Sources found: {format_source_status(found)}")
    print(f"Skipped sources: {format_source_status(skipped)}")


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

    template_contents, missing_templates = load_template_contents()
    file_contents, found_sources, skipped_sources = build_init_file_contents(
        git_root, template_contents
    )
    would_create, would_skip = collect_init_paths(git_root)
    if args.dry_run:
        print_path_section("Would create paths:", would_create)
        print_path_section("Would skip existing paths:", would_skip)
        print_source_status(found_sources, skipped_sources)
        if missing_index_links:
            print_text_section("Missing recommended index links:", missing_index_links)
        if conflicts:
            print_text_section("Conflicts:", conflicts)
            return 2
        print("Next: review .llm-wiki/index.md")
        return 0

    if conflicts:
        print_text_section("Conflicts:", conflicts)
        return 2

    if missing_templates:
        print_text_section("Template assets missing:", missing_templates)
        return 2

    created, skipped = apply_init_plan(git_root, file_contents)
    print_path_section("Created paths:", created)
    print_path_section("Skipped existing paths:", skipped)
    print_source_status(found_sources, skipped_sources)
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
