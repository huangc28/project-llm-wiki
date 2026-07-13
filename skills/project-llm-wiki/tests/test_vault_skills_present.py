from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
SKILLS_ROOT = ROOT / "skills"

# The 10 vault skill dirs consolidated from the private vault repo (ticket #2):
# the maintenance trio + wiki-init, plus the six thinking aids.
VAULT_SKILLS = (
    "vault-ingest",
    "vault-query",
    "vault-lint",
    "vault-wiki-init",
    "vault-today",
    "vault-trace",
    "vault-challenge",
    "vault-connect",
    "vault-ghost",
    "vault-ideas",
)


class VaultSkillsPresentTests(unittest.TestCase):
    def test_all_ten_vault_skill_dirs_present_with_skill_md(self):
        for name in VAULT_SKILLS:
            with self.subTest(skill=name):
                skill_dir = SKILLS_ROOT / name
                self.assertTrue(skill_dir.is_dir(), f"missing skill dir {skill_dir}")
                self.assertFalse(skill_dir.is_symlink(), f"{skill_dir} is a symlink")
                skill_md = skill_dir / "SKILL.md"
                self.assertTrue(skill_md.is_file(), f"missing {skill_md}")
                text = skill_md.read_text()
                self.assertIn(f"name: {name}", text)

    def test_vault_wiki_init_carries_its_readme(self):
        # vault-wiki-init shipped a README.md alongside SKILL.md; it moves too.
        self.assertTrue((SKILLS_ROOT / "vault-wiki-init" / "README.md").is_file())

    def test_no_omx_runtime_state_committed(self):
        # Runtime OMC state must not follow the skills into the repo.
        leaked = [
            str(p.relative_to(SKILLS_ROOT))
            for name in VAULT_SKILLS
            for p in (SKILLS_ROOT / name).glob("**/.omx")
        ]
        self.assertEqual([], leaked, f".omx runtime state leaked in: {leaked}")


if __name__ == "__main__":
    unittest.main()
