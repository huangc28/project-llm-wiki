#!/usr/bin/env python3
import argparse
import json
import pathlib
import re
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
WIKILINK_PATTERN = re.compile(r"\[\[([^\[\]\n]+)\]\]")
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


def repo_relative_path(path: pathlib.Path | str, git_root: pathlib.Path) -> str:
    if isinstance(path, pathlib.Path):
        try:
            return path.relative_to(git_root).as_posix()
        except ValueError:
            return path.as_posix()
    return str(path)


def make_finding(
    severity: str,
    code: str,
    path: pathlib.Path | str,
    message: str,
    remediation: str,
) -> dict[str, str]:
    return {
        "severity": severity,
        "code": code,
        "path": path.as_posix() if isinstance(path, pathlib.Path) else path,
        "message": message,
        "remediation": remediation,
    }


def collect_wiki_files(git_root: pathlib.Path) -> list[pathlib.Path]:
    wiki_root = git_root / WIKI_ROOT
    files: list[pathlib.Path] = []
    pending = [wiki_root]

    while pending:
        current = pending.pop()
        try:
            entries = sorted(current.iterdir(), key=lambda path: path.as_posix())
        except OSError:
            continue
        for entry in entries:
            if entry.is_symlink() or not path_is_under(entry, wiki_root):
                continue
            if entry.is_dir():
                pending.append(entry)
            elif entry.is_file():
                files.append(entry)

    return sorted(files, key=lambda path: path.relative_to(git_root).as_posix())


def collect_markdown_files(git_root: pathlib.Path) -> list[pathlib.Path]:
    return [path for path in collect_wiki_files(git_root) if path.suffix == ".md"]


def collect_lint_files(git_root: pathlib.Path) -> list[pathlib.Path]:
    return collect_markdown_files(git_root)


def read_wiki_text(
    path: pathlib.Path, git_root: pathlib.Path
) -> tuple[str | None, dict[str, str] | None]:
    relative_path = repo_relative_path(path, git_root)
    try:
        return path.read_text(encoding="utf-8"), None
    except (OSError, UnicodeDecodeError):
        return None, make_finding(
            "error",
            "unreadable_wiki_file",
            relative_path,
            "Wiki file could not be read as UTF-8 text.",
            "Fix file permissions or replace the file with readable UTF-8 text before running project-wiki lint.",
        )


def extract_wikilinks(markdown_text: str) -> list[str]:
    return [match.group(1).strip() for match in WIKILINK_PATTERN.finditer(markdown_text)]


def normalize_wikilink_target(raw_target: str) -> str:
    target = raw_target.split("|", 1)[0].split("#", 1)[0].strip()
    if not target:
        return ""
    pure_target = pathlib.PurePosixPath(target)
    if pure_target.suffix:
        return pure_target.as_posix()
    return f"{pure_target.as_posix()}.md"


def wikilink_target_error(raw_target: str, normalized_target: str) -> str | None:
    if not normalized_target:
        return "empty target"
    target = pathlib.PurePosixPath(normalized_target)
    if target.is_absolute() or ".." in target.parts:
        return "target must stay inside .llm-wiki"
    return None


def check_broken_wikilinks(
    git_root: pathlib.Path, markdown_files: list[pathlib.Path]
) -> list[dict[str, str]]:
    wiki_root = git_root / WIKI_ROOT
    findings: list[dict[str, str]] = []

    for markdown_file in markdown_files:
        relative_path = repo_relative_path(markdown_file, git_root)
        markdown_text, read_error = read_wiki_text(markdown_file, git_root)
        if read_error is not None:
            findings.append(read_error)
            continue
        assert markdown_text is not None
        for raw_target in extract_wikilinks(markdown_text):
            normalized_target = normalize_wikilink_target(raw_target)
            target_error = wikilink_target_error(raw_target, normalized_target)
            target_path = wiki_root / pathlib.Path(normalized_target)
            if target_error is None and not path_is_under(target_path, wiki_root):
                target_error = "target must stay inside .llm-wiki"
            if (
                target_error is None
                and target_path.is_file()
                and not target_path.is_symlink()
            ):
                continue

            if target_error is None:
                message = (
                    f"Wikilink [[{raw_target}]] points to missing page "
                    f"{WIKI_ROOT / pathlib.Path(normalized_target)}."
                )
                remediation = (
                    f"Create {(WIKI_ROOT / pathlib.Path(normalized_target)).as_posix()} "
                    f"or update the wikilink in {relative_path}."
                )
            else:
                message = f"Wikilink [[{raw_target}]] is invalid: {target_error}."
                remediation = (
                    "Use a wiki-root-relative target that stays inside .llm-wiki, "
                    "for example [[features/ideas]]."
                )
            findings.append(
                make_finding(
                    "error",
                    "broken_wikilink",
                    relative_path,
                    message,
                    remediation,
                )
            )

    return findings


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


def collect_missing_index_links(git_root: pathlib.Path) -> tuple[list[str], str | None]:
    index_path = git_root / ".llm-wiki" / "index.md"
    if not index_path.is_file():
        return [], None

    try:
        index_text = index_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [], ".llm-wiki/index.md: expected UTF-8 markdown, could not read"
    return [link for link in RECOMMENDED_INDEX_LINKS if link not in index_text], None


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


def sort_findings(findings: list[dict[str, str]]) -> list[dict[str, str]]:
    return sorted(
        findings,
        key=lambda finding: (
            finding["severity"] != "error",
            finding["path"],
            finding["code"],
            finding["message"],
        ),
    )


def render_findings(findings: list[dict[str, str]], as_json: bool) -> None:
    if as_json:
        print(json.dumps({"findings": findings}, indent=2, sort_keys=True))
        return

    if not findings:
        print("No issues found in .llm-wiki/")
        return

    print("Lint findings:")
    for finding in findings:
        print("-")
        for key in ("severity", "code", "path", "message", "remediation"):
            print(f"  {key}: {finding[key]}")


def run_lint(args) -> int:
    cwd = pathlib.Path.cwd()
    git_root, _message = resolve_git_root(cwd)
    if git_root is None:
        print("No git repository found for current directory.")
        return 2

    wiki_root = git_root / WIKI_ROOT
    if (
        not wiki_root.exists()
        or not wiki_root.is_dir()
        or wiki_root.is_symlink()
        or not path_is_under(wiki_root, git_root)
    ):
        print("No .llm-wiki directory found in the resolved Git root.")
        return 2

    _wiki_files = collect_wiki_files(git_root)
    markdown_files = collect_markdown_files(git_root)
    findings = sort_findings(check_broken_wikilinks(git_root, markdown_files))
    render_findings(findings, args.json)
    return 1 if any(finding["severity"] == "error" for finding in findings) else 0


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
    template_contents, missing_templates = load_template_contents()
    file_contents, found_sources, skipped_sources = build_init_file_contents(
        git_root, template_contents
    )
    would_create, would_skip = collect_init_paths(git_root)
    if args.dry_run:
        print_path_section("Would create paths:", would_create)
        print_path_section("Would skip existing paths:", would_skip)
        print_source_status(found_sources, skipped_sources)
        if conflicts:
            print_text_section("Conflicts:", conflicts)
            return 2
        if missing_templates:
            print_text_section("Template assets missing:", missing_templates)
            return 2
        missing_index_links, index_read_error = collect_missing_index_links(git_root)
        if index_read_error:
            print_text_section("Conflicts:", [index_read_error])
            return 2
        if missing_index_links:
            print_text_section("Missing recommended index links:", missing_index_links)
        print("Next: review .llm-wiki/index.md")
        return 0

    if conflicts:
        print_text_section("Conflicts:", conflicts)
        return 2

    if missing_templates:
        print_text_section("Template assets missing:", missing_templates)
        return 2

    missing_index_links, index_read_error = collect_missing_index_links(git_root)
    if index_read_error:
        print_text_section("Conflicts:", [index_read_error])
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
            project-wiki init creates a .llm-wiki skeleton in the current Git root.
            Use project-wiki init --dry-run to preview changes without writing files.
            query and ingest remain planned for later phases.
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

    lint = subcommands.add_parser("lint", help="lint .llm-wiki structure")
    lint.add_argument("--json", action="store_true", help="render lint findings as JSON")
    lint.set_defaults(func=run_lint)

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
