"""Contract for conditional specialist dispatch in a Ralph iteration."""

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
GUIDE = ROOT / ".github" / "skills" / "ralph-loop" / "references" / "skill-aware-routing.md"


class SkillAwareRoutingTests(unittest.TestCase):
    def guide(self):
        self.assertTrue(GUIDE.is_file(), f"Missing routing guide: {GUIDE}")
        return " ".join(GUIDE.read_text(encoding="utf-8").lower().split())

    def test_routes_cover_existing_and_new_roles_without_one_agent_per_skill(self):
        guide = self.guide()
        for role in (
            "ralph-loop",
            "ralph-code-reviewer",
            "ralph-security-reviewer",
            "ralph-git-specialist",
            "ralph-docs-specialist",
            "ralph-agent-design-specialist",
            "ralph-asi-specialist",
        ):
            with self.subTest(role=role):
                self.assertIn(role, guide)
        for skill in (
            "docs-sync-audit",
            "acquire-codebase-knowledge",
            "copilot-instructions-blueprint-generator",
            "agent-architecture",
            "agent-skill-stack",
            "agentic-eval",
            "agent-owasp-compliance",
        ):
            with self.subTest(skill=skill):
                self.assertIn(skill, guide)

    def test_dispatch_is_conditional_and_has_an_honest_fallback(self):
        guide = self.guide()
        for rule in (
            "do not run all specialists",
            "general worker",
            "workers=n",
            "not counted",
            "agent/runsubagent",
            "unavailable",
            "inherit the session model",
            "no measured speed or cost improvement",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, guide)

    def test_scope_and_main_owner_gates_survive_delegation(self):
        guide = self.guide()
        for rule in (
            "exclusive edit scope",
            "docs/agent-sync/main/ownership.json",
            "status",
            "merge",
            "sign out immediately",
            "origin/main",
            "branch owner",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, guide)

    def test_compliance_and_code_review_stay_separate(self):
        guide = self.guide()
        self.assertIn("owasp asi", guide)
        self.assertIn("diff-level security review", guide)
        self.assertIn("code review", guide)
        self.assertIn("do not run all specialists for every request or duplicate investigations", guide)


if __name__ == "__main__":
    unittest.main()
