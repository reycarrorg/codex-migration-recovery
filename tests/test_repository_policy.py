import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RepositoryPolicyTests(unittest.TestCase):
    def test_prompt_injection_warning_is_prominent(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8").lower()
        security = (ROOT / "SECURITY.md").read_text(encoding="utf-8").lower()
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8").lower()

        for text in (readme, security, skill):
            self.assertIn("prompt", text)
            self.assertIn("untrusted", text)
            self.assertIn("inspect", text)

        self.assertIn("if safety is uncertain, do not run it", readme)
        self.assertIn("prompt-injection and untrusted-source disclaimer", security)
        self.assertIn("if safety remains uncertain, stop", skill)

    def test_ci_uses_a_restricted_event_and_permission_model(self):
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn("contents: read", workflow)
        self.assertIn("persist-credentials: false", workflow)
        self.assertNotIn("pull_request_target", workflow)
        self.assertNotIn("workflow_run", workflow)
        self.assertNotIn("secrets.", workflow)


if __name__ == "__main__":
    unittest.main()
