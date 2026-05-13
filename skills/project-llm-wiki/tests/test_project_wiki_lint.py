from pathlib import Path
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


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

    def snapshot_wiki_files(self, repo: Path):
        wiki_root = repo / ".llm-wiki"
        snapshot = {}
        for path in sorted(wiki_root.rglob("*")):
            if path.is_symlink() or not path.is_file():
                continue
            snapshot[path.relative_to(repo).as_posix()] = path.read_bytes()
        return snapshot

    def load_helper_module(self):
        spec = importlib.util.spec_from_file_location("project_wiki_under_test", HELPER)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

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

    def test_lint_text_output_includes_fixed_finding_fields(self):
        helper = self.load_helper_module()
        self.assertTrue(hasattr(helper, "render_text_findings"))

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
            stripped_lines = [line.strip() for line in output.splitlines()]

            self.assertEqual(1, result.returncode, output)
            for label in (
                "severity:",
                "code:",
                "path:",
                "message:",
                "remediation:",
            ):
                self.assertTrue(
                    any(line.startswith(label) for line in stripped_lines), output
                )

    def test_lint_json_output_uses_fixed_finding_fields(self):
        helper = self.load_helper_module()
        self.assertTrue(hasattr(helper, "render_json_findings"))

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            ideas = repo / ".llm-wiki" / "features" / "ideas.md"
            ideas.write_text(
                ideas.read_text(encoding="utf-8") + "\nSee [[missing-page]].\n",
                encoding="utf-8",
            )

            result = self.run_helper(repo, "lint", "--json")
            payload = json.loads(result.stdout)

            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertEqual("", result.stderr)
            self.assertEqual(["findings"], list(payload.keys()))
            self.assertTrue(payload["findings"])
            self.assertEqual(
                {"severity", "code", "path", "message", "remediation"},
                set(payload["findings"][0].keys()),
            )
            self.assertEqual("error", payload["findings"][0]["severity"])

    def test_lint_json_success_outputs_empty_findings(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)

            result = self.run_helper(repo, "lint", "--json")
            payload = json.loads(result.stdout)

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertEqual("", result.stderr)
            self.assertEqual({"findings": []}, payload)

    def test_lint_exit_code_is_one_only_when_error_exists(self):
        helper = self.load_helper_module()

        self.assertEqual(0, helper.lint_exit_code([]))
        self.assertEqual(
            0,
            helper.lint_exit_code(
                [
                    helper.make_finding(
                        "warning",
                        "missing_index_entry",
                        ".llm-wiki/features/ideas.md",
                        "Main wiki page is not linked from .llm-wiki/index.md.",
                        "Add [[features/ideas]] to .llm-wiki/index.md.",
                    )
                ]
            ),
        )
        self.assertEqual(
            1,
            helper.lint_exit_code(
                [
                    helper.make_finding(
                        "error",
                        "broken_wikilink",
                        ".llm-wiki/features/ideas.md",
                        "Wikilink points to missing page.",
                        "Create the page or update the wikilink.",
                    )
                ]
            ),
        )

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

    def test_lint_supports_dotted_markdown_page_wikilinks(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            dotted = repo / ".llm-wiki" / "features" / "api.v2.md"
            dotted.write_text("# API v2\n", encoding="utf-8")
            index = repo / ".llm-wiki" / "index.md"
            index.write_text(
                index.read_text(encoding="utf-8") + "\n- API v2: [[features/api.v2]]\n",
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

    def test_lint_reports_unreadable_markdown_file_once_without_index_noise(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            locked = repo / ".llm-wiki" / "features" / "locked.md"
            locked.write_text("[[features/ideas]]\n", encoding="utf-8")
            locked.chmod(0)
            try:
                result = self.run_helper(repo, "lint", "--json")
            finally:
                locked.chmod(0o644)
            payload = json.loads(result.stdout)
            locked_findings = [
                finding
                for finding in payload["findings"]
                if finding["path"] == ".llm-wiki/features/locked.md"
            ]

            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertEqual("", result.stderr)
            self.assertEqual(1, len(locked_findings), payload)
            self.assertEqual("unreadable_wiki_file", locked_findings[0]["code"])
            self.assertNotIn(
                "missing_index_entry",
                {finding["code"] for finding in payload["findings"]},
            )

    def test_lint_reports_unreadable_index_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            index = repo / ".llm-wiki" / "index.md"
            index.chmod(0)
            try:
                result = self.run_helper(repo, "lint", "--json")
            finally:
                index.chmod(0o644)
            payload = json.loads(result.stdout)
            index_findings = [
                finding
                for finding in payload["findings"]
                if finding["path"] == ".llm-wiki/index.md"
            ]

            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertEqual("", result.stderr)
            self.assertEqual(1, len(index_findings), payload)
            self.assertEqual("unreadable_wiki_file", index_findings[0]["code"])

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

    def test_missing_index_entry_fixture_covers_test_04(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            index = repo / ".llm-wiki" / "index.md"
            index.write_text(
                index.read_text(encoding="utf-8").replace(
                    "- Durable ideas: [[features/ideas]]\n", ""
                ),
                encoding="utf-8",
            )

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("missing_index_entry", output)
            self.assertIn("warning", output)
            self.assertIn(".llm-wiki/features/ideas.md", output)
            self.assertIn(".llm-wiki/index.md", output)

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

    def test_lint_reports_secret_like_raw_content_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            unsafe = repo / ".llm-wiki" / "raw" / "curated" / "unsafe.md"
            unsafe.write_text(
                "-----BEGIN OPENSSH PRIVATE KEY-----\nkey-body\n-----END OPENSSH PRIVATE KEY-----\n",
                encoding="utf-8",
            )

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("severity: warning", output)
            self.assertIn("code: secret_like_content", output)
            self.assertIn(".llm-wiki/raw/curated/unsafe.md", output)
            self.assertIn("redact", output)

    def test_lint_reports_secret_like_non_markdown_raw_file_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            unsafe = repo / ".llm-wiki" / "raw" / "curated" / "unsafe.env"
            unsafe.write_text(
                "DATABASE_URL=postgres://wiki_user:wiki_pass@example.invalid/db\n",
                encoding="utf-8",
            )

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("severity: warning", output)
            self.assertIn("code: secret_like_content", output)
            self.assertIn(".llm-wiki/raw/curated/unsafe.env", output)
            self.assertIn("redact", output)

    def test_lint_reports_key_value_secret_in_markdown_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            ideas = repo / ".llm-wiki" / "features" / "ideas.md"
            ideas.write_text(
                ideas.read_text(encoding="utf-8")
                + "\nDo not keep OPENAI_API_KEY=sk-liveexample01234567890 here.\n",
                encoding="utf-8",
            )

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("code: secret_like_content", output)
            self.assertIn(".llm-wiki/features/ideas.md", output)

    def test_lint_reports_key_value_secret_in_non_markdown_raw_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            unsafe = repo / ".llm-wiki" / "raw" / "curated" / "unsafe.env"
            unsafe.write_text(
                "AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\n",
                encoding="utf-8",
            )

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("code: secret_like_content", output)
            self.assertIn(".llm-wiki/raw/curated/unsafe.env", output)

    def test_lint_reports_multi_component_env_secret_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            unsafe = repo / ".llm-wiki" / "raw" / "curated" / "secrets.env"
            unsafe.write_text(
                "\n".join(
                    [
                        "DATABASE_PASSWORD=prod-db-password",
                        "SLACK_BOT_TOKEN=xoxb-123456789012-abcdefghijklmnop",
                        "STRIPE_SECRET_KEY=sk_live_12345678901234567890",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("code: secret_like_content", output)
            self.assertIn(".llm-wiki/raw/curated/secrets.env", output)

    def test_lint_reports_common_pass_env_secret_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            unsafe = repo / ".llm-wiki" / "raw" / "curated" / "db.env"
            unsafe.write_text(
                "\n".join(
                    [
                        "DB_PASS=prod-db-password",
                        "PGPASSWORD=prod-pg-password",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("code: secret_like_content", output)
            self.assertIn(".llm-wiki/raw/curated/db.env", output)

    def test_lint_reports_bare_github_fine_grained_pat(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            unsafe = repo / ".llm-wiki" / "raw" / "curated" / "unsafe.log"
            unsafe.write_text(
                "Leaked token: github_pat_1234567890abcdefghijklmnopqrstuvwxyz\n",
                encoding="utf-8",
            )

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("code: secret_like_content", output)
            self.assertIn(".llm-wiki/raw/curated/unsafe.log", output)

    def test_lint_allows_placeholder_multi_component_secret_examples(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            example = repo / ".llm-wiki" / "raw" / "curated" / "placeholders.env"
            example.write_text(
                "\n".join(
                    [
                        "DATABASE_PASSWORD=REDACTED",
                        "SLACK_BOT_TOKEN=changeme",
                        "STRIPE_SECRET_KEY=your-token",
                        "DB_PASS=REDACTED",
                        "PGPASSWORD=changeme",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("No issues found in .llm-wiki/", output)

    def test_lint_allows_placeholder_key_value_secret_examples(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            example = repo / ".llm-wiki" / "raw" / "curated" / "example.env"
            example.write_text("API_KEY=REDACTED\nTOKEN=changeme\n", encoding="utf-8")

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("No issues found in .llm-wiki/", output)

    def test_secret_like_raw_file_fixture_covers_test_05(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            unsafe = repo / ".llm-wiki" / "raw" / "curated" / "unsafe.env"
            unsafe.write_text(
                "DATABASE_URL=postgres://wiki_user:wiki_pass@example.invalid/db\n",
                encoding="utf-8",
            )

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("secret_like_content", output)
            self.assertIn("warning", output)
            self.assertIn(".llm-wiki/raw/curated/unsafe.env", output)
            self.assertIn("redact", output)

    def test_lint_scans_secret_like_content_outside_raw(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            ideas = repo / ".llm-wiki" / "features" / "ideas.md"
            ideas.write_text(
                ideas.read_text(encoding="utf-8")
                + "\nCredential URL: https://agent:secret@example.invalid/private\n",
                encoding="utf-8",
            )

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("code: secret_like_content", output)
            self.assertIn(".llm-wiki/features/ideas.md", output)

    def test_lint_default_raw_policy_does_not_trigger_secret_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("No issues found in .llm-wiki/", output)
            self.assertNotIn("secret_like_content", output)

    def test_lint_secret_scan_does_not_follow_symlink_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            repo = parent / "repo"
            repo.mkdir()
            outside = parent / "outside.env"
            outside.write_text(
                "DATABASE_URL=postgres://wiki_user:wiki_pass@example.invalid/db\n",
                encoding="utf-8",
            )
            self.init_wiki(repo)
            symlink = repo / ".llm-wiki" / "raw" / "curated" / "escaped.env"
            symlink.symlink_to(outside)

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("No issues found in .llm-wiki/", output)
            self.assertNotIn("secret_like_content", output)

    def test_lint_reports_unreadable_wiki_file_for_all_file_scan(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            locked = repo / ".llm-wiki" / "raw" / "curated" / "locked.env"
            locked.write_text(
                "DATABASE_URL=postgres://user:pass@example.invalid/db\n",
                encoding="utf-8",
            )
            locked.chmod(0)
            try:
                result = self.run_helper(repo, "lint")
            finally:
                locked.chmod(0o644)
            output = result.stdout + result.stderr

            self.assertEqual(1, result.returncode, output)
            self.assertIn("severity: error", output)
            self.assertIn("code: unreadable_wiki_file", output)
            self.assertIn(".llm-wiki/raw/curated/locked.env", output)
            self.assertNotIn("Traceback", output)

    def test_collect_wiki_files_reports_unreadable_directory(self):
        helper = self.load_helper_module()

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            locked_dir = repo / ".llm-wiki" / "raw" / "locked-dir"
            locked_dir.mkdir()
            original_iterdir = Path.iterdir

            def fake_iterdir(path):
                if path == locked_dir:
                    raise OSError("permission denied")
                return original_iterdir(path)

            with mock.patch.object(Path, "iterdir", fake_iterdir):
                _files, findings = helper.collect_wiki_files(repo)

            self.assertTrue(
                any(
                    finding["code"] == "unreadable_wiki_directory"
                    and finding["path"] == ".llm-wiki/raw/locked-dir"
                    for finding in findings
                ),
                findings,
            )

    def test_lint_reports_stale_updated_frontmatter_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            ideas = repo / ".llm-wiki" / "features" / "ideas.md"
            ideas.write_text(
                "---\nupdated: 2000-01-01\n---\n"
                + ideas.read_text(encoding="utf-8"),
                encoding="utf-8",
            )

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("severity: warning", output)
            self.assertIn("code: stale_page", output)
            self.assertIn(".llm-wiki/features/ideas.md", output)
            self.assertIn("review", output)
            self.assertIn("current repo files", output)

    def test_lint_ignores_pages_without_updated_frontmatter(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("No issues found in .llm-wiki/", output)
            self.assertNotIn("stale_page", output)

    def test_warning_only_secret_and_stale_findings_exit_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            ideas = repo / ".llm-wiki" / "features" / "ideas.md"
            ideas.write_text(
                "---\nupdated: 2000-01-01\n---\n"
                + ideas.read_text(encoding="utf-8")
                + "\nCredential URL: https://agent:secret@example.invalid/private\n",
                encoding="utf-8",
            )

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("code: secret_like_content", output)
            self.assertIn("code: stale_page", output)

    def test_lint_reports_missing_repo_path_from_inline_code_span(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            ideas = repo / ".llm-wiki" / "features" / "ideas.md"
            ideas.write_text(
                ideas.read_text(encoding="utf-8")
                + "\nImplementation lives in `src/missing.py`.\n",
                encoding="utf-8",
            )

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("severity: warning", output)
            self.assertIn("code: missing_repo_path", output)
            self.assertIn(".llm-wiki/features/ideas.md", output)
            self.assertIn("src/missing.py", output)

    def test_lint_reports_missing_repo_path_from_fenced_code_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            ideas = repo / ".llm-wiki" / "features" / "ideas.md"
            ideas.write_text(
                ideas.read_text(encoding="utf-8")
                + "\n```text\nsrc/missing.py\n```\n",
                encoding="utf-8",
            )

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("code: missing_repo_path", output)
            self.assertIn("src/missing.py", output)

    def test_lint_reports_missing_repo_path_from_tilde_fenced_code_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            ideas = repo / ".llm-wiki" / "features" / "ideas.md"
            ideas.write_text(
                ideas.read_text(encoding="utf-8")
                + "\n~~~text\nsrc/missing.py\n~~~\n",
                encoding="utf-8",
            )

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("code: missing_repo_path", output)
            self.assertIn("src/missing.py", output)

    def test_lint_keeps_backtick_fence_open_across_tilde_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            ideas = repo / ".llm-wiki" / "features" / "ideas.md"
            ideas.write_text(
                ideas.read_text(encoding="utf-8")
                + "\n```markdown\n~~~text\nsrc/missing.py\n```\n",
                encoding="utf-8",
            )

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("code: missing_repo_path", output)
            self.assertIn("src/missing.py", output)

    def test_lint_keeps_tilde_fence_open_across_backtick_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            ideas = repo / ".llm-wiki" / "features" / "ideas.md"
            ideas.write_text(
                ideas.read_text(encoding="utf-8")
                + "\n~~~markdown\n```text\nsrc/missing.py\n~~~\n",
                encoding="utf-8",
            )

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("code: missing_repo_path", output)
            self.assertIn("src/missing.py", output)

    def test_lint_ignores_repo_path_like_text_in_plain_prose(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            ideas = repo / ".llm-wiki" / "features" / "ideas.md"
            ideas.write_text(
                ideas.read_text(encoding="utf-8")
                + "\nPlain prose mentions src/missing.py as an example.\n",
                encoding="utf-8",
            )

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("No issues found in .llm-wiki/", output)
            self.assertNotIn("missing_repo_path", output)

    def test_lint_ignores_outside_repo_path_drift_candidates(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            ideas = repo / ".llm-wiki" / "features" / "ideas.md"
            ideas.write_text(
                ideas.read_text(encoding="utf-8")
                + "\nIgnored: `../outside.txt`, `/etc/passwd`, and `~/secret.txt`.\n",
                encoding="utf-8",
            )

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("No issues found in .llm-wiki/", output)
            self.assertNotIn("missing_repo_path", output)

    def test_lint_ignores_outside_repo_paths_in_plain_prose(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            ideas = repo / ".llm-wiki" / "features" / "ideas.md"
            ideas.write_text(
                ideas.read_text(encoding="utf-8")
                + "\nPlain prose can mention /tmp/example.txt or ../outside.txt.\n",
                encoding="utf-8",
            )

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("No issues found in .llm-wiki/", output)
            self.assertNotIn("missing_repo_path", output)

    def test_lint_does_not_warn_for_existing_repo_path_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            source = repo / "src" / "app.py"
            source.parent.mkdir()
            source.write_text("print('ok')\n", encoding="utf-8")
            ideas = repo / ".llm-wiki" / "features" / "ideas.md"
            ideas.write_text(
                ideas.read_text(encoding="utf-8")
                + "\nExisting implementation: `src/app.py`.\n",
                encoding="utf-8",
            )

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("No issues found in .llm-wiki/", output)
            self.assertNotIn("missing_repo_path", output)

    def test_lint_does_not_warn_for_existing_repo_path_line_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            source = repo / "src" / "app.py"
            source.parent.mkdir()
            source.write_text("print('ok')\n", encoding="utf-8")
            ideas = repo / ".llm-wiki" / "features" / "ideas.md"
            ideas.write_text(
                ideas.read_text(encoding="utf-8")
                + "\nExisting implementation: `src/app.py:12`.\n",
                encoding="utf-8",
            )

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("No issues found in .llm-wiki/", output)
            self.assertNotIn("missing_repo_path", output)

    def test_warning_only_repo_path_drift_exits_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            ideas = repo / ".llm-wiki" / "features" / "ideas.md"
            ideas.write_text(
                ideas.read_text(encoding="utf-8")
                + "\nOutdated implementation: `docs/missing.md`.\n",
                encoding="utf-8",
            )

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr

            self.assertEqual(0, result.returncode, output)
            self.assertIn("code: missing_repo_path", output)

    def test_lint_warning_runs_are_read_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            index = repo / ".llm-wiki" / "index.md"
            index.write_text(
                index.read_text(encoding="utf-8").replace(
                    "- Durable ideas: [[features/ideas]]\n", ""
                ),
                encoding="utf-8",
            )
            before = self.snapshot_wiki_files(repo)

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr
            after = self.snapshot_wiki_files(repo)

            self.assertEqual(0, result.returncode, output)
            self.assertIn("missing_index_entry", output)
            self.assertEqual(before, after)

    def test_lint_error_runs_are_read_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.init_wiki(repo)
            ideas = repo / ".llm-wiki" / "features" / "ideas.md"
            ideas.write_text(
                ideas.read_text(encoding="utf-8") + "\nSee [[missing-page]].\n",
                encoding="utf-8",
            )
            before = self.snapshot_wiki_files(repo)

            result = self.run_helper(repo, "lint")
            output = result.stdout + result.stderr
            after = self.snapshot_wiki_files(repo)

            self.assertEqual(1, result.returncode, output)
            self.assertIn("broken_wikilink", output)
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
