import re
import unittest
from pathlib import Path


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

    def test_git_preflight_separates_identity_and_access_permissions(self):
        ralph_skill = read_document(".github/skills/ralph-loop/SKILL.md")

        for requirement in (
            "git var git_author_ident",
            "git var git_committer_ident",
            "git fetch origin",
            "fetch proves read access only",
            "publishing the actual iteration branch",
            "merge permission",
            "use only authentication already configured",
            "never ask the user to paste credentials",
            "bypass branch protection",
            "do not run sign-in/setup commands or change remotes or credential configuration without the user's explicit approval",
        ):
            with self.subTest(requirement=requirement):
                assert_contains(
                    self,
                    ralph_skill,
                    requirement,
                    f"Ralph skill Git preflight must include {requirement!r}",
                )

        agent = read_document(".github/agents/ralph-loop.agent.md")
        for requirement in (
            "authentication preflight",
            "branch push or merge permission",
            "co-authored-by: copilot",
        ):
            with self.subTest(requirement=requirement):
                assert_contains(
                    self,
                    agent,
                    requirement,
                    f"Ralph agent instructions must include {requirement!r}",
                )

        orchestration = read_document(
            ".github/skills/ralph-loop/references/multi-agent-orchestration.md"
        )
        assert_contains(
            self,
            orchestration,
            "fetch success proves read access only",
            "worker guidance must distinguish read access from write access",
        )

        readme = read_document("README.md")
        assert_contains(
            self,
            readme,
            "configured git identity and remote read access",
            "README must surface the Git preflight",
        )

    def test_git_and_github_repository_operations_never_use_a_browser(self):
        governed_docs = (
            ".github/agents/ralph-loop.agent.md",
            ".github/skills/ralph-loop/SKILL.md",
            ".github/skills/ralph-loop/references/multi-agent-orchestration.md",
            ".github/skills/ralph-loop/references/worker-pr-merging.md",
            ".github/skills/ralph-loop/references/ralph-loop.md",
        )
        requirements = (
            "never open, navigate, or automate a browser for git or github repository operations",
            "use the git cli (`git`) for local repository operations",
            "status, diff, fetch/pull, branch/worktree, rebase, commit, and push",
            "use the configured github cli (`gh`) or supported github integration/mcp tools for pull requests, checks, reviews, and merges",
            "if the required cli or integration is unavailable or not authorized, report a blocker; do not fall back to a browser",
        )

        for path in governed_docs:
            document = read_document(path)
            for requirement in requirements:
                with self.subTest(path=path, requirement=requirement):
                    assert_contains(
                        self,
                        document,
                        requirement,
                        f"{path} must direct Git/GitHub operations away from browsers",
                    )

    def test_workers_merge_their_own_prs_after_coordinator_authorizes(self):
        ralph_skill = read_document(".github/skills/ralph-loop/SKILL.md")
        for requirement in (
            "worker performs the remote merge of its own pr after coordinator authorization",
            "configured github cli (`gh`) or supported github integration/mcp tools",
            "do not rely on coordinator credentials",
        ):
            with self.subTest(requirement=requirement):
                assert_contains(
                    self,
                    ralph_skill,
                    requirement,
                    f"Ralph skill must require worker-owned PR merging: {requirement!r}",
                )

        orchestration = read_document(
            ".github/skills/ralph-loop/references/multi-agent-orchestration.md"
        )
        for requirement in (
            "coordinator authorizes one worker pr at a time",
            "worker who owns the branch executes its own pr merge",
            "using its own existing authentication through the configured github cli (`gh`) or supported github integration/mcp tools",
            "coordinator does not use its own credentials to merge a worker pr",
            "never use `--admin` or override managed policy",
            "if the worker's merge permission is denied, preserve the branch and pr and report a sanitized blocker",
        ):
            with self.subTest(requirement=requirement):
                assert_contains(
                    self,
                    orchestration,
                    requirement,
                    f"orchestration must define worker-owned PR merging: {requirement!r}",
                )

        status_guide = read_document(
            ".github/skills/ralph-loop/references/multi-agent-status.md"
        )
        assert_contains(
            self,
            status_guide,
            "merge_actor_worker_id",
            "the worker status must record who performed the PR merge",
        )
        assert_contains(
            self,
            status_guide,
            "worker who submitted or queued the merge action",
            "the merge actor must remain attributable when GitHub applies a queued merge",
        )

        merge_guide = read_document(
            ".github/skills/ralph-loop/references/worker-pr-merging.md"
        )
        assert_contains(
            self,
            merge_guide,
            "coordinator authorization",
            "the dedicated PR merge guide must require coordinator authorization",
        )
        assert_contains(
            self,
            merge_guide,
            "configured github cli (`gh`) or supported github integration/mcp tools",
            "the merge guide must allow the configured CLI or supported GitHub integration",
        )
        assert_contains(
            self,
            merge_guide,
            "worker who submitted or queued the merge action",
            "the merge guide must define the actor for merge-queue integrations",
        )

        readme = read_document("README.md")
        assert_contains(
            self,
            readme,
            "worker-pr-merging.md",
            "README must link the worker-owned PR merge guidance",
        )

        project_prompt = read_document(
            ".github/skills/ralph-loop/references/ralph-loop.md"
        )
        assert_contains(
            self,
            project_prompt,
            "branch-owning worker executes its own pr merge",
            "the project Ralph prompt must use worker-owned PR merging",
        )

    def test_final_response_reports_completion_and_logs_recovered_issues(self):
        ralph_skill = read_document(".github/skills/ralph-loop/SKILL.md")
        for requirement in (
            "task completed: yes",
            "task completed: no",
            "only unresolved blockers",
            "fails but the issue is resolved",
            "docs/decisions/<branch-slug>/",
        ):
            with self.subTest(requirement=requirement):
                assert_contains(
                    self,
                    ralph_skill,
                    requirement,
                    f"Ralph skill must include {requirement!r}",
                )

        agent = read_document(".github/agents/ralph-loop.agent.md")
        for requirement in ("task completed: yes", "task completed: no"):
            with self.subTest(requirement=requirement):
                assert_contains(
                    self,
                    agent,
                    requirement,
                    f"Ralph agent must include {requirement!r}",
                )

        orchestration = read_document(
            ".github/skills/ralph-loop/references/multi-agent-orchestration.md"
        )
        for requirement in (
            "per-agent, per-pr",
            "recovered issues",
            "unresolved blockers",
        ):
            with self.subTest(requirement=requirement):
                assert_contains(
                    self,
                    orchestration,
                    requirement,
                    f"multi-agent guidance must include {requirement!r}",
                )

        status_guide = read_document(
            ".github/skills/ralph-loop/references/multi-agent-status.md"
        )
        for field in ("decision_record_path", "pull_request"):
            with self.subTest(field=field):
                assert_contains(
                    self,
                    status_guide,
                    field,
                    f"status snapshot must reference {field!r}",
                )

        decisions = read_document("docs/decisions/README.md")
        for requirement in (
            "docs/decisions/<branch-slug>/",
            "agents/<agent-id>/pr-<number>.md",
            "pr-pending.md",
            "pr-not-opened.md",
            "recovered",
            "unresolved",
        ):
            with self.subTest(requirement=requirement):
                assert_contains(
                    self,
                    decisions,
                    requirement,
                    f"decision-log guide must include {requirement!r}",
                )

        readme = read_document("README.md")
        assert_contains(
            self,
            readme,
            "docs/decisions/readme.md",
            "README must link to the branch decision-log convention",
        )

        decisions_root = ROOT / "docs" / "decisions"
        self.assertTrue(
            decisions_root.is_dir()
            and any(
                (branch / "README.md").is_file()
                and bool(list(branch.glob("agents/*/pr-*.md")))
                for branch in decisions_root.iterdir()
                if branch.is_dir()
            ),
            "each Ralph branch must have branch details and a per-agent, per-PR decision record",
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

    def test_ralph_docs_contract_uses_active_project_docs_layout(self):
        for path in (
            ".github/skills/ralph-loop/SKILL.md",
            ".github/agents/ralph-loop.agent.md",
            ".github/skills/ralph-loop/references/multi-agent-orchestration.md",
            ".github/skills/ralph-loop/references/multi-agent-status.md",
            ".github/skills/ralph-loop/references/ralph-loop.md",
            ".github/skills/tdd/SKILL.md",
        ):
            with self.subTest(path=path):
                document = read_document(path)
                assert_contains(
                    self,
                    document,
                    "docs/ralph-status.md",
                    f"{path} must identify the active-project Ralph dashboard",
                )
                assert_contains(
                    self,
                    document,
                    "docs/ralph/<branch-slug>/agents/<agent-id>",
                    f"{path} must identify branch/agent-owned records",
                )
                self.assertNotIn(
                    "ralph_progress.md",
                    document,
                    f"{path} must not direct Ralph progress to the repository root",
                )
                self.assertNotIn(
                    "implementation_status.md",
                    document,
                    f"{path} must not direct Ralph status to the repository root",
                )
                self.assertNotIn(
                    "decision_log.md",
                    document,
                    f"{path} must not direct Ralph decisions to the repository root",
                )

    def test_docs_status_dashboard_indexes_every_branch_agent_folder(self):
        dashboard_source = (ROOT / "docs" / "ralph-status.md").read_text(encoding="utf-8")
        dashboard = " ".join(dashboard_source.lower().split())
        assert_contains(self, dashboard, "overall_status", "dashboard must surface overall status")
        assert_contains(
            self,
            dashboard,
            "branch_agent_index",
            "dashboard must expose its branch/agent index",
        )

        ralph_root = ROOT / "docs" / "ralph"
        agent_folders = sorted(
            folder for folder in ralph_root.glob("*/agents/*") if folder.is_dir()
        )
        self.assertTrue(agent_folders, "docs/ralph must contain branch/agent records")
        branch_index = dashboard_source.split("branch_agent_index:", 1)[1].split(
            "\n```", 1
        )[0]
        entries = re.split(r"(?m)^  - run_id: ", branch_index)
        for agent_folder in agent_folders:
            with self.subTest(agent_folder=agent_folder.relative_to(ROOT).as_posix()):
                status_path = agent_folder / "status.md"
                progress_path = agent_folder / "progress.md"
                self.assertTrue(status_path.is_file(), "each branch/agent folder needs status.md")
                self.assertTrue(
                    progress_path.is_file(),
                    "each branch/agent folder needs progress.md",
                )
                assert_contains(
                    self,
                    dashboard,
                    status_path.relative_to(ROOT).as_posix(),
                    "dashboard must link every branch/agent status",
                )
                assert_contains(
                    self,
                    dashboard,
                    progress_path.relative_to(ROOT).as_posix(),
                    "dashboard must link every branch/agent progress log",
                )
                status_relative = status_path.relative_to(ROOT).as_posix()
                progress_relative = progress_path.relative_to(ROOT).as_posix()
                matching_entries = [
                    entry
                    for entry in entries
                    if f'status_path: "{status_relative}"' in entry
                ]
                self.assertEqual(
                    len(matching_entries),
                    1,
                    "each branch/agent folder must have exactly one dashboard entry",
                )
                self.assertIn(
                    f'progress_path: "{progress_relative}"',
                    matching_entries[0],
                    "status and progress links must be in the same dashboard entry",
                )
                leaf_status = status_path.read_text(encoding="utf-8")
                leaf_match = re.search(
                    r"(?im)^\|\s*status\s*\|\s*`([^`]+)`\s*\|\s*$",
                    leaf_status,
                ) or re.search(
                    r"(?im)^-\s+\*\*status:\*\*\s*`([^`]+)`\s*$",
                    leaf_status,
                ) or re.search(
                    r"(?im)^status:\s*([A-Z_]+)\s*$",
                    leaf_status,
                )
                self.assertIsNotNone(leaf_match, "leaf status must expose a status field")
                dashboard_match = re.search(
                    r"(?m)^\s*status:\s*([A-Z_]+)\s*$",
                    matching_entries[0],
                )
                self.assertIsNotNone(
                    dashboard_match,
                    "dashboard entry must expose the leaf's current status",
                )
                self.assertEqual(
                    dashboard_match.group(1),
                    leaf_match.group(1),
                    "dashboard and leaf status must be synchronized",
                )

        self.assertFalse(
            (ROOT / "implementation_status.md").exists(),
            "Ralph status must not remain at the repository root",
        )
        self.assertFalse(
            (ROOT / "RALPH_PROGRESS.md").exists(),
            "Ralph progress must not remain at the repository root",
        )

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
            "docs/ralph-status.md",
            "README must link the current Ralph status dashboard",
        )


if __name__ == "__main__":
    unittest.main()
