from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "skills" / "project-llm-wiki"
HELPER = PACKAGE / "scripts" / "project_wiki.py"


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
            self.assertTrue((repo / ".llm-wiki" / "README.md").exists())
            self.assertTrue((repo / ".llm-wiki" / "index.md").exists())
            self.assertTrue((repo / ".llm-wiki" / "raw" / "README.md").exists())
            self.assertTrue((repo / ".llm-wiki" / "raw" / "curated" / "README.md").exists())
            self.assertTrue((repo / ".llm-wiki" / "features" / "ideas.md").exists())
            self.assertTrue((repo / ".llm-wiki" / "summaries" / "repo-overview.md").exists())
            self.assertTrue((repo / ".llm-wiki" / "architecture" / ".gitkeep").exists())
            self.assertTrue((repo / ".llm-wiki" / "domain" / ".gitkeep").exists())
            self.assertTrue((repo / ".llm-wiki" / "decisions" / ".gitkeep").exists())
            self.assertTrue((repo / ".llm-wiki" / "operations" / ".gitkeep").exists())
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


if __name__ == "__main__":
    unittest.main()
