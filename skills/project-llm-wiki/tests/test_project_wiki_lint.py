from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "skills" / "project-llm-wiki"
HELPER = PACKAGE / "scripts" / "project_wiki.py"


class ProjectWikiLintTests(unittest.TestCase):
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

    def init_wiki(self, repo: Path):
        self.init_repo(repo)
        result = self.run_helper(repo, "init")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        return result

    def test_lint_clean_initialized_wiki_reports_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("No issues found in .llm-wiki/", output)

    def test_lint_reports_broken_obsidian_wikilink_as_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            ideas = repo / ".llm-wiki" / "features" / "ideas.md"
            ideas.write_text(
                ideas.read_text(encoding="utf-8") + "\nSee [[missing-page]].\n",
                encoding="utf-8",
            )

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr

            self.assertEqual(1, result.returncode, output)
            self.assertIn("severity: error", output)
            self.assertIn("code: broken_wikilink", output)
            self.assertIn(".llm-wiki/features/ideas.md", output)
            self.assertIn("missing-page", output)

    def test_lint_supports_alias_heading_and_md_wikilink_forms(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            overview = repo / ".llm-wiki" / "summaries" / "repo-overview.md"
            overview.write_text(
                "\n".join(
                    [
                        overview.read_text(encoding="utf-8"),
                        "Valid aliases: [[features/ideas|Ideas]]",
                        "Valid headings: [[features/ideas#Related links]]",
                        "Valid explicit suffix: [[features/ideas.md]]",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("No issues found in .llm-wiki/", output)

    def test_lint_rejects_parent_directory_wikilink_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            (repo / "outside.md").write_text("# Outside\n", encoding="utf-8")
            ideas = repo / ".llm-wiki" / "features" / "ideas.md"
            ideas.write_text(
                ideas.read_text(encoding="utf-8") + "\nEscape: [[../outside]].\n",
                encoding="utf-8",
            )

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr

            self.assertEqual(1, result.returncode, output)
            self.assertIn("code: broken_wikilink", output)
            self.assertIn("../outside", output)
            self.assertIn("stay inside .llm-wiki", output)

    def test_lint_does_not_follow_symlinked_wiki_file_outside_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            repo = parent / "repo"
            outside = parent / "outside.md"
            repo.mkdir()
            self.init_wiki(repo)
            outside.write_text("This escaped page has [[missing-page]].\n", encoding="utf-8")
            symlink = repo / ".llm-wiki" / "features" / "escaped.md"
            symlink.symlink_to(outside)

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("No issues found in .llm-wiki/", output)
            self.assertNotIn("missing-page", output)

    def test_lint_reports_unreadable_wiki_file_as_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            locked = repo / ".llm-wiki" / "features" / "locked.md"
            locked.write_text("[[features/ideas]]\n", encoding="utf-8")
            locked.chmod(0)
            try:
                result = self.run_helper(repo, "lint")
            finally:
                locked.chmod(0o644)
            output = result.stdout + result.stderr

            self.assertEqual(1, result.returncode, output)
            self.assertIn("severity: error", output)
            self.assertIn("code: unreadable_wiki_file", output)
            self.assertIn(".llm-wiki/features/locked.md", output)
            self.assertNotIn("Traceback", output)

    def test_lint_ignores_general_markdown_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            ideas = repo / ".llm-wiki" / "features" / "ideas.md"
            ideas.write_text(
                ideas.read_text(encoding="utf-8") + "\nNot checked: [Missing](missing.md).\n",
                encoding="utf-8",
            )

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("No issues found in .llm-wiki/", output)

    def test_lint_reports_missing_index_entry_as_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            glossary = repo / ".llm-wiki" / "domain" / "glossary.md"
            glossary.write_text("# Glossary\n", encoding="utf-8")

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("severity: warning", output)
            self.assertIn("code: missing_index_entry", output)
            self.assertIn(".llm-wiki/domain/glossary.md", output)
            self.assertIn("[[domain/glossary]]", output)

    def test_lint_reports_missing_raw_curated_readme_index_entry(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            index = repo / ".llm-wiki" / "index.md"
            index.write_text(
                index.read_text(encoding="utf-8").replace(
                    " and [[raw/curated/README]]", ""
                ),
                encoding="utf-8",
            )

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("severity: warning", output)
            self.assertIn("code: missing_index_entry", output)
            self.assertIn(".llm-wiki/raw/curated/README.md", output)
            self.assertIn("[[raw/curated/README]]", output)

    def test_lint_does_not_require_raw_curated_sources_in_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            source = repo / ".llm-wiki" / "raw" / "curated" / "source.md"
            source.write_text("# Source\n", encoding="utf-8")

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("No issues found in .llm-wiki/", output)
            self.assertNotIn("source.md", output)

    def test_lint_does_not_require_outgoing_links_on_topic_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            standalone = repo / ".llm-wiki" / "features" / "standalone.md"
            standalone.write_text("# Standalone\n\nNo outgoing links.\n", encoding="utf-8")
            index = repo / ".llm-wiki" / "index.md"
            index.write_text(
                index.read_text(encoding="utf-8") + "\n- Standalone: [[features/standalone]]\n",
                encoding="utf-8",
            )

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("No issues found in .llm-wiki/", output)

    def test_lint_reports_oversized_raw_file_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            oversized = repo / ".llm-wiki" / "raw" / "large.log"
            oversized.write_text("x" * (100 * 1024 + 1), encoding="utf-8")

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("severity: warning", output)
            self.assertIn("code: oversized_raw_file", output)
            self.assertIn(".llm-wiki/raw/large.log", output)
            self.assertIn("102400 bytes", output)

    def test_lint_does_not_size_check_non_raw_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            large_page = repo / ".llm-wiki" / "features" / "large.md"
            large_page.write_text("x" * (100 * 1024 + 1), encoding="utf-8")
            index = repo / ".llm-wiki" / "index.md"
            index.write_text(
                index.read_text(encoding="utf-8") + "\n- Large: [[features/large]]\n",
                encoding="utf-8",
            )

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("No issues found in .llm-wiki/", output)
            self.assertNotIn("oversized_raw_file", output)


if __name__ == "__main__":
    unittest.main()
