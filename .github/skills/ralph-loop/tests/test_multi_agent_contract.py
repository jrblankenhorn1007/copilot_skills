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


class MultiAgentContractTests(unittest.TestCase):
    def test_ralph_agent_accepts_worker_count_and_creates_a_split_plan(self):
        orchestrator = read_document(".github/agents/ralph-loop.agent.md")

        assert_contains(
            self,
            orchestrator,
            "workers=n",
            "the Ralph Loop agent must accept a worker-count request",
        )
        assert_contains(
            self,
            orchestrator,
            "default is two workers",
            "the orchestrator must preserve the documented two-worker default",
        )
        assert_contains(
            self,
            orchestrator,
            "positive integer",
            "the orchestrator must validate worker-count input",
        )
        assert_contains(
            self,
            orchestrator,
            "split plan",
            "the orchestrator must produce a split plan",
        )
        assert_contains(
            self,
            orchestrator,
            "ralph loop",
            "the orchestrator must use Ralph Loop workers",
        )
        assert_contains(
            self,
            orchestrator,
            "agents: ['ralph loop']",
            "the orchestrator must restrict delegated agents to Ralph Loop",
        )
        self.assertTrue(
            any(
                term in orchestrator
                for term in (
                    "runsubagent",
                    "subagent tool",
                    "sub-agent tool",
                    "subagent invocation tool",
                )
            ),
            "the orchestrator must use a supported subagent mechanism",
        )

    def test_orchestration_reference_defines_worker_split_and_git_sync(self):
        orchestration = read_document(
            ".github/skills/ralph-loop/references/multi-agent-orchestration.md"
        )

        for requirement in (
            "workers=n",
            "split plan",
            "git fetch origin",
            "rebase",
            "origin/main",
            "force-push",
            "verify",
        ):
            with self.subTest(requirement=requirement):
                assert_contains(
                    self,
                    orchestration,
                    requirement,
                    f"orchestration reference must include {requirement!r}",
                )

    def test_worker_git_sync_requires_fetch_rebase_retest_and_remote_verification(self):
        worker = read_document(".github/agents/ralph-loop.agent.md")

        for requirement in (
            "git fetch origin",
            "rebase",
            "origin/main",
            "force-push",
            "rerun",
            "verify",
        ):
            with self.subTest(requirement=requirement):
                assert_contains(
                    self,
                    worker,
                    requirement,
                    f"worker Git protocol must include {requirement!r}",
                )

    def test_status_protocol_records_overall_worker_iteration_and_attestation(self):
        status_guide = read_document(
            ".github/skills/ralph-loop/references/multi-agent-status.md"
        )

        for field in (
            "requested_worker_count",
            "effective_worker_count",
            "active_worker_count",
            "aggregate_status",
            "worker id",
            "runtime_agent_id",
            "iteration",
            "iteration_history",
            "branch",
            "commit",
            "merge",
            "attestation",
            "cryptographic",
            "cryptographic_signature_status",
        ):
            with self.subTest(field=field):
                assert_contains(self, status_guide, field, f"status guide must define {field!r}")

    def test_live_status_snapshot_lists_both_test_workers(self):
        status = read_document("implementation_status.md")

        for field in (
            "overall status",
            "requested worker count",
            "effective worker count",
            "active worker count",
            "worker-01",
            "worker-02",
            "iteration",
            "attestation",
            "runtime agent id",
            "not cryptographically signed",
        ):
            with self.subTest(field=field):
                assert_contains(self, status, field, f"live status snapshot must include {field!r}")

    def test_readme_links_the_multi_agent_workflow_and_status(self):
        readme = read_document("README.md")

        assert_contains(
            self,
            readme,
            "first run an orchestrator",
            "README must document that the top-level Ralph Loop is the orchestrator",
        )
        assert_contains(
            self,
            readme,
            "multi-agent-orchestration.md",
            "README must link orchestration guidance",
        )
        assert_contains(
            self,
            readme,
            "multi-agent-status.md",
            "README must link status guidance",
        )
        assert_contains(
            self,
            readme,
            "implementation_status.md",
            "README must link the current run status",
        )


if __name__ == "__main__":
    unittest.main()
