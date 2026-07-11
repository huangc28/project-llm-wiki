from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "skills" / "project-llm-wiki"
CONVENTIONS = PACKAGE / "references" / "wiki-conventions.md"


class WikiConventionsTests(unittest.TestCase):
    def test_exactly_one_conventions_file_exists(self):
        matches = sorted(ROOT.glob("**/wiki-conventions.md"))
        self.assertEqual(
            [CONVENTIONS],
            matches,
            f"expected exactly one wiki-conventions.md at {CONVENTIONS}, found {matches}",
        )

    def test_conventions_document_the_shared_invariants(self):
        text = CONVENTIONS.read_text().lower()
        for needle in (
            "index-first",        # index-first lookup
            "[[wikilink]]",       # wikilink citation
            "thicken",            # thicken-existing-before-creating
            "before creating",    # ...before creating a new page
            "updated from",       # provenance format
            "yyyy-mm-dd",         # provenance format
            "contradiction",      # contradiction flagging
            "append-only",        # append-only log
            "blast-radius",       # blast-radius hard cap
            "15",                 # ...hard cap = 15
        ):
            with self.subTest(needle=needle):
                self.assertIn(needle, text)

    def test_conventions_exclude_vault_specific_page_budgets(self):
        text = CONVENTIONS.read_text()
        for forbidden in ("5-10", "5–10", "1-3", "1–3"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, text)

    def test_core_skill_references_conventions_instead_of_restating(self):
        skill = (PACKAGE / "SKILL.md").read_text()
        self.assertIn("wiki-conventions.md", skill)


if __name__ == "__main__":
    unittest.main()
