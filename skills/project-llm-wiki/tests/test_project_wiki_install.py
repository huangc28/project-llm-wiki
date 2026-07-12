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
MARKER_FILE = ".project-llm-wiki-install.json"


def snapshot_tree(root: Path):
    """Content snapshot of a directory tree, or None if it does not exist.

    Maps every descendant path (relative to root) to its file bytes; directories
    map to None. Comparing two snapshots detects any create/delete/modify.
    """
    if not root.exists():
        return None
    snapshot = {}
    for path in sorted(root.rglob("*")):
        rel = str(path.relative_to(root))
        snapshot[rel] = path.read_bytes() if path.is_file() else None
    return snapshot


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

    def assert_installed_skill_dirs(self, target: Path):
        for name in SKILL_NAMES:
            with self.subTest(name=name):
                skill_dir = target / name
                self.assertTrue(skill_dir.is_dir(), f"{skill_dir} is not a directory")
                self.assertFalse(skill_dir.is_symlink(), f"{skill_dir} is a symlink")
                self.assertTrue((skill_dir / "SKILL.md").is_file())
                marker = skill_dir / MARKER_FILE
                self.assertTrue(marker.is_file(), f"{marker} is missing")
                self.assertIn(f'"skill": "{name}"', marker.read_text())

    def test_fresh_install_creates_expected_skill_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = self.make_target(Path(tmp))

            result = self.run_install("--target", str(target))

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assert_installed_skill_dirs(target)

    def test_install_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = self.make_target(Path(tmp))

            first = self.run_install("--target", str(target))
            second = self.run_install("--target", str(target))

            self.assertEqual(0, first.returncode, first.stdout + first.stderr)
            self.assertEqual(0, second.returncode, second.stdout + second.stderr)
            self.assertIn("Updated installed skills:", second.stdout)
            self.assert_installed_skill_dirs(target)

    def test_dry_run_reports_plan_without_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = self.make_target(Path(tmp))

            result = self.run_install("--target", str(target), "--dry-run")

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("Would install skills:", result.stdout)
            self.assertFalse(target.exists())

    def test_existing_unmarked_directory_aborts_without_partial_install(self):
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

    def test_existing_symlink_requires_force_then_replaces_with_directory(self):
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
            self.assertFalse(stale_link.is_symlink())
            self.assertTrue((stale_link / "SKILL.md").is_file())
            self.assert_installed_skill_dirs(target)

    def test_uninstall_removes_only_marker_owned_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            target = self.make_target(tmp_path)
            install = self.run_install("--target", str(target))
            self.assertEqual(0, install.returncode, install.stdout + install.stderr)
            foreign_dir = target / "project-wiki-query"
            marker = foreign_dir / MARKER_FILE
            marker.unlink()
            (foreign_dir / "custom.txt").write_text("foreign")

            result = self.run_install("--target", str(target), "--uninstall")

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            for name in SKILL_NAMES:
                skill_dir = target / name
                if name == "project-wiki-query":
                    self.assertTrue(skill_dir.is_dir())
                    self.assertEqual("foreign", (skill_dir / "custom.txt").read_text())
                else:
                    self.assertFalse(skill_dir.exists(), f"{name} was not removed")

    def test_uninstall_preserves_foreign_symlinks(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            target = self.make_target(tmp_path)
            target.mkdir()
            foreign_source = tmp_path / "foreign-skill"
            foreign_source.mkdir()
            foreign_link = target / "project-wiki-query"
            foreign_link.symlink_to(foreign_source, target_is_directory=True)

            result = self.run_install("--target", str(target), "--uninstall")

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertTrue(foreign_link.is_symlink())
            self.assertEqual(foreign_source.resolve(), foreign_link.resolve())

    def test_install_does_not_initialize_repo_or_modify_root_agents(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = self.make_target(Path(tmp))
            agents_path = ROOT / "AGENTS.md"
            agents_before = agents_path.read_bytes()
            # Install must not create OR modify the repo's own .llm-wiki/. Snapshot
            # it before/after rather than asserting absolute absence — the repo now
            # commits its own .llm-wiki/ skeleton at HEAD.
            wiki_path = ROOT / ".llm-wiki"
            wiki_before = snapshot_tree(wiki_path)

            result = self.run_install("--target", str(target))

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertEqual(wiki_before, snapshot_tree(wiki_path))
            self.assertEqual(agents_before, agents_path.read_bytes())


if __name__ == "__main__":
    unittest.main()
