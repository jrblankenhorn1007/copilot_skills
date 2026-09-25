from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[4]
AGENT_PATH = ROOT / ".github" / "agents" / "project-memory-update.agent.md"


def normalize(text: str) -> str:
    return " ".join(text.replace("`", "").lower().split())


class MemoryUpdateAgentContractTests(unittest.TestCase):
    def test_agent_has_verified_post_merge_memory_review_contract(self):
        self.assertTrue(
            AGENT_PATH.is_file(),
            "the dedicated Project Memory Update agent definition is absent",
        )

        raw_agent = AGENT_PATH.read_text(encoding="utf-8")
        parts = raw_agent.split("---", 2)
        self.assertGreaterEqual(len(parts), 3, "agent definition must have YAML front matter")
        self.assertIn(
            "name: Project Memory Update",
            parts[1],
            "agent display name must be exactly Project Memory Update",
        )
        agent = normalize(raw_agent)

        requirements = (
            "after the current ralph implementation batch or iteration is merged",
            "resulting sha has been verified on fetched origin/main",
            "if the merge sha is not verified on origin/main, report blocked and make no memory changes",
            "coordinator's report",
            "every worker's memory_handoff",
            "independently inspect the merged sources, tests, review feedback, and integration evidence",
            "do not treat handoff assertions as verified facts",
            "implementation_summary",
            "lesson_candidates",
            "no_durable_lessons_reason",
            "lesson_candidates may be an empty list",
            "when it is empty, set no_durable_lessons_reason to a concise explanation",
            "each candidate provides a rule, why, optional scope, and specific evidence",
            "when candidates are supplied, set no_durable_lessons_reason to null",
            "handoffs must not include credentials, secrets, personal data, or task chronology",
            "read that project's applicable project memory skill",
            ".github/memory/readme.md",
            "relevant category files",
            "update only the active project's documented memory store",
            "do not write to copilot_skills when a different active project documents its own memory store",
            "validate, generalize, and deduplicate",
            "durable lessons",
            "no task diary",
            "unsupported assumptions, credentials, secrets, or personal data",
            "do not add empty category placeholders",
            "if there is no durable lesson after review, return an explicit no_update outcome",
            "create no branch",
            "fetch the latest origin/main and create a fresh branch from the latest origin/main",
            "never write directly to main",
            "normal review and integration process",
            "wait for coordinator authorization before the branch-owning memory agent merges its own pr",
            "preserve the branch and report a sanitized blocker if publication or integration is unavailable",
            "never bypass repository policy",
            "do not invoke yourself recursively",
            "do not trigger another memory review for a memory-only follow-up",
            "no_update",
            "awaiting_merge",
            "complete",
            "blocked",
            "reviewed_handoff_sources",
            "lesson_paths_changed",
            "pull_request",
            "merge_sha",
            "remote verification",
            "reason for no update or block",
        )
        for requirement in requirements:
            with self.subTest(requirement=requirement):
                self.assertTrue(
                    requirement in agent,
                    f"Project Memory Update agent must include {requirement!r}",
                )


if __name__ == "__main__":
    unittest.main()
