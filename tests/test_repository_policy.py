import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RepositoryPolicyTests(unittest.TestCase):
    def test_execution_security_guidance_remains_in_policy_files(self):
        security = (ROOT / "SECURITY.md").read_text(encoding="utf-8").lower()
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8").lower()

        for text in (security, skill):
            self.assertIn("prompt", text)
            self.assertIn("untrusted", text)
            self.assertIn("inspect", text)

        universal_wording = "should be considered untrusted data until"
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

    def test_installation_guidance_targets_the_canonical_collection(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        normalized_readme = " ".join(readme.split())

        self.assertIn("Install with Codex's built-in skill installer", readme)
        self.assertIn("Install manually with Git", readme)
        self.assertIn("Prompt an agent to install it", readme)
        self.assertIn("--repo reycarrorg/skills", readme)
        self.assertIn("--path skills/codex-migration-recovery", readme)
        self.assertIn("--name codex-migration-recovery", readme)
        self.assertIn("git rev-parse HEAD", readme)
        self.assertIn("pull --ff-only", readme)
        self.assertIn("Do not overwrite an existing destination", normalized_readme)
        self.assertIn("https://github.com/reycarrorg/skills/tree/main/skills/codex-migration-recovery", readme)
        self.assertNotIn("--repo reycarrorg/codex-migration-recovery", readme)
        self.assertNotIn("prompt injection", readme.lower())
        self.assertNotIn("universal skill and prompt-flow disclaimer", readme.lower())


if __name__ == "__main__":
    unittest.main()
