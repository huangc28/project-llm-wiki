import datetime
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[3]
HELPER = ROOT / "skills" / "project-llm-wiki" / "scripts" / "project_wiki.py"

VAULT_CONTENT_DIRS = ("projects", "daily_notes", "raw", "Ideas", "skills")
VAULT_CONTROL_FILES = ("index.md", "log.md")


class VaultProfileTests(unittest.TestCase):
    def run_helper(self, *args, cwd=None):
        return subprocess.run(
            [sys.executable, str(HELPER), *args],
            capture_output=True,
            text=True,
            check=False,
            cwd=cwd,
        )

    # ----- init -----

    def test_vault_init_builds_skeleton_idempotently(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = self.run_helper("init", "--profile", "vault", "--root", str(root))
            self.assertEqual(0, first.returncode, first.stdout + first.stderr)

            for name in VAULT_CONTENT_DIRS:
                self.assertTrue((root / name).is_dir(), f"missing dir {name}")
            for name in VAULT_CONTROL_FILES:
                self.assertTrue((root / name).is_file(), f"missing file {name}")

            # A second run must be a pure no-op: nothing created, existing content
            # preserved byte-for-byte.
            marker = "MARKER-DO-NOT-CLOBBER"
            index_path = root / "index.md"
            index_path.write_text(index_path.read_text() + f"\n{marker}\n")

            second = self.run_helper("init", "--profile", "vault", "--root", str(root))
            self.assertEqual(0, second.returncode, second.stdout + second.stderr)
            self.assertIn(marker, index_path.read_text(), "second init clobbered index.md")
            self.assertIn("Created paths:", second.stdout)
            created_block = second.stdout.split("Created paths:", 1)[1].split("Skipped", 1)[0]
            self.assertIn("(none)", created_block, "second init created new paths")

    def test_vault_init_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = self.run_helper(
                "init", "--profile", "vault", "--root", str(root), "--dry-run"
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("Would create", result.stdout)
            for name in VAULT_CONTENT_DIRS:
                self.assertFalse((root / name).exists(), f"dry-run created dir {name}")
            for name in VAULT_CONTROL_FILES:
                self.assertFalse((root / name).exists(), f"dry-run created file {name}")

    def test_vault_init_requires_root(self):
        result = self.run_helper("init", "--profile", "vault")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("--root", result.stdout + result.stderr)

    def test_vault_init_does_not_affect_project_profile(self):
        # The default (project) profile still refuses a non-git directory.
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_helper("init", cwd=tmp)
            self.assertEqual(2, result.returncode, result.stdout + result.stderr)
            self.assertIn("No git repository found", result.stdout + result.stderr)

    # ----- lint -----

    def init_vault(self, root: Path):
        result = self.run_helper("init", "--profile", "vault", "--root", str(root))
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def lint_vault_json(self, root: Path):
        result = self.run_helper(
            "lint", "--profile", "vault", "--root", str(root), "--json"
        )
        payload = json.loads(result.stdout)
        return result, payload["findings"]

    def test_vault_lint_clean_skeleton_is_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_vault(root)
            result, findings = self.lint_vault_json(root)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertEqual([], findings, findings)

    def test_vault_lint_reports_structural_findings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_vault(root)

            # Link linker + stale in the index so only `orphan` is missing.
            (root / "index.md").write_text(
                "# Vault Index\n\n- [[projects/linker]]\n- [[projects/stale]]\n"
            )
            # Durable page absent from the index -> missing_index_entry.
            (root / "projects" / "orphan.md").write_text("# Orphan\n\nDurable page.\n")
            # Linked page with a dangling wikilink -> broken_wikilink (error).
            (root / "projects" / "linker.md").write_text("# Linker\n\nSee [[projects/ghost]].\n")
            # Stale page (older than the vault 30-day horizon).
            stale_date = (datetime.date.today() - datetime.timedelta(days=45)).isoformat()
            (root / "projects" / "stale.md").write_text(
                f"---\nupdated: {stale_date}\n---\n# Stale\n\nOld.\n"
            )
            # Oversized raw file.
            (root / "raw" / "big.md").write_text("a\n" * 60000)
            # Secret-looking raw content.
            (root / "raw" / "leak.md").write_text(
                "# Leak\n\naws_secret_access_key = AKIAIOSFODNN7EXAMPLEXYZ12\n"
            )
            # Excluded directory content must be ignored entirely.
            obsidian = root / ".obsidian"
            obsidian.mkdir()
            (obsidian / "secret.md").write_text(
                "password = hunter2primeval-not-placeholder\n"
            )

            result, findings = self.lint_vault_json(root)
            codes = {f["code"] for f in findings}
            self.assertIn("broken_wikilink", codes)
            self.assertIn("missing_index_entry", codes)
            self.assertIn("oversized_raw_file", codes)
            self.assertIn("stale_page", codes)
            self.assertIn("secret_like_content", codes)
            # Broken wikilink is an error -> exit 1.
            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            # Nothing under the excluded directory may be reported.
            self.assertFalse(
                any(".obsidian" in f["path"] for f in findings),
                f"excluded dir leaked into findings: {findings}",
            )

    def test_vault_lint_stale_horizon_is_30_days(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_vault(root)
            (root / "index.md").write_text(
                "# Vault Index\n\n- [[projects/old]]\n- [[projects/recent]]\n"
            )
            old_date = (datetime.date.today() - datetime.timedelta(days=40)).isoformat()
            recent_date = (datetime.date.today() - datetime.timedelta(days=20)).isoformat()
            (root / "projects" / "old.md").write_text(
                f"---\nupdated: {old_date}\n---\n# Old\n"
            )
            (root / "projects" / "recent.md").write_text(
                f"---\nupdated: {recent_date}\n---\n# Recent\n"
            )

            findings = self.lint_vault_json(root)[1]
            stale_paths = {f["path"] for f in findings if f["code"] == "stale_page"}
            self.assertIn("projects/old.md", stale_paths)
            self.assertNotIn("projects/recent.md", stale_paths)


if __name__ == "__main__":
    unittest.main()
