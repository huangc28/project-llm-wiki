from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "skills" / "project-llm-wiki"


class ProjectWikiPackageTests(unittest.TestCase):
    def run_helper(self, *args):
        return subprocess.run(
            [sys.executable, str(PACKAGE / "scripts" / "project_wiki.py"), *args],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_skill_file_documents_modes(self):
        skill = (PACKAGE / "SKILL.md").read_text()

        self.assertIn("project-wiki-init", skill)
        self.assertIn("project-wiki-lint", skill)
        self.assertIn("project-wiki-query", skill)
        self.assertIn("project-wiki-ingest", skill)

    def test_package_contract_states_local_boundary(self):
        contract = (PACKAGE / "references" / "package-contract.md").read_text()

        self.assertIn("Phase 1 does not install into global skill directories.", contract)

    def test_readme_points_to_skill_package(self):
        readme = (ROOT / "README.md").read_text()

        self.assertIn("skills/project-llm-wiki/SKILL.md", readme)

    def test_helper_help_exits_zero(self):
        result = self.run_helper("--help")

        self.assertEqual(0, result.returncode)
        self.assertIn("Repo-local .llm-wiki helper for Project LLM Wiki", result.stdout)
        self.assertIn(
            "query prepares index-first support packets; ingest updates curated wiki pages.",
            result.stdout,
        )
        self.assertNotIn("query and ingest remain planned for later phases", result.stdout)

    def test_lint_help_documents_json_flag(self):
        result = self.run_helper("lint", "--help")

        self.assertEqual(0, result.returncode)
        self.assertIn("--json", result.stdout)

    def test_query_help_documents_phase_4_flags(self):
        result = self.run_helper("query", "--help")

        self.assertEqual(0, result.returncode)
        for expected in (
            "--json",
            "--consulted",
            "--key-insight",
            "--not-covered",
            "--suggest-source",
        ):
            self.assertIn(expected, result.stdout)

    def test_ingest_help_documents_phase_4_flags(self):
        result = self.run_helper("ingest", "--help")

        self.assertEqual(0, result.returncode)
        for expected in (
            "--text",
            "--file",
            "--url",
            "--title",
            "--target-page",
            "--new-page",
            "--new-page-reason",
            "--key-idea",
            "--preserve-raw",
            "--summary-page",
            "--json",
        ):
            self.assertIn(expected, result.stdout)

    def test_command_surface_documents_completed_lint_contract(self):
        command_surface = (PACKAGE / "references" / "command-surface.md").read_text()

        self.assertIn("project-wiki lint --json", command_surface)
        self.assertIn("warning-only", command_surface)
        self.assertRegex(
            command_surface,
            r"severity.*code.*path.*message.*remediation",
        )
        self.assertNotIn("Lint and safety checks: Phase 3", command_surface)

    def test_command_surface_documents_completed_query_and_ingest_contract(self):
        command_surface = (PACKAGE / "references" / "command-surface.md").read_text()

        for expected in (
            "Implemented support mode for reading `.llm-wiki/index.md` first",
            "project-wiki query QUESTION",
            "project-wiki query QUESTION --consulted PAGE --key-insight TEXT",
            "Implemented mode for updating existing wiki pages",
            "project-wiki ingest --text TEXT --title TITLE --target-page PAGE --key-idea TEXT",
            "project-wiki ingest --url URL --text CURATED_TEXT --title TITLE --target-page PAGE --key-idea TEXT",
            "watch-video",
        ):
            self.assertIn(expected, command_surface)
        self.assertNotIn("Query and ingest loop: Phase 4", command_surface)

    def test_testing_reference_documents_phase_3_validation_contract(self):
        testing_reference = (PACKAGE / "references" / "testing.md").read_text()

        for expected in (
            "Phase 3 Validation Contract",
            "test_project_wiki_lint.py",
            "broken wikilinks",
            "missing index entries",
            "secret-looking content",
            "oversized raw files",
            "stale pages",
            "repo path drift",
            "read-only",
        ):
            self.assertIn(expected, testing_reference)

    def test_testing_reference_documents_phase_4_validation_contract(self):
        testing_reference = (PACKAGE / "references" / "testing.md").read_text()

        for expected in (
            "Phase 4 Validation Contract",
            "test_project_wiki_query.py",
            "test_project_wiki_ingest.py",
            "QUERY-01",
            "QUERY-04",
            "INGEST-01",
            "INGEST-05",
            "TEST-03",
            "video sources require transcript, summary, or curated notes",
        ):
            self.assertIn(expected, testing_reference)

    def test_helper_version_output(self):
        result = self.run_helper("version")

        self.assertEqual(0, result.returncode)
        self.assertIn("project-llm-wiki 0.1.0-foundation", result.stdout)

    def test_helper_init_refuses_non_git_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result = subprocess.run(
                [sys.executable, str(PACKAGE / "scripts" / "project_wiki.py"), "init"],
                cwd=tmp_path,
                capture_output=True,
                text=True,
                check=False,
            )
            output = result.stdout + result.stderr

            self.assertEqual(2, result.returncode, output)
            self.assertIn("No git repository found for current directory.", output)
            self.assertFalse((tmp_path / ".llm-wiki").exists())

    def test_helper_imports_only_allowed_modules(self):
        allowed = {
            "argparse",
            "datetime",
            "json",
            "pathlib",
            "re",
            "subprocess",
            "sys",
            "textwrap",
        }
        script = (PACKAGE / "scripts" / "project_wiki.py").read_text()
        imported = set()

        for line in script.splitlines():
            if line.startswith("import "):
                module = line.removeprefix("import ").split()[0].split(".")[0]
                imported.add(module)
            elif line.startswith("from "):
                module = line.removeprefix("from ").split()[0].split(".")[0]
                imported.add(module)

        self.assertTrue(imported)
        self.assertLessEqual(imported, allowed)

    def test_template_readme_lists_llm_wiki_inventory(self):
        template_readme = (PACKAGE / "assets" / "templates" / "README.md").read_text()

        self.assertIn("llm-wiki/README.md", template_readme)
        self.assertIn("llm-wiki/raw/curated/README.md", template_readme)
        self.assertIn("Templates must not contain secrets", template_readme)


if __name__ == "__main__":
    unittest.main()
