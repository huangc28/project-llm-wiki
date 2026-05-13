from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "skills" / "project-llm-wiki"
HELPER = PACKAGE / "scripts" / "project_wiki.py"


class ProjectWikiIngestTests(unittest.TestCase):
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

    def test_ingest_accepts_curated_text_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)

            result = self.run_helper(
                repo,
                "ingest",
                "--text",
                "Curated source note about wiki query behavior.",
                "--title",
                "Query Note",
                "--target-page",
                "features/ideas",
                "--key-idea",
                "Query uses wiki evidence.",
            )
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("Ingest source accepted.", output)
            self.assertIn("Source kind: text", output)
            self.assertIn("Raw preservation: skipped", output)

    def test_ingest_accepts_file_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            source = repo / "source-note.md"
            source.write_text("Curated source note from a local file.\n", encoding="utf-8")

            result = self.run_helper(
                repo,
                "ingest",
                "--file",
                str(source),
                "--title",
                "File Source",
                "--target-page",
                "features/ideas",
                "--key-idea",
                "File sources can seed durable ideas.",
            )
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("Source kind: file", output)
            self.assertIn(str(source), output)

    def test_ingest_accepts_url_with_curated_text_as_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)

            result = self.run_helper(
                repo,
                "ingest",
                "--url",
                "https://example.com/design-note",
                "--text",
                "Curated summary from a stable URL.",
                "--title",
                "URL Source",
                "--target-page",
                "features/ideas",
                "--key-idea",
                "URL source is recorded as provenance.",
            )
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("Source kind: url", output)
            self.assertIn("https://example.com/design-note", output)

    def test_ingest_video_url_without_curated_text_requests_transcript(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)

            result = self.run_helper(
                repo,
                "ingest",
                "--url",
                "https://www.youtube.com/watch?v=abc123",
                "--title",
                "Video Source",
                "--target-page",
                "features/ideas",
                "--key-idea",
                "Video sources need preprocessing.",
            )
            output = result.stdout + result.stderr

            self.assertEqual(2, result.returncode, output)
            self.assertIn(
                "Provide a transcript, summary, or curated notes before ingesting video sources.",
                output,
            )

    def test_ingest_rejects_secret_like_raw_material(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)

            result = self.run_helper(
                repo,
                "ingest",
                "--text",
                "DATABASE_PASSWORD=super-secret-value",
                "--title",
                "Unsafe Source",
                "--target-page",
                "features/ideas",
                "--key-idea",
                "Unsafe material must be rejected.",
            )
            output = result.stdout + result.stderr

            self.assertEqual(2, result.returncode, output)
            self.assertIn("Unsafe raw material was not stored.", output)
            self.assertIn("secret-looking", output)

    def test_ingest_rejects_large_unreviewed_raw_material(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            large_text = "x" * (101 * 1024)

            result = self.run_helper(
                repo,
                "ingest",
                "--text",
                large_text,
                "--title",
                "Large Source",
                "--target-page",
                "features/ideas",
                "--key-idea",
                "Large source must be rejected.",
            )
            output = result.stdout + result.stderr

            self.assertEqual(2, result.returncode, output)
            self.assertIn("Unsafe raw material was not stored.", output)
            self.assertIn("larger than the raw size policy allows", output)

    def test_ingest_does_not_store_full_transcript_or_task_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)

            result = self.run_helper(
                repo,
                "ingest",
                "--text",
                "Full transcript from a call plus active task state checkpoint.",
                "--title",
                "Unsafe Transcript",
                "--target-page",
                "features/ideas",
                "--key-idea",
                "Unsafe transcript must be rejected.",
            )
            output = result.stdout + result.stderr

            self.assertEqual(2, result.returncode, output)
            self.assertIn("Unsafe raw material was not stored.", output)
            self.assertIn("transcripts, logs, dumps, private data, or active task state", output)

    def test_ingest_updates_existing_page_before_creating_new_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)

            result = self.run_helper(
                repo,
                "ingest",
                "--text",
                "Curated source note.",
                "--title",
                "Existing Page Source",
                "--target-page",
                "features/ideas",
                "--key-idea",
                "Existing pages receive the durable update first.",
            )
            ideas = (repo / ".llm-wiki" / "features" / "ideas.md").read_text(
                encoding="utf-8"
            )

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("Existing pages receive the durable update first.", ideas)
            self.assertFalse((repo / ".llm-wiki" / "features" / "new-page.md").exists())

    def test_ingest_requires_reason_before_creating_new_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)

            result = self.run_helper(
                repo,
                "ingest",
                "--text",
                "Curated source note.",
                "--title",
                "New Page Source",
                "--new-page",
                "features/new-topic",
                "--key-idea",
                "New page creation needs a reason.",
            )
            output = result.stdout + result.stderr

            self.assertEqual(2, result.returncode, output)
            self.assertIn("New page creation requires --new-page-reason.", output)

    def test_ingest_rejects_more_than_fifteen_touched_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            args = [
                "ingest",
                "--text",
                "Curated source note.",
                "--title",
                "Large Blast Radius",
                "--key-idea",
                "Too many pages should be rejected.",
            ]
            for index in range(16):
                args.extend(["--target-page", f"features/page-{index}"])

            result = self.run_helper(repo, *args)
            output = result.stdout + result.stderr

            self.assertEqual(2, result.returncode, output)
            self.assertIn("Ingest touches more than the 15 page hard cap.", output)

    def test_ingest_adds_provenance_to_every_touched_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            overview = repo / ".llm-wiki" / "summaries" / "repo-overview.md"

            result = self.run_helper(
                repo,
                "ingest",
                "--text",
                "Curated source note.",
                "--title",
                "Provenance Source",
                "--target-page",
                "features/ideas",
                "--target-page",
                "summaries/repo-overview",
                "--key-idea",
                "Every touched page receives provenance.",
            )
            ideas = (repo / ".llm-wiki" / "features" / "ideas.md").read_text(
                encoding="utf-8"
            )
            overview_text = overview.read_text(encoding="utf-8")

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("Updated from Provenance Source", ideas)
            self.assertIn("Updated from Provenance Source", overview_text)

    def test_ingest_updates_index_only_for_new_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            index_path = repo / ".llm-wiki" / "index.md"
            before = index_path.read_text(encoding="utf-8")

            existing_result = self.run_helper(
                repo,
                "ingest",
                "--text",
                "Curated source note.",
                "--title",
                "Existing Source",
                "--target-page",
                "features/ideas",
                "--key-idea",
                "Existing page update does not touch index.",
            )
            after_existing = index_path.read_text(encoding="utf-8")

            new_result = self.run_helper(
                repo,
                "ingest",
                "--text",
                "Curated source note.",
                "--title",
                "New Source",
                "--new-page",
                "features/new-topic",
                "--new-page-title",
                "New Topic",
                "--new-page-reason",
                "no existing page covers this concept",
                "--key-idea",
                "New page updates the index once.",
            )
            after_new = index_path.read_text(encoding="utf-8")

            self.assertEqual(0, existing_result.returncode, existing_result.stdout)
            self.assertEqual(before, after_existing)
            self.assertEqual(0, new_result.returncode, new_result.stdout)
            self.assertIn("[[features/new-topic]] - New Topic", after_new)

    def test_ingest_appends_log_with_pages_touched_and_key_idea(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)

            result = self.run_helper(
                repo,
                "ingest",
                "--text",
                "Curated source note.",
                "--title",
                "Log Source",
                "--target-page",
                "features/ideas",
                "--key-idea",
                "Ingest logs touched pages.",
            )
            log_text = (repo / ".llm-wiki" / "log.md").read_text(encoding="utf-8")

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("] ingest | Log Source", log_text)
            self.assertIn("Pages touched: [[features/ideas]]", log_text)
            self.assertIn("Key insight: Ingest logs touched pages.", log_text)

    def test_ingest_preserves_short_curated_raw_copy_when_requested(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)

            result = self.run_helper(
                repo,
                "ingest",
                "--text",
                "Short curated source note.",
                "--title",
                "Curated Raw Source",
                "--target-page",
                "features/ideas",
                "--key-idea",
                "Raw copies are optional and policy-gated.",
                "--preserve-raw",
            )
            raw_path = repo / ".llm-wiki" / "raw" / "curated" / "curated-raw-source.md"
            raw_text = raw_path.read_text(encoding="utf-8")

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertTrue(raw_path.is_file())
            self.assertIn("Provenance: inline text", raw_text)
            self.assertIn("Short curated source note.", raw_text)

    def test_ingest_prefers_existing_pages_over_new_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)

            result = self.run_helper(
                repo,
                "ingest",
                "--text",
                "Curated source note.",
                "--title",
                "Existing Preference Source",
                "--target-page",
                "features/ideas",
                "--key-idea",
                "Existing page update is preferred.",
            )
            ideas = (repo / ".llm-wiki" / "features" / "ideas.md").read_text(
                encoding="utf-8"
            )

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("Existing page update is preferred.", ideas)
            self.assertFalse((repo / ".llm-wiki" / "features" / "auto-created.md").exists())

    def test_ingest_creates_summary_page_only_with_cross_cutting_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)

            missing_flag = self.run_helper(
                repo,
                "ingest",
                "--text",
                "Curated source note.",
                "--title",
                "Summary Source",
                "--new-page",
                "summaries/source-note",
                "--new-page-reason",
                "cross-cutting source",
                "--key-idea",
                "Summary pages need the summary flag.",
            )
            summary_result = self.run_helper(
                repo,
                "ingest",
                "--text",
                "Curated source note.",
                "--title",
                "Summary Source",
                "--new-page",
                "summaries/source-note",
                "--new-page-reason",
                "cross-cutting source",
                "--summary-page",
                "--key-idea",
                "Summary pages capture cross-cutting sources.",
            )
            durable_result = self.run_helper(
                repo,
                "ingest",
                "--text",
                "Curated source note.",
                "--title",
                "Durable Page Source",
                "--new-page",
                "features/durable-note",
                "--new-page-reason",
                "no existing page covers this concept",
                "--key-idea",
                "Non-summary durable pages do not need the summary flag.",
            )

            self.assertEqual(2, missing_flag.returncode, missing_flag.stdout)
            self.assertIn("Summary pages require --summary-page.", missing_flag.stdout)
            self.assertEqual(0, summary_result.returncode, summary_result.stdout)
            self.assertTrue(
                (repo / ".llm-wiki" / "summaries" / "source-note.md").is_file()
            )
            self.assertEqual(0, durable_result.returncode, durable_result.stdout)
            self.assertTrue(
                (repo / ".llm-wiki" / "features" / "durable-note.md").is_file()
            )

    def test_ingest_new_page_adds_index_link_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)

            for key_idea in ("First durable idea.", "Second durable idea."):
                result = self.run_helper(
                    repo,
                    "ingest",
                    "--text",
                    "Curated source note.",
                    "--title",
                    "Index Source",
                    "--new-page",
                    "features/indexed-topic",
                    "--new-page-title",
                    "Indexed Topic",
                    "--new-page-reason",
                    "no existing page covers this concept",
                    "--key-idea",
                    key_idea,
                )
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)

            index_text = (repo / ".llm-wiki" / "index.md").read_text(encoding="utf-8")
            self.assertEqual(1, index_text.count("[[features/indexed-topic]]"))

    def test_ingest_raw_copy_is_optional(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)

            result = self.run_helper(
                repo,
                "ingest",
                "--text",
                "Short curated source note.",
                "--title",
                "Optional Raw Source",
                "--target-page",
                "features/ideas",
                "--key-idea",
                "Raw copy is optional.",
            )
            raw_path = repo / ".llm-wiki" / "raw" / "curated" / "optional-raw-source.md"

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertFalse(raw_path.exists())

    def test_ingest_url_provenance_does_not_fetch_or_store_full_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)

            result = self.run_helper(
                repo,
                "ingest",
                "--url",
                "https://example.com/source",
                "--title",
                "URL Only Source",
                "--target-page",
                "features/ideas",
                "--key-idea",
                "Stable URLs can be provenance only.",
            )
            raw_path = repo / ".llm-wiki" / "raw" / "curated" / "url-only-source.md"

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("Provenance: https://example.com/source", result.stdout)
            self.assertFalse(raw_path.exists())

    def test_ingest_boundary_rejects_parent_directory_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)

            result = self.run_helper(
                repo,
                "ingest",
                "--text",
                "Curated source note.",
                "--title",
                "Boundary Source",
                "--target-page",
                "../outside",
                "--key-idea",
                "Outside pages must be rejected.",
            )
            output = result.stdout + result.stderr

            self.assertEqual(2, result.returncode, output)
            self.assertIn("target must stay inside .llm-wiki", output)

    def test_ingest_boundary_rejects_checkpoint_or_full_log_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)

            result = self.run_helper(
                repo,
                "ingest",
                "--text",
                "Full log with execution checkpoint and active task state.",
                "--title",
                "Checkpoint Source",
                "--target-page",
                "features/ideas",
                "--key-idea",
                "Checkpoint text must be rejected.",
            )
            output = result.stdout + result.stderr

            self.assertEqual(2, result.returncode, output)
            self.assertIn("Unsafe raw material was not stored.", output)


if __name__ == "__main__":
    unittest.main()
