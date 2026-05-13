from pathlib import Path
import json
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

    def test_query_appends_log_entry_with_date_summary_pages_and_key_insight(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)

            result = self.run_helper(
                repo,
                "query",
                "What ideas are tracked?",
                "--consulted",
                "features/ideas",
                "--key-insight",
                "Ideas are tracked in the repo wiki.",
            )
            log_text = (repo / ".llm-wiki" / "log.md").read_text(encoding="utf-8")

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("] query | What ideas are tracked?", log_text)
            self.assertIn("Pages consulted: [[features/ideas]]", log_text)
            self.assertIn("Key insight: Ideas are tracked in the repo wiki.", log_text)

    def test_query_not_covered_log_lists_consulted_pages_and_source_suggestion(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)

            result = self.run_helper(
                repo,
                "query",
                "What does the wiki know about billing?",
                "--consulted",
                "features/ideas",
                "--not-covered",
                "--suggest-source",
                "architecture note",
            )
            log_text = (repo / ".llm-wiki" / "log.md").read_text(encoding="utf-8")

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("query | not-covered: What does the wiki know about billing?", log_text)
            self.assertIn("Pages consulted: [[features/ideas]]", log_text)
            self.assertIn("not currently cover", log_text)
            self.assertIn("architecture note", log_text)

    def test_query_log_does_not_store_full_answer_transcript(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            transcript = "\n\n".join(
                [
                    "This is the concise finding.",
                    "Full answer transcript with many details should not be stored.",
                    "Another paragraph that should be collapsed into bounded log text.",
                ]
            )

            result = self.run_helper(
                repo,
                "query",
                "Summarize ideas",
                "--consulted",
                "features/ideas",
                "--key-insight",
                transcript,
            )
            log_text = (repo / ".llm-wiki" / "log.md").read_text(encoding="utf-8")

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertNotIn("\n\nFull answer transcript", log_text)
            self.assertIn("- Key insight: This is the concise finding.", log_text)

    def test_query_log_normalizes_consulted_pages_to_wikilinks(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)

            result = self.run_helper(
                repo,
                "query",
                "What ideas are tracked?",
                "--consulted",
                "[[features/ideas.md]]",
                "--key-insight",
                "Ideas are tracked in the repo wiki.",
            )
            log_text = (repo / ".llm-wiki" / "log.md").read_text(encoding="utf-8")

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("Pages consulted: [[features/ideas]]", log_text)

    def test_seeded_query_fixture_supports_cited_answer_workflow(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            (repo / ".llm-wiki" / "features" / "ideas.md").write_text(
                "# Ideas\n\nIdeas are tracked in the repo wiki.\n",
                encoding="utf-8",
            )
            overview = repo / ".llm-wiki" / "summaries" / "repo-overview.md"
            overview.write_text(
                overview.read_text(encoding="utf-8")
                + "\nRelated evidence lives in [[features/ideas]].\n",
                encoding="utf-8",
            )

            result = self.run_helper(
                repo,
                "query",
                "What does the repo wiki know about ideas?",
            )
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("[[features/ideas]]", output)
            self.assertIn("Direct claims require [[wikilink]] citations.", output)
            self.assertNotIn("Final answer:", output)

    def test_seeded_query_fixture_appends_log_after_answer(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)

            result = self.run_helper(
                repo,
                "query",
                "What does the repo wiki know about ideas?",
                "--consulted",
                "features/ideas",
                "--key-insight",
                "Ideas are tracked in the repo wiki.",
            )
            log_text = (repo / ".llm-wiki" / "log.md").read_text(encoding="utf-8")

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("Pages consulted: [[features/ideas]]", log_text)
            self.assertIn("Key insight: Ideas are tracked in the repo wiki.", log_text)

    def test_seeded_query_not_covered_fixture_lists_pages_and_suggestion(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)

            result = self.run_helper(
                repo,
                "query",
                "What does the repo wiki know about billing?",
                "--consulted",
                "features/ideas",
                "--not-covered",
                "--suggest-source",
                "billing architecture note",
            )
            output = result.stdout + result.stderr
            log_text = (repo / ".llm-wiki" / "log.md").read_text(encoding="utf-8")

            self.assertEqual(0, result.returncode, output)
            self.assertIn("Not-covered template:", output)
            self.assertIn("Pages consulted: [[features/ideas]]", log_text)
            self.assertIn("billing architecture note", log_text)

    def test_seeded_query_json_packet_is_parseable(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)

            result = self.run_helper(
                repo,
                "query",
                "What does the repo wiki know about ideas?",
                "--json",
            )
            payload = json.loads(result.stdout)

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertEqual(".llm-wiki/index.md", payload["index_path"])
            self.assertIn("[[features/ideas]]", payload["candidate_pages"])
            self.assertIn(
                "Direct claims require [[wikilink]] citations.",
                payload["answer_contract"],
            )


if __name__ == "__main__":
    unittest.main()
