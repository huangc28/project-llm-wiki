#!/usr/bin/env python3
import argparse
import datetime
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
