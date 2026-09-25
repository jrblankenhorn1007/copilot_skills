"""Contract for conditional specialist dispatch in a Ralph iteration."""

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
GUIDE = ROOT / ".github" / "skills" / "ralph-loop" / "references" / "skill-aware-routing.md"
AGENTS = ROOT / ".github" / "agents"


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

    def test_deployed_ralph_coordinator_routes_specialists_until_roles_are_merged(self):
        guide = self.guide()
        for rule in (
            "currently deployed ralph loop coordinator",
            "ralph loop workers",
            "the future ralph orchestrator",
            "not yet on `origin/main`",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, guide)
        self.assertNotIn("the entrypoint does not dispatch specialists", guide)
        self.assertNotIn("ralph loop worker (`ralph-worker`)", guide)

    def test_deployed_coordinator_allows_existing_agents_and_every_specialist(self):
        content = (AGENTS / "ralph-loop.agent.md").read_text(encoding="utf-8")
        self.assertTrue(content.startswith("---\n"))
        metadata = content.split("---\n", 2)[1]
        match = re.search(r"(?m)^agents: \[([^\]\n]+)\]$", metadata)
        self.assertIsNotNone(match, "the deployed coordinator needs an agent allowlist")
        allowed = {name.strip().strip("'\"") for name in match.group(1).split(",")}
        for name in ("Ralph Loop", "Ralph Code Reviewer", "Ralph Security Reviewer"):
            with self.subTest(existing_agent=name):
                self.assertIn(name, allowed)

        profiles = sorted(AGENTS.glob("ralph-*-specialist.agent.md"))
        self.assertEqual(len(profiles), 4, "all four focused specialists must be installed")
        for path in profiles:
            with self.subTest(specialist=path.name):
                profile = path.read_text(encoding="utf-8").split("---\n", 2)[1]
                name = re.search(r"(?m)^name: (.+)$", profile)
                self.assertIsNotNone(name)
                self.assertIn(name.group(1), allowed)
                self.assertIn("user-invocable: true", profile)
                self.assertNotIn("disable-model-invocation: true", profile)
        self.assertNotIn("disable-model-invocation: true", metadata)
        self.assertIn("`agent`", content)

    def test_pipeline_surfaces_link_the_conditional_routing_guide(self):
        for path in (
            AGENTS / "ralph-loop.agent.md",
            ROOT / ".github" / "skills" / "ralph-loop" / "SKILL.md",
            ROOT / ".github" / "skills" / "ralph-loop" / "references" / "multi-agent-orchestration.md",
            ROOT / "README.md",
        ):
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertIn("skill-aware-routing.md", path.read_text(encoding="utf-8"))

    def test_specialists_use_the_same_host_capacity_as_workers(self):
        guide = self.guide()
        for rule in (
            "every launched specialist counts toward the resource manager's host limit",
            "reserve a host slot before each `agent/runsubagent` call",
            "an execution-capable specialist activates its reservation before task work",
            "when capacity is full, queue or block the specialist",
            "a general worker fallback also requires an available slot",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, guide)

    def test_read_only_specialists_do_not_gain_execute_for_admission(self):
        guide = self.guide()
        for rule in (
            "read-only specialists cannot run the registry cli",
            "the coordinator must account for their live sessions",
            "if their capacity cannot be verified, do not dispatch",
            "do not grant `execute` solely for registry bookkeeping",
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
