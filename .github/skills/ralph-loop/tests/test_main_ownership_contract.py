from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[4]


def instructions(path: str) -> str:
    return " ".join((ROOT / path).read_text(encoding="utf-8").lower().split())


class MainOwnershipContractTests(unittest.TestCase):
    def test_ralph_entrypoints_refresh_without_checking_out_main(self):
        for path in (
            ".github/agents/ralph-loop.agent.md",
            ".github/skills/ralph-loop/SKILL.md",
            ".github/skills/ralph-loop/references/multi-agent-orchestration.md",
            ".github/skills/ralph-loop/references/ralph-loop.md",
        ):
            with self.subTest(path=path):
                content = instructions(path)
                self.assertTrue("git fetch origin" in content, f"{path} must fetch")
                self.assertTrue(
                    "docs/agent-sync/main-ownership.md" in content,
                    f"{path} must link the main ownership protocol",
                )
                self.assertFalse(
                    "git -c <integration-worktree> pull --ff-only" in content,
                    f"{path} must not pull the shared main checkout for refresh",
                )

    def test_status_and_merge_paths_wait_for_an_owner_and_release_main(self):
        for path in (
            ".github/agents/ralph-loop.agent.md",
            ".github/skills/ralph-loop/SKILL.md",
            ".github/skills/ralph-loop/references/multi-agent-orchestration.md",
            ".github/skills/ralph-loop/references/ralph-loop.md",
        ):
            with self.subTest(path=path):
                content = instructions(path)
                for requirement in (
                    "main/ownership.json",
                    "wait for",
                    "sign out immediately",
                    "status",
                    "merge",
                ):
                    self.assertTrue(
                        requirement in content,
                        f"{path} must document main ownership: {requirement}",
                    )

    def test_pr_merge_guide_reserves_main_without_holding_a_merge_queue(self):
        guide = instructions(
            ".github/skills/ralph-loop/references/worker-pr-merging.md"
        )
        for requirement in (
            "docs/agent-sync/main-ownership.md",
            "main/ownership.json",
            "wait for",
            "sign out",
            "merge queue",
        ):
            with self.subTest(requirement=requirement):
                self.assertTrue(
                    requirement in guide,
                    f"PR merge guide must document main ownership: {requirement}",
                )

    def test_main_signout_does_not_end_the_task_signin(self):
        contract = instructions("docs/agent-sync/main-ownership.md")
        self.assertIn("task sign-in", contract)
        self.assertIn("docs/agent-sync/main/ownership.json", contract)
        self.assertIn("atomic", contract)
        self.assertIn("immediately after that status commit", contract)
        self.assertIn("does not sign out of the task edit scope", contract)

    def test_agent_sync_guide_explains_automatic_main_release_and_manual_merge(self):
        guide = instructions("docs/agent-sync/README.md")
        for requirement in (
            "docs/agent-sync/main-ownership.md",
            "docs/agent-sync/main/ownership.json",
            "sign out immediately",
            "task sign-in",
            "--main-action acquire",
            "--main-action release",
            "--operation merge",
        ):
            with self.subTest(requirement=requirement):
                self.assertTrue(
                    requirement in guide,
                    f"agent-sync guide must cover main ownership: {requirement}",
                )

    def test_status_guide_keeps_main_signout_separate_from_task_state(self):
        guide = instructions(
            ".github/skills/ralph-loop/references/multi-agent-status.md"
        )
        self.assertTrue(
            "main/ownership.json" in guide,
            "status guide must distinguish the main owner from task state",
        )
        self.assertTrue(
            "sign out immediately" in guide,
            "status publication must release main without ending the task",
        )


if __name__ == "__main__":
    unittest.main()
