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


if __name__ == "__main__":
    unittest.main()
