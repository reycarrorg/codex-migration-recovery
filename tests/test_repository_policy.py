import json
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
        universal_wording = "should be considered untrusted data until"
        self.assertIn(universal_wording, readme)
        self.assertIn(universal_wording, security)
        self.assertIn(universal_wording, skill)
        self.assertIn("universal skill and prompt-flow safety disclaimer", security)
        self.assertIn("not a claim that every source is malicious", security)
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

    def test_public_provenance_is_present_and_sanitized(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        provenance_text = (ROOT / "PROVENANCE.json").read_text(encoding="utf-8")
        provenance = json.loads(provenance_text)

        self.assertIn("Design and test provenance", readme)
        self.assertIn("gpt-5.6-sol", readme)
        self.assertIn("xhigh", readme)
        self.assertEqual(provenance["schema_version"], 1)
        self.assertEqual(
            provenance["records"][0]["session_runtime"]["recorded_model_request"],
            "gpt-5.6-sol",
        )
        self.assertEqual(
            provenance["records"][0]["session_runtime"][
                "recorded_reasoning_effort"
            ],
            "xhigh",
        )

        self.assertNotIn("/Users/", provenance_text)
        self.assertNotIn("@", provenance_text)
        self.assertNotIn("thread_id", provenance_text.lower())
        self.assertNotIn("session_id", provenance_text.lower())


if __name__ == "__main__":
    unittest.main()
