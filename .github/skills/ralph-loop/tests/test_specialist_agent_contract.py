"""Contract checks for focused, skill-aware Ralph specialist definitions."""

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
AGENTS = {
    "ralph-git-specialist.agent.md": {
        "name": "Ralph Git Specialist",
        "tools": "['read', 'search', 'execute']",
        "skills": ("ralph-loop",),
    },
    "ralph-docs-specialist.agent.md": {
        "name": "Ralph Docs Specialist",
        "tools": "['read', 'search', 'edit', 'execute']",
        "skills": (
            "docs-sync-audit",
            "acquire-codebase-knowledge",
            "copilot-instructions-blueprint-generator",
        ),
    },
    "ralph-agent-design-specialist.agent.md": {
        "name": "Ralph Agent Design Specialist",
        "tools": "['read', 'search']",
        "skills": ("agent-architecture", "agent-skill-stack", "agentic-eval"),
    },
    "ralph-asi-specialist.agent.md": {
        "name": "Ralph ASI Specialist",
        "tools": "['read', 'search']",
        "skills": ("agent-owasp-compliance",),
    },
}


class SpecialistAgentContractTests(unittest.TestCase):
    def test_agents_are_selectable_and_inherit_the_session_model(self):
        for filename, expected in AGENTS.items():
            with self.subTest(agent=filename):
                path = ROOT / ".github" / "agents" / filename
                self.assertTrue(path.is_file(), f"Missing specialist: {path}")
                content = path.read_text(encoding="utf-8")
                self.assertTrue(content.startswith("---\n"))
                metadata = content.split("---\n", 2)[1]
                self.assertRegex(
                    metadata,
                    rf"(?m)^name: {re.escape(expected['name'])}$",
                )
                self.assertRegex(metadata, r"(?m)^description: .+")
                self.assertIn("user-invocable: true", metadata)
                self.assertIn("include-custom-instructions: true", metadata)
                self.assertIn(f"tools: {expected['tools']}", metadata)
                self.assertNotRegex(metadata, r"(?m)^model:")
                self.assertNotIn("'agent'", metadata)

    def test_specialists_only_reference_existing_relevant_skills(self):
        for filename, expected in AGENTS.items():
            with self.subTest(agent=filename):
                path = ROOT / ".github" / "agents" / filename
                self.assertTrue(path.is_file(), f"Missing specialist: {path}")
                content = path.read_text(encoding="utf-8")
                for skill in expected["skills"]:
                    with self.subTest(skill=skill):
                        self.assertTrue(
                            (ROOT / ".github" / "skills" / skill / "SKILL.md").is_file()
                        )
                        self.assertIn(f"../skills/{skill}/SKILL.md", content)

    def test_git_role_guards_the_shared_main_and_merge_actor(self):
        path = ROOT / ".github" / "agents" / "ralph-git-specialist.agent.md"
        self.assertTrue(path.is_file(), f"Missing specialist: {path}")
        content = path.read_text(encoding="utf-8")
        for rule in (
            "git fetch origin",
            "docs/agent-sync/main/ownership.json",
            "STATUS",
            "MERGE",
            "sign out immediately",
            "branch owner",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, content)

    def test_analysis_specialists_do_not_turn_audits_into_implementation(self):
        for filename in (
            "ralph-agent-design-specialist.agent.md",
            "ralph-asi-specialist.agent.md",
        ):
            with self.subTest(agent=filename):
                path = ROOT / ".github" / "agents" / filename
                self.assertTrue(path.is_file(), f"Missing specialist: {path}")
                self.assertIn("read-only", path.read_text(encoding="utf-8"))
        docs = ROOT / ".github" / "agents" / "ralph-docs-specialist.agent.md"
        self.assertTrue(docs.is_file(), f"Missing specialist: {docs}")
        self.assertIn(
            "read-only unless the user explicitly requests documentation changes",
            docs.read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
