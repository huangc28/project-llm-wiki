from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "skills" / "project-llm-wiki"


class ProjectWikiPackageTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
