from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "skills" / "project-llm-wiki"
HELPER = PACKAGE / "scripts" / "project_wiki.py"
ROOT_AGENTS_START_MARKER = "<!-- PROJECT-LLM-WIKI:START -->"
ROOT_AGENTS_END_MARKER = "<!-- PROJECT-LLM-WIKI:END -->"
ROOT_AGENTS_MANAGED_SECTION = """<!-- PROJECT-LLM-WIKI:START -->
## Project LLM Wiki

Before non-trivial architecture, debugging, product, onboarding, or cross-file implementation work, read `.llm-wiki/index.md` first, then only task-relevant linked pages.

For simple typo fixes and narrow single-file edits, wiki lookup is not required.

Current repository files are authoritative when they disagree with `.llm-wiki/`; report wiki drift when found.

Update `.llm-wiki/` only after validated non-trivial work produces durable learning. Do not use `.llm-wiki/` for active task status.
<!-- PROJECT-LLM-WIKI:END -->
"""


class ProjectWikiInitTests(unittest.TestCase):
    def run_git(self, repo: Path, *args: str):
        return subprocess.run(
            ["git", *args],
            cwd=repo,
            capture_output=True,
            text=True,
            check=False,
        )

    def init_repo(self, repo: Path):
        result = subprocess.run(
            ["git", "init"],
            cwd=repo,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        return result

    def run_helper(self, cwd: Path, *args: str):
        return subprocess.run(
            [sys.executable, str(HELPER), *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )

    def git_status_short(self, repo: Path):
        return subprocess.run(
            ["git", "status", "--short"],
            cwd=repo,
            capture_output=True,
            text=True,
            check=False,
        )

    def marker_external_bytes(self, content: bytes) -> bytes:
        start_marker = ROOT_AGENTS_START_MARKER.encode("utf-8")
        end_marker = ROOT_AGENTS_END_MARKER.encode("utf-8")
        start = content.index(start_marker)
        end = content.index(end_marker, start) + len(end_marker)
        return content[:start] + content[end:]

    def test_init_creates_root_agents_when_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_repo(repo)

            result = self.run_helper(repo, "init")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertEqual(
                ROOT_AGENTS_MANAGED_SECTION,
                (repo / "AGENTS.md").read_text(encoding="utf-8"),
            )
            self.assertIn("Root AGENTS.md: created", output)

    def test_init_appends_project_wiki_section_without_overwriting_existing_agents(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_repo(repo)
            original = textwrap.dedent(
                """\
                # Agent Instructions

                ## Repo-Specific Workflow

                Keep this local deployment rule.
                """
            )
            (repo / "AGENTS.md").write_text(original, encoding="utf-8")

            result = self.run_helper(repo, "init")
            output = result.stdout + result.stderr
            updated = (repo / "AGENTS.md").read_text(encoding="utf-8")

            self.assertEqual(0, result.returncode, output)
            self.assertTrue(updated.startswith(original), updated)
            self.assertIn(ROOT_AGENTS_MANAGED_SECTION, updated)
            self.assertIn("Root AGENTS.md: updated", output)

    def test_init_appends_to_crlf_agents_without_rewriting_existing_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_repo(repo)
            original = (
                b"# Agent Instructions\r\n"
                b"\r\n"
                b"## NotebookLM Second Brain\r\n"
                b"Keep this retrieval rule byte-for-byte.\r\n"
            )
            agents = repo / "AGENTS.md"
            agents.write_bytes(original)

            result = self.run_helper(repo, "init")
            output = result.stdout + result.stderr
            updated = agents.read_bytes()

            self.assertEqual(0, result.returncode, output)
            self.assertTrue(updated.startswith(original), updated)
            self.assertIn(ROOT_AGENTS_MANAGED_SECTION.encode("utf-8"), updated)
            self.assertIn("Root AGENTS.md: updated", output)

    def test_init_updates_only_marker_bounded_project_wiki_section(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_repo(repo)
            original = textwrap.dedent(
                """\
                # Agent Instructions

                Prefix rule stays untouched.

                <!-- PROJECT-LLM-WIKI:START -->
                Old wiki instructions that should be replaced.
                <!-- PROJECT-LLM-WIKI:END -->

                Suffix rule stays untouched.
                """
            ).encode("utf-8")
            agents = repo / "AGENTS.md"
            agents.write_bytes(original)

            result = self.run_helper(repo, "init")
            output = result.stdout + result.stderr
            updated = agents.read_bytes()

            self.assertEqual(0, result.returncode, output)
            self.assertEqual(
                self.marker_external_bytes(original),
                self.marker_external_bytes(updated),
            )
            updated_text = updated.decode("utf-8")
            self.assertIn(ROOT_AGENTS_MANAGED_SECTION.rstrip("\n"), updated_text)
            self.assertNotIn("Old wiki instructions", updated_text)
            self.assertIn("Root AGENTS.md: updated", output)

    def test_init_updates_crlf_marker_section_without_mutating_external_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_repo(repo)
            original = (
                b"# Agent Instructions\r\n"
                b"\r\n"
                b"Prefix rule stays untouched.\r\n"
                b"\r\n"
                + ROOT_AGENTS_START_MARKER.encode("utf-8")
                + b"\r\n"
                b"Old wiki instructions that should be replaced.\r\n"
                + ROOT_AGENTS_END_MARKER.encode("utf-8")
                + b"\r\n"
                b"\r\n"
                b"Suffix rule stays untouched.\r\n"
            )
            agents = repo / "AGENTS.md"
            agents.write_bytes(original)

            result = self.run_helper(repo, "init")
            output = result.stdout + result.stderr
            updated = agents.read_bytes()

            self.assertEqual(0, result.returncode, output)
            self.assertEqual(
                self.marker_external_bytes(original),
                self.marker_external_bytes(updated),
            )
            self.assertIn(ROOT_AGENTS_MANAGED_SECTION.rstrip("\n").encode("utf-8"), updated)
            self.assertNotIn(b"Old wiki instructions", updated)
            self.assertIn("Root AGENTS.md: updated", output)

    def test_init_preserves_notebooklm_gsd_and_workflow_sections_byte_for_byte(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_repo(repo)
            original = textwrap.dedent(
                """\
                # Agent Instructions

                ## NotebookLM Second Brain

                Keep this NotebookLM retrieval guidance byte-for-byte.

                <!-- PROJECT-LLM-WIKI:START -->
                Old managed wiki section.
                <!-- PROJECT-LLM-WIKI:END -->

                ## GSD Workflow Enforcement

                Keep this GSD workflow rule byte-for-byte.

                ## Repo-Specific Workflow

                Keep this repo-specific workflow byte-for-byte.
                """
            ).encode("utf-8")
            agents = repo / "AGENTS.md"
            agents.write_bytes(original)

            result = self.run_helper(repo, "init")
            output = result.stdout + result.stderr
            updated = agents.read_bytes()

            self.assertEqual(0, result.returncode, output)
            self.assertEqual(
                self.marker_external_bytes(original),
                self.marker_external_bytes(updated),
            )
            for section in (
                b"## NotebookLM Second Brain",
                b"## GSD Workflow Enforcement",
                b"## Repo-Specific Workflow",
            ):
                self.assertIn(section, updated)

    def test_dry_run_reports_managed_agents_section_without_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_repo(repo)

            result = self.run_helper(repo, "init", "--dry-run")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertFalse((repo / ".llm-wiki").exists())
            self.assertFalse((repo / "AGENTS.md").exists())
            self.assertIn("Root AGENTS.md: would create", output)
            self.assertIn("Managed AGENTS.md section:", output)
            self.assertIn(ROOT_AGENTS_MANAGED_SECTION, output)

    def test_init_no_patch_agents_skips_root_agents_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_repo(repo)
            original = b"# Agent Instructions\n\nDo not change this file.\n"
            (repo / "AGENTS.md").write_bytes(original)

            result = self.run_helper(repo, "init", "--no-patch-agents")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertEqual(original, (repo / "AGENTS.md").read_bytes())
            self.assertTrue((repo / ".llm-wiki" / "index.md").is_file())
            self.assertIn("Root AGENTS.md: skipped by --no-patch-agents", output)

    def test_init_rejects_invalid_utf8_root_agents_without_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_repo(repo)
            original = b"\xff\xfeinvalid root agents\n"
            (repo / "AGENTS.md").write_bytes(original)

            result = self.run_helper(repo, "init")
            output = result.stdout + result.stderr

            self.assertEqual(2, result.returncode, output)
            self.assertIn(
                "AGENTS.md: expected readable UTF-8, could not patch Project LLM Wiki section",
                output,
            )
            self.assertEqual(original, (repo / "AGENTS.md").read_bytes())
            self.assertFalse((repo / ".llm-wiki").exists())

    def test_init_rejects_unmatched_project_wiki_marker_without_writing(self):
        cases = (
            (
                "start",
                f"# Agents\n\n{ROOT_AGENTS_START_MARKER}\nMissing end\n",
                "AGENTS.md: unmatched Project LLM Wiki start marker",
            ),
            (
                "end",
                f"# Agents\n\nMissing start\n{ROOT_AGENTS_END_MARKER}\n",
                "AGENTS.md: unmatched Project LLM Wiki end marker",
            ),
        )
        for _name, content, expected in cases:
            with self.subTest(marker=_name):
                with tempfile.TemporaryDirectory() as tmp:
                    repo = Path(tmp)
                    self.init_repo(repo)
                    original = content.encode("utf-8")
                    (repo / "AGENTS.md").write_bytes(original)

                    result = self.run_helper(repo, "init")
                    output = result.stdout + result.stderr

                    self.assertEqual(2, result.returncode, output)
                    self.assertIn(expected, output)
                    self.assertEqual(original, (repo / "AGENTS.md").read_bytes())
                    self.assertFalse((repo / ".llm-wiki").exists())

    def test_init_rejects_duplicate_project_wiki_markers_without_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_repo(repo)
            original = textwrap.dedent(
                f"""\
                # Agents

                {ROOT_AGENTS_START_MARKER}
                First section.
                {ROOT_AGENTS_END_MARKER}

                {ROOT_AGENTS_START_MARKER}
                Second section.
                {ROOT_AGENTS_END_MARKER}
                """
            ).encode("utf-8")
            (repo / "AGENTS.md").write_bytes(original)

            result = self.run_helper(repo, "init")
            output = result.stdout + result.stderr

            self.assertEqual(2, result.returncode, output)
            self.assertIn("AGENTS.md: multiple Project LLM Wiki marker pairs", output)
            self.assertEqual(original, (repo / "AGENTS.md").read_bytes())
            self.assertFalse((repo / ".llm-wiki").exists())

    def test_init_creates_wiki_at_git_root_from_subdirectory(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_repo(repo)
            (repo / "README.md").write_text("# Test Repo\n", encoding="utf-8")
            (repo / "AGENTS.md").write_text("# Agent Instructions\n", encoding="utf-8")
            nested = repo / "nested" / "deeper"
            nested.mkdir(parents=True)

            result = self.run_helper(nested, "init")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            expected_files = [
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
            ]
            for relative_path in expected_files:
                self.assertTrue((repo / relative_path).is_file(), relative_path)
            self.assertFalse((nested / ".llm-wiki").exists())
            self.assertIn("Resolved git root:", output)
            self.assertIn("Created paths:", output)

    def test_init_refuses_parent_workspace_with_child_repo_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            child = parent / "api"
            child.mkdir()
            self.init_repo(child)

            result = self.run_helper(parent, "init")
            output = result.stdout + result.stderr

            self.assertNotEqual(0, result.returncode)
            self.assertFalse((parent / ".llm-wiki").exists())
            self.assertIn("No git repository found for current directory.", output)
            self.assertIn("Candidate child repositories:", output)
            self.assertIn("api", output)
            self.assertIn("cd into the intended repo", output)

    def test_dry_run_reports_without_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_repo(repo)
            (repo / "README.md").write_text("# Test Repo\n", encoding="utf-8")

            result = self.run_helper(repo, "init", "--dry-run")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertFalse((repo / ".llm-wiki").exists())
            self.assertIn("Resolved git root:", output)
            self.assertIn("Would create paths:", output)
            self.assertIn("Sources found: README.md", output)
            self.assertIn("Skipped sources: AGENTS.md", output)

    def test_conflict_fails_before_partial_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_repo(repo)
            wiki = repo / ".llm-wiki"
            wiki.mkdir()
            (wiki / "features").write_text("not a directory\n", encoding="utf-8")

            result = self.run_helper(repo, "init")
            output = result.stdout + result.stderr

            self.assertNotEqual(0, result.returncode)
            self.assertIn(".llm-wiki/features: expected directory, found file", output)
            self.assertFalse((wiki / "README.md").exists())

    def test_dry_run_conflict_reports_plan_and_conflicts_without_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_repo(repo)
            wiki = repo / ".llm-wiki"
            wiki.mkdir()
            (wiki / "features").write_text("not a directory\n", encoding="utf-8")

            result = self.run_helper(repo, "init", "--dry-run")
            output = result.stdout + result.stderr

            self.assertNotEqual(0, result.returncode)
            self.assertIn("Would create paths:", output)
            self.assertIn("Would skip existing paths:", output)
            self.assertIn("Conflicts:", output)
            self.assertIn(".llm-wiki/features: expected directory, found file", output)
            self.assertFalse((wiki / "README.md").exists())

    def test_init_rejects_symlinked_required_paths_before_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            repo = parent / "repo"
            outside = parent / "outside-wiki"
            repo.mkdir()
            outside.mkdir()
            self.init_repo(repo)
            wiki = repo / ".llm-wiki"
            wiki.symlink_to(outside, target_is_directory=True)

            result = self.run_helper(repo, "init")
            output = result.stdout + result.stderr

            self.assertNotEqual(0, result.returncode)
            self.assertIn(".llm-wiki: expected real directory, found symlink", output)
            self.assertFalse((outside / "README.md").exists())

    def test_init_rejects_symlinked_wiki_before_reading_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            repo = parent / "repo"
            outside = parent / "outside-wiki"
            repo.mkdir()
            outside.mkdir()
            self.init_repo(repo)
            (outside / "index.md").write_bytes(b"\xff\xfeoutside index\n")
            (repo / ".llm-wiki").symlink_to(outside, target_is_directory=True)

            result = self.run_helper(repo, "init")
            output = result.stdout + result.stderr

            self.assertEqual(2, result.returncode, output)
            self.assertIn(".llm-wiki: expected real directory, found symlink", output)
            self.assertNotIn("Traceback", output)

    def test_init_rejects_broken_symlinked_required_file_before_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            repo = parent / "repo"
            outside_file = parent / "outside-readme.md"
            repo.mkdir()
            self.init_repo(repo)
            wiki = repo / ".llm-wiki"
            wiki.mkdir()
            (wiki / "README.md").symlink_to(outside_file)

            result = self.run_helper(repo, "init")
            output = result.stdout + result.stderr

            self.assertNotEqual(0, result.returncode)
            self.assertIn(".llm-wiki/README.md: expected real file, found symlink", output)
            self.assertFalse(outside_file.exists())

    def test_init_rejects_invalid_existing_index_before_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_repo(repo)
            wiki = repo / ".llm-wiki"
            wiki.mkdir()
            (wiki / "index.md").write_bytes(b"\xff\xfeinvalid index\n")

            result = self.run_helper(repo, "init")
            output = result.stdout + result.stderr

            self.assertEqual(2, result.returncode, output)
            self.assertIn(
                ".llm-wiki/index.md: expected UTF-8 markdown, could not read",
                output,
            )
            self.assertNotIn("Traceback", output)
            self.assertFalse((wiki / "README.md").exists())
            self.assertFalse((wiki / "raw").exists())

    def test_dry_run_rejects_invalid_existing_index_without_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_repo(repo)
            wiki = repo / ".llm-wiki"
            wiki.mkdir()
            (wiki / "index.md").write_bytes(b"\xff\xfeinvalid index\n")

            result = self.run_helper(repo, "init", "--dry-run")
            output = result.stdout + result.stderr

            self.assertEqual(2, result.returncode, output)
            self.assertIn("Would create paths:", output)
            self.assertIn(
                ".llm-wiki/index.md: expected UTF-8 markdown, could not read",
                output,
            )
            self.assertNotIn("Traceback", output)
            self.assertFalse((wiki / "README.md").exists())

    def test_clean_repo_status_shows_llm_wiki_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_repo(repo)

            result = self.run_helper(repo, "init")
            output = result.stdout + result.stderr
            status = self.git_status_short(repo)

            self.assertEqual(0, result.returncode, output)
            self.assertEqual(0, status.returncode, status.stdout + status.stderr)
            self.assertTrue(
                "?? .llm-wiki/" in status.stdout or ".llm-wiki/" in status.stdout,
                status.stdout,
            )
            self.assertTrue((repo / ".llm-wiki" / "README.md").exists())
            self.assertTrue((repo / ".llm-wiki" / "index.md").exists())
            self.assertTrue((repo / ".llm-wiki" / "raw" / "README.md").exists())
            self.assertTrue((repo / ".llm-wiki" / "raw" / "curated" / "README.md").exists())
            self.assertTrue((repo / ".llm-wiki" / "features" / "ideas.md").exists())
            self.assertTrue((repo / ".llm-wiki" / "summaries" / "repo-overview.md").exists())

    def test_rerun_preserves_existing_files_and_reports_missing_index_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_repo(repo)

            first = self.run_helper(repo, "init")
            first_output = first.stdout + first.stderr
            self.assertEqual(0, first.returncode, first_output)

            index = repo / ".llm-wiki" / "index.md"
            overview = repo / ".llm-wiki" / "summaries" / "repo-overview.md"
            index.write_text("# Custom Index\n\nSentinel\n", encoding="utf-8")
            overview.write_text("# Custom Overview\n\nSentinel\n", encoding="utf-8")

            rerun = self.run_helper(repo, "init")
            output = rerun.stdout + rerun.stderr

            self.assertEqual(0, rerun.returncode, output)
            self.assertIn("Sentinel", index.read_text(encoding="utf-8"))
            self.assertIn("Sentinel", overview.read_text(encoding="utf-8"))
            self.assertIn("Skipped existing paths:", output)
            self.assertIn("Missing recommended index links:", output)
            self.assertIn("[[features/ideas]]", output)
            self.assertIn("[[summaries/repo-overview]]", output)

    def test_repo_overview_uses_only_readme_and_agents(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_repo(repo)
            (repo / "README.md").write_text("# Test Repo\n", encoding="utf-8")
            (repo / "AGENTS.md").write_text("# Agent Instructions\n", encoding="utf-8")
            (repo / "package.json").write_text("{}\n", encoding="utf-8")
            (repo / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
            (repo / "go.mod").write_text("module example.com/test\n", encoding="utf-8")
            (repo / "Cargo.toml").write_text("[package]\n", encoding="utf-8")

            result = self.run_helper(repo, "init")
            output = result.stdout + result.stderr
            overview = repo / ".llm-wiki" / "summaries" / "repo-overview.md"

            self.assertEqual(0, result.returncode, output)
            overview_text = overview.read_text(encoding="utf-8")
            self.assertIn("Sources found: README.md, AGENTS.md", overview_text)
            self.assertNotIn("package.json", overview_text)
            self.assertNotIn("pyproject.toml", overview_text)
            self.assertNotIn("go.mod", overview_text)
            self.assertNotIn("Cargo.toml", overview_text)

    def test_raw_policy_and_ideas_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_repo(repo)

            result = self.run_helper(repo, "init")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            raw_readme = (repo / ".llm-wiki" / "raw" / "README.md").read_text(
                encoding="utf-8"
            )
            curated_readme = (
                repo / ".llm-wiki" / "raw" / "curated" / "README.md"
            ).read_text(encoding="utf-8")
            ideas = (repo / ".llm-wiki" / "features" / "ideas.md").read_text(
                encoding="utf-8"
            )

            self.assertIn(
                "secrets, credentials, auth tokens, private customer data, full logs, database exports, generated dumps",
                raw_readme,
            )
            self.assertIn("de-secreted", curated_readme)
            self.assertIn("intentionally selected", curated_readme)
            self.assertIn("small sources or excerpts", curated_readme)
            self.assertIn("2026-05-13-api-notes.md", curated_readme)
            self.assertIn("Thought", ideas)
            self.assertIn("Why it might matter", ideas)
            self.assertIn("Current leaning", ideas)
            self.assertIn("Not decided", ideas)
            self.assertIn("Related links", ideas)
            self.assertIn("not a roadmap, backlog, or active task-state store", ideas)


if __name__ == "__main__":
    unittest.main()
