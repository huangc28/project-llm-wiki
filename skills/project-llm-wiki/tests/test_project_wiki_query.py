from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "skills" / "project-llm-wiki"
HELPER = PACKAGE / "scripts" / "project_wiki.py"


class ProjectWikiQueryTests(unittest.TestCase):
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

    def test_query_reads_index_first_and_lists_candidate_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)

            result = self.run_helper(repo, "query", "What ideas are tracked?")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("Index: .llm-wiki/index.md", output)
            self.assertIn("Candidate pages:", output)
            self.assertIn("[[features/ideas]]", output)
            self.assertIn("[[summaries/repo-overview]]", output)

    def test_query_output_states_wikilink_citation_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)

            result = self.run_helper(repo, "query", "What does the wiki cover?")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("Answer contract:", output)
            self.assertIn("Read .llm-wiki/index.md first.", output)
            self.assertIn("Direct claims require [[wikilink]] citations.", output)
            self.assertIn(
                "Put synthesis or inference under a labeled Inference section.",
                output,
            )

    def test_query_missing_wiki_returns_operational_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_repo(repo)

            result = self.run_helper(repo, "query", "What does the wiki cover?")
            output = result.stdout + result.stderr

            self.assertEqual(2, result.returncode, output)
            self.assertIn(
                "No .llm-wiki directory found in the resolved Git root.",
                output,
            )

    def test_query_missing_index_returns_operational_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            (repo / ".llm-wiki" / "index.md").unlink()

            result = self.run_helper(repo, "query", "What does the wiki cover?")
            output = result.stdout + result.stderr

            self.assertEqual(2, result.returncode, output)
            self.assertIn(
                "No .llm-wiki/index.md found in the resolved Git root.",
                output,
            )

    def test_query_helper_does_not_emit_final_answer_label(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)

            result = self.run_helper(repo, "query", "What does the wiki cover?")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertNotIn("Answer:", output)
            self.assertNotIn("Final answer:", output)
            self.assertNotIn("Final Answer:", output)


if __name__ == "__main__":
    unittest.main()
