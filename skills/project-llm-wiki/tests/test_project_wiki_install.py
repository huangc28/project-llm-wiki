from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "skills" / "project-llm-wiki"
HELPER = PACKAGE / "scripts" / "project_wiki.py"
SKILLS_ROOT = ROOT / "skills"
SKILL_NAMES = (
    "project-llm-wiki",
    "project-wiki-init",
    "project-wiki-lint",
    "project-wiki-query",
    "project-wiki-ingest",
)


class ProjectWikiInstallTests(unittest.TestCase):
    def run_install(self, *args):
        return subprocess.run(
            [sys.executable, str(HELPER), "install", *args],
            capture_output=True,
            text=True,
            check=False,
        )

    def make_target(self, tmp_path: Path) -> Path:
        codex_home = tmp_path / "codex"
        codex_home.mkdir()
        return codex_home / "skills"

    def assert_installed_links(self, target: Path):
        for name in SKILL_NAMES:
            with self.subTest(name=name):
                link = target / name
                self.assertTrue(link.is_symlink(), f"{link} is not a symlink")
                self.assertEqual((SKILLS_ROOT / name).resolve(), link.resolve())

    def test_fresh_install_creates_expected_skill_symlinks(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = self.make_target(Path(tmp))

            result = self.run_install("--target", str(target))

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assert_installed_links(target)

    def test_install_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = self.make_target(Path(tmp))

            first = self.run_install("--target", str(target))
            second = self.run_install("--target", str(target))

            self.assertEqual(0, first.returncode, first.stdout + first.stderr)
            self.assertEqual(0, second.returncode, second.stdout + second.stderr)
            self.assertIn("Skipped existing skills:", second.stdout)
            self.assert_installed_links(target)

    def test_dry_run_reports_plan_without_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = self.make_target(Path(tmp))

            result = self.run_install("--target", str(target), "--dry-run")

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("Would install skills:", result.stdout)
            self.assertFalse(target.exists())

    def test_existing_real_directory_aborts_without_partial_install(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = self.make_target(Path(tmp))
            target.mkdir()
            conflict = target / "project-wiki-init"
            conflict.mkdir()

            result = self.run_install("--target", str(target))

            self.assertEqual(2, result.returncode, result.stdout + result.stderr)
            self.assertIn("Conflicts:", result.stdout)
            self.assertTrue(conflict.is_dir())
            for name in SKILL_NAMES:
                if name == "project-wiki-init":
                    continue
                self.assertFalse((target / name).exists(), f"{name} was partially installed")

    def test_stale_symlink_requires_force_then_replaces(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            target = self.make_target(tmp_path)
            target.mkdir()
            stale_source = tmp_path / "stale-skill"
            stale_source.mkdir()
            stale_link = target / "project-wiki-init"
            stale_link.symlink_to(stale_source, target_is_directory=True)

            blocked = self.run_install("--target", str(target))
            forced = self.run_install("--target", str(target), "--force")

            self.assertEqual(2, blocked.returncode, blocked.stdout + blocked.stderr)
            self.assertEqual(0, forced.returncode, forced.stdout + forced.stderr)
            self.assertEqual((SKILLS_ROOT / "project-wiki-init").resolve(), stale_link.resolve())
            self.assert_installed_links(target)

    def test_uninstall_removes_only_package_owned_symlinks(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            target = self.make_target(tmp_path)
            install = self.run_install("--target", str(target))
            self.assertEqual(0, install.returncode, install.stdout + install.stderr)
            foreign_source = tmp_path / "foreign-skill"
            foreign_source.mkdir()
            foreign_link = target / "project-wiki-query"
            foreign_link.unlink()
            foreign_link.symlink_to(foreign_source, target_is_directory=True)

            result = self.run_install("--target", str(target), "--uninstall")

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            for name in SKILL_NAMES:
                link = target / name
                if name == "project-wiki-query":
                    self.assertTrue(link.is_symlink())
                    self.assertEqual(foreign_source.resolve(), link.resolve())
                else:
                    self.assertFalse(link.exists(), f"{name} was not removed")

    def test_install_does_not_initialize_repo_or_modify_root_agents(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = self.make_target(Path(tmp))
            agents_path = ROOT / "AGENTS.md"
            agents_before = agents_path.read_bytes()

            result = self.run_install("--target", str(target))

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertFalse((ROOT / ".llm-wiki").exists())
            self.assertEqual(agents_before, agents_path.read_bytes())


if __name__ == "__main__":
    unittest.main()
