#!/usr/bin/env python3
import argparse
import datetime
import json
import os
import pathlib
import re
import subprocess
import sys
import textwrap


VERSION = "0.1.0-foundation"
WIKI_ROOT = pathlib.Path(".llm-wiki")
ROOT_AGENTS_RELATIVE_PATH = pathlib.Path("AGENTS.md")
ROOT_AGENTS_START_MARKER = "<!-- PROJECT-LLM-WIKI:START -->"
ROOT_AGENTS_END_MARKER = "<!-- PROJECT-LLM-WIKI:END -->"
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
INSTALL_SKILL_NAMES = (
    "project-llm-wiki",
    "project-wiki-init",
    "project-wiki-lint",
    "project-wiki-query",
    "project-wiki-ingest",
)
RECOMMENDED_INDEX_LINKS = ("[[features/ideas]]", "[[summaries/repo-overview]]")
WIKILINK_PATTERN = re.compile(r"\[\[([^\[\]\n]+)\]\]")
INLINE_CODE_SPAN_PATTERN = re.compile(r"(?<!`)`([^`\n]+)`(?!`)")
PRIVATE_KEY_PATTERN = re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")
CREDENTIAL_URL_PATTERN = re.compile(
    r"\b[A-Za-z][A-Za-z0-9+.-]*://[^\s:/@]+:[^\s/@]+@[^\s/@]+"
)
SECRET_KEY_NAME_PATTERN = (
    r"(?:[a-z0-9]+[_-])*"
    r"(?:"
    r"password|passwd|pwd|pass|pgpassword|token|bearer|api[_-]?key|access[_-]?key|"
    r"private[_-]?key|secret(?:[_-]?(?:key|access[_-]?key))?"
    r")"
    r"(?:[_-][a-z0-9]+)*"
)
KEY_VALUE_SECRET_PATTERN = re.compile(
    rf"(?i)\b{SECRET_KEY_NAME_PATTERN}\b\s*[:=]\s*['\"]?([^'\"\s#]+)"
)
KNOWN_TOKEN_PATTERN = re.compile(
    r"\b(?:"
    r"sk-[A-Za-z0-9_-]{20,}|"
    r"github_pat_[A-Za-z0-9_]{20,}|"
    r"gh[pousr]_[A-Za-z0-9_]{20,}|"
    r"AKIA[0-9A-Z]{16}"
    r")\b"
)
UPDATED_FRONTMATTER_PATTERN = re.compile(r"updated:\s*(\d{4}-\d{2}-\d{2})\s*")
LINE_REFERENCE_PATTERN = re.compile(
    r"^(?P<path>.+):(?P<line>[1-9][0-9]*)(?:-[1-9][0-9]*)?$"
)
RAW_SIZE_WARNING_BYTES = 100 * 1024
STALE_AFTER_DAYS = 90
LOG_TITLE_MAX_CHARS = 120
LOG_INSIGHT_MAX_CHARS = 240
SHELL_INTERPOLATION_CHARS = frozenset("$`{}()<>|;&")
INDEX_COVERAGE_DIRECTORIES = (
    "architecture",
    "domain",
    "decisions",
    "operations",
    "features",
    "summaries",
)
INDEX_COVERAGE_POLICY_PAGES = (
    pathlib.Path("raw/README.md"),
    pathlib.Path("raw/curated/README.md"),
)
INDEX_COVERAGE_EXCLUDED_PAGES = {
    pathlib.Path("README.md"),
    pathlib.Path("AGENTS.md"),
    pathlib.Path("index.md"),
    pathlib.Path("log.md"),
}
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
FINDING_FIELDS = ("severity", "code", "path", "message", "remediation")
TEXT_FINDING_LABELS = (
    ("severity", "severity:"),
    ("code", "code:"),
    ("path", "path:"),
    ("message", "message:"),
    ("remediation", "remediation:"),
)
SEVERITY_SORT_RANK = {"error": 0, "warning": 1}
PLACEHOLDER_SECRET_VALUES = {
    "<redacted>",
    "changeme",
    "example",
    "placeholder",
    "redacted",
    "replace-me",
    "your-token",
    "your_token",
}
DISALLOWED_RAW_PHRASES = (
    "active task state",
    "database dump",
    "execution checkpoint",
    "full log",
    "full logs",
    "full transcript",
    "full transcripts",
    "private customer data",
    "private data",
    "unreviewed dump",
)
VIDEO_URL_MARKERS = ("youtube.com", "youtu.be", "vimeo.com")


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


def package_skills_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[2]


def default_install_target() -> pathlib.Path:
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        return pathlib.Path(codex_home).expanduser() / "skills"
    return pathlib.Path.home() / ".codex" / "skills"


def install_sources() -> dict[str, pathlib.Path]:
    root = package_skills_root()
    return {name: root / name for name in INSTALL_SKILL_NAMES}


def collect_install_plan(
    target_dir: pathlib.Path, force: bool, uninstall: bool
) -> tuple[list[tuple[str, str, pathlib.Path, pathlib.Path]], list[str]]:
    actions: list[tuple[str, str, pathlib.Path, pathlib.Path]] = []
    conflicts: list[str] = []
    sources = install_sources()
    source_root = package_skills_root()

    for name, source in sources.items():
        target = target_dir / name
        if not source.is_dir():
            conflicts.append(f"{name}: source skill directory is missing at {source}")
            continue

        if uninstall:
            if target.is_symlink() and path_is_under(
                target.resolve(strict=False), source_root
            ):
                actions.append(("remove", name, source, target))
            elif target.is_symlink():
                actions.append(("preserve", name, source, target))
            elif target.exists():
                actions.append(("preserve", name, source, target))
            else:
                actions.append(("absent", name, source, target))
            continue

        if target.is_symlink():
            if target.resolve(strict=False) == source.resolve():
                actions.append(("skip", name, source, target))
            elif force:
                actions.append(("replace", name, source, target))
            else:
                conflicts.append(
                    f"{name}: existing symlink points to {target.resolve(strict=False)}; "
                    "rerun with --force to replace it"
                )
            continue

        if target.exists():
            conflicts.append(
                f"{name}: {target} already exists and is not a symlink; move it first"
            )
            continue

        actions.append(("create", name, source, target))

    return actions, conflicts


def print_install_plan(
    actions: list[tuple[str, str, pathlib.Path, pathlib.Path]],
    dry_run: bool,
    uninstall: bool,
) -> None:
    headings = {
        "create": "Would install skills:" if dry_run else "Installed skills:",
        "replace": "Would replace symlinks:" if dry_run else "Replaced symlinks:",
        "skip": "Skipped existing skills:",
        "remove": "Would remove skills:" if dry_run else "Removed skills:",
        "preserve": "Preserved foreign entries:",
        "absent": "Already absent:",
    }
    order = ("create", "replace", "skip", "remove", "preserve", "absent")
    if uninstall:
        order = ("remove", "preserve", "absent")

    for action in order:
        names = [
            name
            for current_action, name, _source, _target in actions
            if current_action == action
        ]
        if names:
            print_text_section(headings[action], names)


def apply_install_plan(
    target_dir: pathlib.Path, actions: list[tuple[str, str, pathlib.Path, pathlib.Path]]
) -> None:
    needs_target_dir = any(
        action in {"create", "replace"} for action, _name, _source, _target in actions
    )
    if needs_target_dir:
        target_dir.mkdir(exist_ok=True)

    for action, _name, source, target in actions:
        if action == "create":
            target.symlink_to(source, target_is_directory=True)
        elif action == "replace":
            target.unlink()
            target.symlink_to(source, target_is_directory=True)
        elif action == "remove":
            target.unlink()


def path_has_symlink_component(root: pathlib.Path, relative_path: pathlib.Path) -> bool:
    current = root
    for part in relative_path.parts:
        current = current / part
        if current.is_symlink():
            return True
    return False


def wiki_write_file(
    git_root: pathlib.Path, relative_path: pathlib.Path
) -> tuple[pathlib.Path | None, str | None]:
    wiki_root = git_root / WIKI_ROOT
    path = wiki_root / relative_path
    if relative_path.is_absolute() or ".." in relative_path.parts:
        return None, f"{WIKI_ROOT / relative_path}: write target must stay inside .llm-wiki."
    if path_has_symlink_component(wiki_root, relative_path) or not path_is_under(
        path, wiki_root
    ):
        return (
            None,
            f"{WIKI_ROOT / relative_path}: write target must stay inside .llm-wiki and must not be a symlink.",
        )
    if path.exists() and not path.is_file():
        return None, f"{WIKI_ROOT / relative_path}: expected file."
    return path, None


def wiki_write_directory(
    git_root: pathlib.Path, relative_path: pathlib.Path
) -> tuple[pathlib.Path | None, str | None]:
    wiki_root = git_root / WIKI_ROOT
    path = wiki_root / relative_path
    if relative_path.is_absolute() or ".." in relative_path.parts:
        return None, f"{WIKI_ROOT / relative_path}: write target must stay inside .llm-wiki."
    if path_has_symlink_component(wiki_root, relative_path) or not path_is_under(
        path, wiki_root
    ):
        return (
            None,
            f"{WIKI_ROOT / relative_path}: write target must stay inside .llm-wiki and must not be a symlink.",
        )
    if path.exists() and not path.is_dir():
        return None, f"{WIKI_ROOT / relative_path}: expected directory."
    return path, None


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


def collect_wiki_files(
    git_root: pathlib.Path,
) -> tuple[list[pathlib.Path], list[dict[str, str]]]:
    wiki_root = git_root / WIKI_ROOT
    files: list[pathlib.Path] = []
    findings: list[dict[str, str]] = []
    pending = [wiki_root]

    while pending:
        current = pending.pop()
        try:
            entries = sorted(current.iterdir(), key=lambda path: path.as_posix())
        except OSError:
            findings.append(
                make_finding(
                    "error",
                    "unreadable_wiki_directory",
                    repo_relative_path(current, git_root),
                    "Wiki directory could not be listed during lint.",
                    "Fix directory permissions or remove the unreadable directory before running project-wiki lint.",
                )
            )
            continue
        for entry in entries:
            if entry.is_symlink() or not path_is_under(entry, wiki_root):
                continue
            if entry.is_dir():
                pending.append(entry)
            elif entry.is_file():
                files.append(entry)

    return sorted(files, key=lambda path: path.relative_to(git_root).as_posix()), findings


def collect_markdown_files(git_root: pathlib.Path) -> list[pathlib.Path]:
    wiki_files, _findings = collect_wiki_files(git_root)
    return [path for path in wiki_files if path.suffix == ".md"]


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
    if pure_target.suffix == ".md":
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


def index_link_for_page(wiki_relative_path: pathlib.Path) -> str:
    return f"[[{wiki_relative_path.with_suffix('').as_posix()}]]"


def is_index_coverage_candidate(
    markdown_file: pathlib.Path, git_root: pathlib.Path
) -> bool:
    wiki_root = git_root / WIKI_ROOT
    try:
        wiki_relative_path = markdown_file.relative_to(wiki_root)
    except ValueError:
        return False

    if wiki_relative_path.name == ".gitkeep":
        return False
    if wiki_relative_path in INDEX_COVERAGE_EXCLUDED_PAGES:
        return False
    if wiki_relative_path in INDEX_COVERAGE_POLICY_PAGES:
        return True
    if (
        len(wiki_relative_path.parts) > 1
        and wiki_relative_path.parts[0] in INDEX_COVERAGE_DIRECTORIES
    ):
        return True
    return False


def check_index_coverage(
    git_root: pathlib.Path, markdown_files: list[pathlib.Path]
) -> list[dict[str, str]]:
    wiki_root = git_root / WIKI_ROOT
    index_path = wiki_root / "index.md"
    index_text, read_error = read_wiki_text(index_path, git_root)
    if read_error is not None:
        return [read_error]
    assert index_text is not None

    linked_pages: set[str] = set()
    for raw_target in extract_wikilinks(index_text):
        normalized_target = normalize_wikilink_target(raw_target)
        if wikilink_target_error(raw_target, normalized_target) is None:
            linked_pages.add(normalized_target)

    findings: list[dict[str, str]] = []
    for markdown_file in markdown_files:
        if not is_index_coverage_candidate(markdown_file, git_root):
            continue
        wiki_relative_path = markdown_file.relative_to(wiki_root)
        normalized_path = wiki_relative_path.as_posix()
        if normalized_path in linked_pages:
            continue
        link = index_link_for_page(wiki_relative_path)
        findings.append(
            make_finding(
                "warning",
                "missing_index_entry",
                repo_relative_path(markdown_file, git_root),
                "Main wiki page is not linked from .llm-wiki/index.md.",
                (
                    f"Add {link} to .llm-wiki/index.md when this page is "
                    "durable main wiki knowledge."
                ),
            )
        )
    return findings


def check_raw_file_sizes(
    git_root: pathlib.Path, wiki_files: list[pathlib.Path]
) -> list[dict[str, str]]:
    wiki_root = git_root / WIKI_ROOT
    findings: list[dict[str, str]] = []
    for wiki_file in wiki_files:
        wiki_relative_path = wiki_file.relative_to(wiki_root)
        if not wiki_relative_path.parts or wiki_relative_path.parts[0] != "raw":
            continue
        try:
            size = wiki_file.stat().st_size
        except OSError:
            continue
        if size <= RAW_SIZE_WARNING_BYTES:
            continue
        findings.append(
            make_finding(
                "warning",
                "oversized_raw_file",
                repo_relative_path(wiki_file, git_root),
                f"Raw file is {size} bytes, larger than {RAW_SIZE_WARNING_BYTES} bytes.",
                "Replace large raw material with a curated excerpt or summarize it in a durable wiki page.",
            )
        )
    return findings


def is_placeholder_secret_value(value: str) -> bool:
    normalized = value.strip().strip("'\"").lower()
    return normalized in PLACEHOLDER_SECRET_VALUES or normalized.startswith(
        ("example_", "example-", "your_", "your-")
    )


def has_secret_like_content(text: str) -> bool:
    if PRIVATE_KEY_PATTERN.search(text) or CREDENTIAL_URL_PATTERN.search(text):
        return True
    if KNOWN_TOKEN_PATTERN.search(text):
        return True
    for match in KEY_VALUE_SECRET_PATTERN.finditer(text):
        if not is_placeholder_secret_value(match.group(1)):
            return True
    return False


def check_secret_like_content(
    git_root: pathlib.Path, wiki_files: list[pathlib.Path]
) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for wiki_file in wiki_files:
        relative_path = repo_relative_path(wiki_file, git_root)
        text, read_error = read_wiki_text(wiki_file, git_root)
        if read_error is not None:
            findings.append(read_error)
            continue
        assert text is not None
        if not has_secret_like_content(text):
            continue
        findings.append(
            make_finding(
                "warning",
                "secret_like_content",
                relative_path,
                "Wiki file contains high-confidence secret-looking material.",
                "Remove or redact the unsafe material before committing the wiki.",
            )
        )
    return findings


def parse_updated_frontmatter(markdown_text: str) -> datetime.date | None:
    lines = markdown_text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None

    frontmatter_lines: list[str] = []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        frontmatter_lines.append(line)
    else:
        return None

    for line in frontmatter_lines:
        match = UPDATED_FRONTMATTER_PATTERN.fullmatch(line.strip())
        if match is None:
            continue
        try:
            return datetime.date.fromisoformat(match.group(1))
        except ValueError:
            return None
    return None


def check_stale_pages(
    git_root: pathlib.Path, markdown_files: list[pathlib.Path]
) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    today = datetime.date.today()
    for markdown_file in markdown_files:
        relative_path = repo_relative_path(markdown_file, git_root)
        markdown_text, read_error = read_wiki_text(markdown_file, git_root)
        if read_error is not None:
            continue
        assert markdown_text is not None
        updated = parse_updated_frontmatter(markdown_text)
        if updated is None:
            continue
        if today - updated <= datetime.timedelta(days=STALE_AFTER_DAYS):
            continue
        findings.append(
            make_finding(
                "warning",
                "stale_page",
                relative_path,
                f"Wiki page updated date {updated.isoformat()} is older than {STALE_AFTER_DAYS} days.",
                "review the page against current repo files and update updated: only after validation.",
            )
        )
    return findings


def is_markdown_fence(line: str) -> bool:
    return markdown_fence_marker(line) is not None


def markdown_fence_marker(line: str) -> str | None:
    stripped = line.lstrip()
    if stripped.startswith("```"):
        return "```"
    if stripped.startswith("~~~"):
        return "~~~"
    return None


def extract_markdown_code_references(markdown_text: str) -> list[str]:
    references: list[str] = []
    active_fence_marker: str | None = None
    for line in markdown_text.splitlines():
        fence_marker = markdown_fence_marker(line)
        if active_fence_marker is not None:
            if fence_marker == active_fence_marker:
                active_fence_marker = None
                continue
            reference = line.strip()
            if reference:
                references.append(reference)
            continue
        if fence_marker is not None:
            active_fence_marker = fence_marker
            continue
        for match in INLINE_CODE_SPAN_PATTERN.finditer(line):
            reference = match.group(1).strip()
            if reference:
                references.append(reference)
    return references


def normalize_repo_path_candidate(reference: str) -> str | None:
    candidate = reference.strip()
    line_reference = LINE_REFERENCE_PATTERN.fullmatch(candidate)
    if line_reference is not None:
        candidate = line_reference.group("path")
    if candidate.startswith("./"):
        candidate = candidate[2:]
    if not candidate or "/" not in candidate:
        return None
    if candidate.endswith("/"):
        return None
    if any(character.isspace() for character in candidate):
        return None
    if candidate.startswith((".llm-wiki/", "../", "/", "~", "http://", "https://")):
        return None
    if any(character in candidate for character in SHELL_INTERPOLATION_CHARS):
        return None

    pure_path = pathlib.PurePosixPath(candidate)
    if pure_path.is_absolute() or ".." in pure_path.parts:
        return None
    return pure_path.as_posix()


def check_repo_path_drift(
    git_root: pathlib.Path, markdown_files: list[pathlib.Path]
) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for markdown_file in markdown_files:
        relative_path = repo_relative_path(markdown_file, git_root)
        markdown_text, read_error = read_wiki_text(markdown_file, git_root)
        if read_error is not None:
            continue
        assert markdown_text is not None

        seen_candidates: set[str] = set()
        for reference in extract_markdown_code_references(markdown_text):
            candidate = normalize_repo_path_candidate(reference)
            if candidate is None or candidate in seen_candidates:
                continue
            seen_candidates.add(candidate)
            candidate_path = git_root / pathlib.Path(candidate)
            if not path_is_under(candidate_path, git_root):
                continue
            if candidate_path.exists():
                continue
            findings.append(
                make_finding(
                    "warning",
                    "missing_repo_path",
                    relative_path,
                    f"Wiki reference points to missing repo path {candidate}.",
                    (
                        "Verify whether the wiki reference is stale, update the "
                        "wiki after checking current repo files, or remove the "
                        "reference if it is only an example."
                    ),
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


def root_agents_managed_section() -> str:
    return "\n".join(
        [
            ROOT_AGENTS_START_MARKER,
            "## Project LLM Wiki",
            "",
            "Before non-trivial architecture, debugging, product, onboarding, or cross-file implementation work, read `.llm-wiki/index.md` first, then only task-relevant linked pages.",
            "",
            "For simple typo fixes and narrow single-file edits, wiki lookup is not required.",
            "",
            "Current repository files are authoritative when they disagree with `.llm-wiki/`; report wiki drift when found.",
            "",
            "Update `.llm-wiki/` only after validated non-trivial work produces durable learning. Do not use `.llm-wiki/` for active task status.",
            ROOT_AGENTS_END_MARKER,
            "",
        ]
    )


def agents_append_separator(existing_bytes: bytes) -> bytes:
    if existing_bytes.endswith(b"\r\n"):
        return b"\r\n"
    if existing_bytes.endswith(b"\n"):
        return b"\n"
    return b"\n\n"


def build_agents_patch_plan(
    git_root: pathlib.Path, patch_agents: bool
) -> dict[str, object]:
    plan: dict[str, object] = {
        "enabled": patch_agents,
        "relative_path": ROOT_AGENTS_RELATIVE_PATH,
        "action": "skipped",
        "content": "",
        "content_bytes": b"",
        "conflicts": [],
    }
    if not patch_agents:
        return plan

    managed_section = root_agents_managed_section()
    managed_section_bytes = managed_section.encode("utf-8")
    plan["content"] = managed_section
    plan["content_bytes"] = managed_section_bytes
    agents_path = git_root / ROOT_AGENTS_RELATIVE_PATH

    if agents_path.is_symlink():
        plan["action"] = "conflict"
        plan["conflicts"] = ["AGENTS.md: expected real file, found symlink"]
        return plan
    if agents_path.exists() and not agents_path.is_file():
        plan["action"] = "conflict"
        plan["conflicts"] = ["AGENTS.md: expected file, found directory"]
        return plan
    if not path_is_under(agents_path, git_root):
        plan["action"] = "conflict"
        plan["conflicts"] = ["AGENTS.md: resolves outside git root"]
        return plan
    if not agents_path.exists():
        plan["action"] = "create"
        return plan

    try:
        existing_bytes = agents_path.read_bytes()
        existing_text = existing_bytes.decode("utf-8")
    except (OSError, UnicodeDecodeError):
        plan["action"] = "conflict"
        plan["conflicts"] = [
            "AGENTS.md: expected readable UTF-8, could not patch Project LLM Wiki section"
        ]
        return plan

    start_marker_bytes = ROOT_AGENTS_START_MARKER.encode("utf-8")
    end_marker_bytes = ROOT_AGENTS_END_MARKER.encode("utf-8")
    start_count = existing_bytes.count(start_marker_bytes)
    end_count = existing_bytes.count(end_marker_bytes)
    if start_count == 0 and end_count == 0:
        separator = agents_append_separator(existing_bytes)
        planned_bytes = existing_bytes + separator + managed_section_bytes
        plan["action"] = "append"
        plan["content"] = planned_bytes.decode("utf-8")
        plan["content_bytes"] = planned_bytes
        return plan
    if start_count > end_count:
        plan["action"] = "conflict"
        plan["conflicts"] = ["AGENTS.md: unmatched Project LLM Wiki start marker"]
        return plan
    if end_count > start_count:
        plan["action"] = "conflict"
        plan["conflicts"] = ["AGENTS.md: unmatched Project LLM Wiki end marker"]
        return plan
    if start_count > 1:
        plan["action"] = "conflict"
        plan["conflicts"] = ["AGENTS.md: multiple Project LLM Wiki marker pairs"]
        return plan

    start_index = existing_bytes.index(start_marker_bytes)
    end_index = existing_bytes.index(end_marker_bytes)
    if end_index < start_index:
        plan["action"] = "conflict"
        plan["conflicts"] = ["AGENTS.md: unmatched Project LLM Wiki end marker"]
        return plan

    end_index += len(end_marker_bytes)
    planned_bytes = (
        existing_bytes[:start_index]
        + managed_section.rstrip("\n").encode("utf-8")
        + existing_bytes[end_index:]
    )
    plan["content"] = planned_bytes.decode("utf-8")
    plan["content_bytes"] = planned_bytes
    plan["action"] = "unchanged" if planned_bytes == existing_bytes else "update"
    return plan


def print_agents_patch_plan(plan: dict[str, object]) -> None:
    action = plan["action"]
    if action == "skipped":
        print("Root AGENTS.md: skipped by --no-patch-agents")
        return
    if action == "create":
        print("Root AGENTS.md: would create")
    elif action == "append":
        print("Root AGENTS.md: would append managed section")
    elif action == "update":
        print("Root AGENTS.md: would update managed section")
    elif action == "unchanged":
        print("Root AGENTS.md: already up to date")
    elif action == "conflict":
        print("Root AGENTS.md: conflict")

    print("Managed AGENTS.md section:")
    print(root_agents_managed_section(), end="")


def apply_agents_patch_plan(git_root: pathlib.Path, plan: dict[str, object]) -> str:
    action = plan["action"]
    if action == "skipped":
        return "Root AGENTS.md: skipped by --no-patch-agents"
    if action == "unchanged":
        return "Root AGENTS.md: already up to date"
    if action not in {"create", "append", "update"}:
        return "Root AGENTS.md: already up to date"

    agents_path = git_root / ROOT_AGENTS_RELATIVE_PATH
    agents_path.write_bytes(bytes(plan["content_bytes"]))
    if action == "create":
        return "Root AGENTS.md: created"
    return "Root AGENTS.md: updated"


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
            SEVERITY_SORT_RANK.get(finding["severity"], 99),
            finding["path"],
            finding["code"],
            finding["message"],
        ),
    )


def render_text_findings(findings: list[dict[str, str]]) -> None:
    sorted_findings = sort_findings(findings)
    if not sorted_findings:
        print("No issues found in .llm-wiki/")
        return

    for index, finding in enumerate(sorted_findings):
        if index:
            print()
        for key, label in TEXT_FINDING_LABELS:
            print(f"{label} {finding[key]}")


def render_json_findings(findings: list[dict[str, str]]) -> None:
    sorted_findings = sort_findings(findings)
    print(json.dumps({"findings": sorted_findings}, indent=2, sort_keys=True))


def render_findings(findings: list[dict[str, str]], as_json: bool) -> None:
    if as_json:
        render_json_findings(findings)
    else:
        render_text_findings(findings)


def lint_exit_code(findings: list[dict[str, str]]) -> int:
    return 1 if any(finding["severity"] == "error" for finding in findings) else 0


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

    wiki_files, inventory_findings = collect_wiki_files(git_root)
    readable_wiki_files: list[pathlib.Path] = []
    read_error_findings: list[dict[str, str]] = []
    unreadable_wiki_files: set[pathlib.Path] = set()
    for wiki_file in wiki_files:
        _text, read_error = read_wiki_text(wiki_file, git_root)
        if read_error is not None:
            read_error_findings.append(read_error)
            unreadable_wiki_files.add(wiki_file)
        else:
            readable_wiki_files.append(wiki_file)
    markdown_files = [path for path in readable_wiki_files if path.suffix == ".md"]
    index_coverage_findings = []
    if wiki_root / "index.md" not in unreadable_wiki_files:
        index_coverage_findings = check_index_coverage(git_root, markdown_files)
    findings = [
        *inventory_findings,
        *read_error_findings,
        *check_broken_wikilinks(git_root, markdown_files),
        *index_coverage_findings,
        *check_raw_file_sizes(git_root, readable_wiki_files),
        *check_secret_like_content(git_root, readable_wiki_files),
        *check_stale_pages(git_root, markdown_files),
        *check_repo_path_drift(git_root, markdown_files),
    ]
    render_findings(findings, args.json)
    return lint_exit_code(findings)


def trim_summary_text(value: str, limit: int) -> str:
    summary = " ".join(value.split())
    if len(summary) <= limit:
        return summary
    truncated = summary[:limit].rsplit(" ", 1)[0].rstrip()
    return f"{truncated}..." if truncated else f"{summary[:limit].rstrip()}..."


def wikilink_from_normalized_target(normalized_target: str) -> str:
    return f"[[{pathlib.PurePosixPath(normalized_target).with_suffix('').as_posix()}]]"


def format_wikilink_page(page: str) -> str:
    raw_page = page.strip()
    if raw_page.startswith("[[") and raw_page.endswith("]]"):
        raw_page = raw_page[2:-2]
    normalized_target = normalize_wikilink_target(raw_page)
    target_error = wikilink_target_error(raw_page, normalized_target)
    if target_error is not None:
        raise ValueError(target_error)
    return wikilink_from_normalized_target(normalized_target)


def read_query_index(
    git_root: pathlib.Path,
) -> tuple[str | None, list[str], str | None]:
    wiki_root = git_root / WIKI_ROOT
    if (
        not wiki_root.exists()
        or not wiki_root.is_dir()
        or wiki_root.is_symlink()
        or not path_is_under(wiki_root, git_root)
    ):
        return None, [], "No .llm-wiki directory found in the resolved Git root."

    index_path = wiki_root / "index.md"
    if not index_path.is_file() or index_path.is_symlink():
        return None, [], "No .llm-wiki/index.md found in the resolved Git root."

    index_text, read_error = read_wiki_text(index_path, git_root)
    if read_error is not None:
        return None, [], read_error["message"]
    assert index_text is not None

    candidate_pages: list[str] = []
    seen_pages: set[str] = set()
    for raw_target in extract_wikilinks(index_text):
        normalized_target = normalize_wikilink_target(raw_target)
        if wikilink_target_error(raw_target, normalized_target) is not None:
            continue
        page = wikilink_from_normalized_target(normalized_target)
        if page not in seen_pages:
            seen_pages.add(page)
            candidate_pages.append(page)
    return index_text, candidate_pages, None


def build_query_packet(git_root: pathlib.Path, question: str) -> dict[str, object]:
    _index_text, candidate_pages, error = read_query_index(git_root)
    if error is not None:
        raise ValueError(error)
    return {
        "question": question,
        "index_path": ".llm-wiki/index.md",
        "candidate_pages": candidate_pages,
        "answer_contract": [
            "Read .llm-wiki/index.md first.",
            "Direct claims require [[wikilink]] citations.",
            "Put synthesis or inference under a labeled Inference section.",
        ],
        "not_covered_template": [
            "Say `.llm-wiki/` does not currently cover the topic.",
            "List pages consulted.",
            "Suggest the source type to ingest next.",
        ],
    }


def render_query_packet(packet: dict[str, object], as_json: bool) -> None:
    if as_json:
        print(json.dumps(packet, indent=2, sort_keys=True))
        return

    print(f"Index: {packet['index_path']}")
    print("Candidate pages:")
    candidate_pages = packet["candidate_pages"]
    if isinstance(candidate_pages, list) and candidate_pages:
        for page in candidate_pages:
            print(f"- {page}")
    else:
        print("- (none)")

    print("Answer contract:")
    answer_contract = packet["answer_contract"]
    if isinstance(answer_contract, list):
        for item in answer_contract:
            print(f"- {item}")

    print("Not-covered template:")
    not_covered_template = packet["not_covered_template"]
    if isinstance(not_covered_template, list):
        for item in not_covered_template:
            print(f"- {item}")


def append_wiki_log_entry(
    git_root: pathlib.Path,
    entry_type: str,
    title: str,
    pages: list[str],
    insight: str,
) -> None:
    log_path, log_error = wiki_write_file(git_root, pathlib.Path("log.md"))
    if log_error is not None:
        raise ValueError(log_error)
    assert log_path is not None
    page_label = "Pages consulted:" if entry_type == "query" else "Pages touched:"
    page_list = ", ".join(format_wikilink_page(page) for page in pages) if pages else "(none)"
    entry_title = trim_summary_text(title, LOG_TITLE_MAX_CHARS)
    entry_insight = trim_summary_text(insight, LOG_INSIGHT_MAX_CHARS)
    entry = "\n".join(
        [
            "",
            f"## [{datetime.date.today().isoformat()}] {entry_type} | {entry_title}",
            f"- {page_label} {page_list}",
            f"- Key insight: {entry_insight}",
            "",
        ]
    )
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(entry)


def run_query(args) -> int:
    cwd = pathlib.Path.cwd()
    git_root, _message = resolve_git_root(cwd)
    if git_root is None:
        print("No git repository found for current directory.")
        return 2

    try:
        packet = build_query_packet(git_root, args.question)
    except ValueError as error:
        print(str(error))
        return 2

    if args.key_insight or args.not_covered:
        source_suggestion = args.suggest_source or "ingest curated source notes"
        if args.not_covered:
            title = f"not-covered: {args.question}"
            insight = (
                ".llm-wiki/ does not currently cover this topic; "
                f"next ingest source type: {source_suggestion}."
            )
        else:
            title = args.question
            insight = args.key_insight
        for label, value in (
            ("query title", title),
            ("key insight", insight),
            ("source suggestion", source_suggestion),
            *[
                (f"consulted page {index}", page)
                for index, page in enumerate(args.consulted, 1)
            ],
        ):
            unsafe_error = validate_persisted_wiki_text(label, value)
            if unsafe_error is not None:
                print(unsafe_error)
                return 2
        try:
            append_wiki_log_entry(git_root, "query", title, args.consulted, insight)
        except ValueError as error:
            print(str(error))
            return 2

    render_query_packet(packet, args.json)
    return 0


def is_video_url(url: str) -> bool:
    normalized_url = url.lower()
    return any(marker in normalized_url for marker in VIDEO_URL_MARKERS)


def has_disallowed_raw_policy_content(text: str) -> bool:
    normalized_text = text.lower()
    return any(phrase in normalized_text for phrase in DISALLOWED_RAW_PHRASES)


def unsafe_wiki_text_reason(text: str) -> str | None:
    encoded_size = len(text.encode("utf-8"))
    if encoded_size > RAW_SIZE_WARNING_BYTES:
        return "is larger than the raw size policy allows."
    if has_secret_like_content(text):
        return "contains secret-looking material."
    if has_disallowed_raw_policy_content(text):
        return "appears to contain transcripts, logs, dumps, private data, or active task state."
    return None


def validate_curated_source_text(text: str) -> str | None:
    reason = unsafe_wiki_text_reason(text)
    if reason is not None:
        return f"Unsafe raw material was not stored. Curated source text {reason}"
    return None


def validate_persisted_wiki_text(label: str, value: str) -> str | None:
    if not value:
        return None
    reason = unsafe_wiki_text_reason(value)
    if reason is not None:
        return f"Unsafe wiki content was not stored. {label} {reason}"
    return None


def normalize_source_record(args) -> tuple[dict[str, str] | None, str | None]:
    if not args.text and not args.file and not args.url:
        return None, "Provide one of --text, --file, or --url."
    if args.file and args.text:
        return None, "Use either --file or --text for curated source text, not both."

    source_text = ""
    kind = "text"
    provenance = "inline text"

    if args.file:
        source_path = pathlib.Path(args.file)
        try:
            source_text = source_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return None, f"Could not read curated source file: {args.file}"
        kind = "file"
        provenance = source_path.as_posix()
    elif args.url:
        kind = "url"
        provenance = args.url
        if args.text:
            source_text = args.text
        elif is_video_url(args.url):
            return (
                None,
                "Provide a transcript, summary, or curated notes before ingesting video sources.",
            )
    else:
        source_text = args.text

    if source_text:
        unsafe_error = validate_curated_source_text(source_text)
        if unsafe_error is not None:
            return None, unsafe_error

    return {
        "kind": kind,
        "title": args.title,
        "provenance": provenance,
        "text": source_text,
    }, None


def render_ingest_result(result: dict[str, object], as_json: bool) -> None:
    if as_json:
        print(json.dumps(result, indent=2, sort_keys=True))
        return

    print("Ingest source accepted.")
    print(f"Source kind: {result['kind']}")
    print(f"Title: {result['title']}")
    print(f"Provenance: {result['provenance']}")
    print(f"Raw preservation: {result['raw_preservation']}")
    touched_pages = result.get("touched_pages", [])
    if isinstance(touched_pages, list):
        print("Pages touched:")
        for page in touched_pages:
            print(f"- {page}")


def wiki_page_path(
    git_root: pathlib.Path, page: str
) -> tuple[pathlib.Path | None, str | None]:
    try:
        wikilink = format_wikilink_page(page)
    except ValueError as error:
        return None, str(error)

    normalized_target = normalize_wikilink_target(wikilink[2:-2])
    page_path = git_root / WIKI_ROOT / pathlib.Path(normalized_target)
    wiki_root = git_root / WIKI_ROOT
    if not path_is_under(page_path, wiki_root):
        return None, "target must stay inside .llm-wiki"
    return page_path, None


def append_page_update(path: pathlib.Path, content: str, provenance: str) -> None:
    update_date = datetime.date.today().isoformat()
    entry = "\n".join(
        [
            "",
            f"## Update {update_date}",
            trim_summary_text(content, LOG_INSIGHT_MAX_CHARS),
            "",
            f"_Updated from {provenance} {update_date}._",
            "",
        ]
    )
    with path.open("a", encoding="utf-8") as handle:
        handle.write(entry)


def update_index_for_new_page(
    git_root: pathlib.Path, page: str, title: str
) -> str | None:
    index_path, index_error = wiki_write_file(git_root, pathlib.Path("index.md"))
    if index_error is not None:
        return index_error
    assert index_path is not None
    wikilink = format_wikilink_page(page)
    index_text = index_path.read_text(encoding="utf-8")
    if wikilink in index_text:
        return None
    with index_path.open("a", encoding="utf-8") as handle:
        handle.write(f"\n- {wikilink} - {title}\n")
    return None


def slugify_title(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug or "curated-source"


def next_curated_raw_path(
    git_root: pathlib.Path, title: str
) -> tuple[pathlib.Path | None, str | None]:
    raw_root, raw_root_error = wiki_write_directory(
        git_root, pathlib.Path("raw") / "curated"
    )
    if raw_root_error is not None:
        return None, raw_root_error
    raw_slug = slugify_title(title)
    suffix = 1
    while True:
        raw_filename = f"{raw_slug}.md" if suffix == 1 else f"{raw_slug}-{suffix}.md"
        raw_relative_path = pathlib.Path("raw") / "curated" / raw_filename
        raw_path, raw_file_error = wiki_write_file(git_root, raw_relative_path)
        if raw_file_error is not None:
            return None, raw_file_error
        assert raw_path is not None
        if not raw_path.exists():
            return raw_path, None
        suffix += 1


def preserve_curated_raw_source(
    git_root: pathlib.Path, title: str, text: str, provenance: str
) -> tuple[str | None, str | None]:
    unsafe_error = validate_curated_source_text(text)
    if unsafe_error is not None:
        return None, unsafe_error

    raw_root, raw_root_error = wiki_write_directory(
        git_root, pathlib.Path("raw") / "curated"
    )
    if raw_root_error is not None:
        return None, raw_root_error
    assert raw_root is not None
    raw_root.mkdir(parents=True, exist_ok=True)
    raw_path, raw_path_error = next_curated_raw_path(git_root, title)
    if raw_path_error is not None:
        return None, raw_path_error
    assert raw_path is not None
    raw_note = "\n".join(
        [
            f"# {title}",
            "",
            f"Provenance: {provenance}",
            f"Date: {datetime.date.today().isoformat()}",
            "",
            "## Curated Source",
            "",
            text,
            "",
        ]
    )
    raw_path.write_text(raw_note, encoding="utf-8")
    return repo_relative_path(raw_path, git_root), None


def run_ingest(args) -> int:
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

    source_record, error = normalize_source_record(args)
    if error is not None:
        print(error)
        return 2
    assert source_record is not None

    for label, value in (
        ("title", args.title),
        ("key idea", args.key_idea),
        ("source provenance", source_record["provenance"]),
        ("new page title", args.new_page_title or ""),
        *[
            (f"target page {index}", page)
            for index, page in enumerate(args.target_page, 1)
        ],
        ("new page", args.new_page),
    ):
        unsafe_error = validate_persisted_wiki_text(label, value)
        if unsafe_error is not None:
            print(unsafe_error)
            return 2

    touched_page_names = list(args.target_page)
    if args.new_page:
        touched_page_names.append(args.new_page)
    if not touched_page_names:
        print("Provide at least one --target-page or --new-page.")
        return 2
    if len(touched_page_names) > 15:
        print("Ingest touches more than the 15 page hard cap.")
        return 2

    new_path: pathlib.Path | None = None
    if args.new_page and not args.new_page_reason:
        print("New page creation requires --new-page-reason.")
        return 2
    if args.new_page:
        new_path, new_error = wiki_page_path(git_root, args.new_page)
        if new_error is not None:
            print(new_error)
            return 2
        assert new_path is not None
        wiki_relative = new_path.relative_to(wiki_root).as_posix()
        if wiki_relative.startswith("summaries/") and not args.summary_page:
            print("Summary pages require --summary-page.")
            return 2
        new_relative = pathlib.Path(wiki_relative)
        _new_write_path, new_write_error = wiki_write_file(git_root, new_relative)
        if new_write_error is not None:
            print(new_write_error)
            return 2
        _new_parent_path, new_parent_error = wiki_write_directory(
            git_root, new_relative.parent
        )
        if new_parent_error is not None:
            print(new_parent_error)
            return 2

    _log_path, log_error = wiki_write_file(git_root, pathlib.Path("log.md"))
    if log_error is not None:
        print(log_error)
        return 2
    if args.new_page:
        _index_path, index_error = wiki_write_file(git_root, pathlib.Path("index.md"))
        if index_error is not None:
            print(index_error)
            return 2
    if args.preserve_raw and source_record["text"]:
        _raw_path, raw_path_error = next_curated_raw_path(git_root, args.title)
        if raw_path_error is not None:
            print(raw_path_error)
            return 2

    target_paths: list[tuple[str, pathlib.Path]] = []
    for page in args.target_page:
        target_path, target_error = wiki_page_path(git_root, page)
        if target_error is not None:
            print(target_error)
            return 2
        assert target_path is not None
        if not target_path.is_file() or target_path.is_symlink():
            print(f"Target page does not exist: {format_wikilink_page(page)}")
            return 2
        target_paths.append((page, target_path))

    touched_pages: list[str] = []
    for page, target_path in target_paths:
        append_page_update(target_path, args.key_idea, args.title)
        touched_pages.append(format_wikilink_page(page))

    if args.new_page:
        assert new_path is not None
        new_path.parent.mkdir(parents=True, exist_ok=True)
        new_title = args.new_page_title or args.title
        if new_path.exists():
            append_page_update(new_path, args.key_idea, args.title)
        else:
            new_path.write_text(
                "\n".join(
                    [
                        f"# {new_title}",
                        "",
                        args.key_idea,
                        "",
                        f"_Updated from {args.title} {datetime.date.today().isoformat()}._",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            index_error = update_index_for_new_page(git_root, args.new_page, new_title)
            if index_error is not None:
                print(index_error)
                return 2
        touched_pages.append(format_wikilink_page(args.new_page))

    raw_preservation = "skipped"
    if args.preserve_raw and source_record["text"]:
        raw_path, raw_error = preserve_curated_raw_source(
            git_root,
            args.title,
            source_record["text"],
            source_record["provenance"],
        )
        if raw_error is not None:
            print(raw_error)
            return 2
        assert raw_path is not None
        raw_preservation = raw_path

    if touched_pages:
        try:
            append_wiki_log_entry(
                git_root,
                "ingest",
                args.title,
                touched_pages,
                args.key_idea,
            )
        except ValueError as error:
            print(str(error))
            return 2

    result: dict[str, object] = {
        "kind": source_record["kind"],
        "title": source_record["title"],
        "provenance": source_record["provenance"],
        "raw_preservation": raw_preservation,
        "target_pages": args.target_page,
        "new_page": args.new_page,
        "touched_pages": touched_pages,
    }
    render_ingest_result(result, args.json)
    return 0


def run_install(args) -> int:
    target_dir = pathlib.Path(args.target).expanduser()
    print(f"Install target: {target_dir}")

    if target_dir.exists() and not target_dir.is_dir():
        print_text_section(
            "Conflicts:",
            [f"{target_dir} exists and is not a directory"],
        )
        return 2

    if not target_dir.parent.exists():
        print_text_section(
            "Conflicts:",
            [
                f"Codex home does not exist: {target_dir.parent}",
                "Install or run Codex first, or pass --target to an existing Codex home.",
            ],
        )
        return 2

    actions, conflicts = collect_install_plan(target_dir, args.force, args.uninstall)
    print_install_plan(actions, args.dry_run, args.uninstall)

    if conflicts:
        print_text_section("Conflicts:", conflicts)
        return 2

    if args.dry_run:
        if args.uninstall:
            print("Dry run only; no skill symlinks were removed.")
        else:
            print("Dry run only; no skill symlinks were installed.")
        return 0

    apply_install_plan(target_dir, actions)
    if args.uninstall:
        print("Project LLM Wiki skills uninstalled from this target.")
    else:
        print("Next: restart Codex, then run $project-wiki-init in a target Git repo")
    return 0


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
    agents_plan = build_agents_patch_plan(
        git_root, patch_agents=not args.no_patch_agents
    )
    agents_conflicts = list(agents_plan["conflicts"])
    if args.dry_run:
        print_path_section("Would create paths:", would_create)
        print_path_section("Would skip existing paths:", would_skip)
        print_source_status(found_sources, skipped_sources)
        print_agents_patch_plan(agents_plan)
        all_conflicts = [*conflicts, *agents_conflicts]
        if all_conflicts:
            print_text_section("Conflicts:", all_conflicts)
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

    all_conflicts = [*conflicts, *agents_conflicts]
    if all_conflicts:
        print_text_section("Conflicts:", all_conflicts)
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
    print(apply_agents_patch_plan(git_root, agents_plan))
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
            query prepares index-first support packets; ingest updates curated wiki pages.
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
    init.add_argument(
        "--no-patch-agents",
        action="store_true",
        help="skip root AGENTS.md Project LLM Wiki section patching",
    )
    init.set_defaults(func=run_init)

    install = subcommands.add_parser(
        "install", help="install Project LLM Wiki Codex skill symlinks"
    )
    install.add_argument(
        "--target",
        default=str(default_install_target()),
        help="Codex skills directory to install into; defaults to ${CODEX_HOME:-~/.codex}/skills",
    )
    install.add_argument(
        "--dry-run",
        action="store_true",
        help="report planned skill symlink changes without writing files",
    )
    install.add_argument(
        "--force",
        action="store_true",
        help="replace existing stale symlinks that point somewhere else",
    )
    install.add_argument(
        "--uninstall",
        action="store_true",
        help="remove only Project LLM Wiki symlinks owned by this package",
    )
    install.set_defaults(func=run_install)

    lint = subcommands.add_parser("lint", help="lint .llm-wiki structure")
    lint.add_argument("--json", action="store_true", help="render lint findings as JSON")
    lint.set_defaults(func=run_lint)

    query = subcommands.add_parser(
        "query", help="prepare an index-first project wiki query"
    )
    query.add_argument(
        "question", help="question or topic to answer from .llm-wiki"
    )
    query.add_argument(
        "--json", action="store_true", help="render query support packet as JSON"
    )
    query.add_argument(
        "--consulted",
        action="append",
        default=[],
        help="wiki page consulted by the agent, e.g. features/ideas",
    )
    query.add_argument(
        "--key-insight",
        default="",
        help="concise insight or not-covered result to append to log.md",
    )
    query.add_argument(
        "--not-covered",
        action="store_true",
        help="log the query as not covered by current wiki pages",
    )
    query.add_argument(
        "--suggest-source",
        default="",
        help="source type to suggest when the topic is not covered",
    )
    query.set_defaults(func=run_query)

    ingest = subcommands.add_parser(
        "ingest", help="ingest curated source material into .llm-wiki"
    )
    ingest.add_argument("--text", help="curated source text")
    ingest.add_argument("--file", help="path to curated source text file")
    ingest.add_argument(
        "--url",
        help="source URL used as provenance; pair with --text for curated content",
    )
    ingest.add_argument("--title", required=True, help="short source title")
    ingest.add_argument(
        "--target-page",
        action="append",
        default=[],
        help="existing wiki page to update",
    )
    ingest.add_argument(
        "--new-page",
        default="",
        help="new wiki page to create only when no existing page covers the concept",
    )
    ingest.add_argument("--new-page-title", default="", help="heading for --new-page")
    ingest.add_argument(
        "--new-page-reason",
        default="",
        help="explicit reason the new page is warranted",
    )
    ingest.add_argument(
        "--key-idea", required=True, help="concise durable idea to add and log"
    )
    ingest.add_argument(
        "--preserve-raw",
        action="store_true",
        help="preserve short curated source note when policy allows",
    )
    ingest.add_argument(
        "--summary-page",
        action="store_true",
        help="mark --new-page as a cross-cutting summary page",
    )
    ingest.add_argument("--json", action="store_true", help="render ingest result as JSON")
    ingest.set_defaults(func=run_ingest)

    return parser


def main(argv: list[str] | None = None) -> int:
    _script_path = pathlib.Path(__file__)
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__": raise SystemExit(main())
