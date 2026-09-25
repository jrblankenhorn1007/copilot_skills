from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[4]


def read_document(path: str) -> str:
    document = ROOT / path
    if not document.exists():
        return ""
    return " ".join(document.read_text(encoding="utf-8").lower().split())


def assert_contains(test_case, text: str, requirement: str, message: str) -> None:
    test_case.assertTrue(requirement in text, message)


class PromptGenerationContractTests(unittest.TestCase):
    def test_ralph_agent_invokes_prompt_generation_guidance(self):
        agent = read_document(".github/agents/ralph-loop.agent.md")

        assert_contains(
            self,
            agent,
            "references/prompt-generation.md",
            "the Ralph Loop agent must invoke the prompt-generation guidance",
        )
        assert_contains(
            self,
            agent,
            "follow the prompt-generation guidance",
            "the Ralph Loop agent must direct coordinators and workers to follow "
            "the prompt-generation guidance",
        )

    def test_ralph_agent_uses_the_generated_prompt_for_execution_and_workers(self):
        agent = read_document(".github/agents/ralph-loop.agent.md")

        assert_contains(
            self,
            agent,
            "source of truth for execution and worker assignments",
            "execution and worker assignments must use the generated prompt",
        )
        assert_contains(
            self,
            agent,
            "not the raw user message",
            "the raw user message must not replace the generated prompt",
        )

    def test_guidance_defines_all_required_structured_fields(self):
        guidance = read_document(
            ".github/skills/ralph-loop/references/prompt-generation.md"
        )

        for requirement in (
            "objective",
            "user-stated scope",
            "derived requirements",
            "assumptions",
            "constraints and non-goals",
            "applicable skills",
            "validated project memory",
            "available tools",
            "work plan",
            "acceptance criteria",
            "verification",
            "integration end condition",
        ):
            with self.subTest(requirement=requirement):
                assert_contains(
                    self,
                    guidance,
                    requirement,
                    f"structured prompt guidance must define {requirement!r}",
                )

    def test_guidance_preserves_user_intent_and_surfaces_material_ambiguity(self):
        guidance = read_document(
            ".github/skills/ralph-loop/references/prompt-generation.md"
        )

        for requirement in (
            "preserve the user's explicit scope",
            "distinguish user-stated requirements from project-derived requirements",
            "do not invent work",
            "material ambiguity",
            "ask for clarification",
        ):
            with self.subTest(requirement=requirement):
                assert_contains(
                    self,
                    guidance,
                    requirement,
                    f"prompt generation must {requirement}",
                )

    def test_guidance_loads_and_validates_current_project_context(self):
        guidance = read_document(
            ".github/skills/ralph-loop/references/prompt-generation.md"
        )

        for requirement in (
            "current project instructions",
            "applicable skills",
            "relevant project memory",
            "validate memory against current sources",
            "available tools",
        ):
            with self.subTest(requirement=requirement):
                assert_contains(
                    self,
                    guidance,
                    requirement,
                    f"prompt generation must account for {requirement!r}",
                )

    def test_guidance_persists_a_secret_safe_branch_local_prompt(self):
        guidance = read_document(
            ".github/skills/ralph-loop/references/prompt-generation.md"
        )

        for requirement in (
            "docs/decisions/<branch-slug>/prompt.md",
            "link it from that branch's readme.md",
            "sanitize",
            "secrets",
            "unrelated private context",
        ):
            with self.subTest(requirement=requirement):
                assert_contains(
                    self,
                    guidance,
                    requirement,
                    f"prompt persistence must cover {requirement!r}",
                )

    def test_guidance_uses_the_prompt_as_the_execution_contract(self):
        guidance = read_document(
            ".github/skills/ralph-loop/references/prompt-generation.md"
        )

        for requirement in (
            "source of truth for execution and worker assignments",
            "not the raw user message",
        ):
            with self.subTest(requirement=requirement):
                assert_contains(
                    self,
                    guidance,
                    requirement,
                    "the structured prompt, rather than raw user text, must "
                    "drive execution and worker assignments",
                )


if __name__ == "__main__":
    unittest.main()
