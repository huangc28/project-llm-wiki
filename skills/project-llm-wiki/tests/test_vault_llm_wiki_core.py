from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
CORE = ROOT / "skills" / "vault-llm-wiki"
CORE_SKILL = CORE / "SKILL.md"
TEMPLATES = CORE / "assets" / "templates"
CONVENTIONS = ROOT / "skills" / "project-llm-wiki" / "references" / "wiki-conventions.md"

# Relative path the core is expected to use to cite the shared conventions,
# resolved from the core SKILL.md's own directory.
CONVENTIONS_REL = "../project-llm-wiki/references/wiki-conventions.md"

# The five in-vault control-file templates the core must carry as the single
# maintained source (currently embedded inside vault-wiki-init).
CONTROL_FILE_TEMPLATES = (
    "AGENTS.md",
    "CLAUDE.md",
    "AI Note-Taking Principles.md",
    "index.md",
    "log.md",
)


class VaultLlmWikiCoreTests(unittest.TestCase):
    def test_core_skill_exists_with_frontmatter(self):
        self.assertTrue(CORE_SKILL.is_file(), f"missing core skill at {CORE_SKILL}")
        text = CORE_SKILL.read_text()
        self.assertIn("name: vault-llm-wiki", text)
        self.assertIn("description:", text)

    def test_core_references_shared_conventions_by_relative_path(self):
        text = CORE_SKILL.read_text()
        # Cite the shared conventions rather than restating them.
        self.assertIn("wiki-conventions.md", text)
        self.assertIn(CONVENTIONS_REL, text)
        # The cited relative path must resolve to the single real conventions file.
        resolved = (CORE_SKILL.parent / CONVENTIONS_REL).resolve()
        self.assertEqual(CONVENTIONS.resolve(), resolved)
        self.assertTrue(resolved.is_file())

    def test_core_does_not_copy_the_conventions_file(self):
        # Single source: the vault core must not ship its own wiki-conventions.md.
        copies = sorted(CORE.glob("**/wiki-conventions.md"))
        self.assertEqual([], copies, f"vault core copied conventions: {copies}")

    def test_core_states_vault_specific_protocol(self):
        text = CORE_SKILL.read_text()
        lower = text.lower()
        # Truth = the vault (primary source of truth / second brain).
        self.assertIn("source of truth", lower)
        # Vault-specific page budgets live in the core prose, not in conventions.
        self.assertIn("5–10", text)  # default blast radius 5–10 pages
        self.assertIn("1–3", text)   # careful mode caps at 1–3 pages
        # Maintenance-trio-vs-thinking-aids split.
        for needle in ("vault-ingest", "vault-query", "vault-lint"):
            with self.subTest(needle=needle):
                self.assertIn(needle, text)
        self.assertIn("thinking aid", lower)

    def test_control_file_templates_are_carried_by_the_core(self):
        self.assertTrue(TEMPLATES.is_dir(), f"missing templates dir at {TEMPLATES}")
        for name in CONTROL_FILE_TEMPLATES:
            with self.subTest(template=name):
                # Exactly one maintained copy of each control-file template.
                matches = sorted(TEMPLATES.glob(f"**/{name}"))
                self.assertEqual(
                    1,
                    len(matches),
                    f"expected exactly one {name} under {TEMPLATES}, found {matches}",
                )

    def test_control_file_templates_carry_recognizable_content(self):
        def read(name):
            return (sorted(TEMPLATES.glob(f"**/{name}"))[0]).read_text()

        # AGENTS.md points agents at CLAUDE.md.
        self.assertIn("CLAUDE.md", read("AGENTS.md"))
        # CLAUDE.md is the vault schema / operating contract.
        self.assertIn("Vault Schema", read("CLAUDE.md"))
        # Style guide.
        self.assertIn("AI Note-Taking Principles", read("AI Note-Taking Principles.md"))
        # Seeded index.
        self.assertIn("Vault Index", read("index.md"))
        # Append-only log.
        log = read("log.md")
        self.assertIn("Vault Log", log)
        self.assertIn("Append-only", log)

    def test_templates_readme_documents_inventory_and_safety(self):
        readme = (TEMPLATES / "README.md").read_text()
        for name in CONTROL_FILE_TEMPLATES:
            with self.subTest(name=name):
                self.assertIn(name, readme)
        self.assertIn("single", readme.lower())
        self.assertIn("secret", readme.lower())


if __name__ == "__main__":
    unittest.main()
