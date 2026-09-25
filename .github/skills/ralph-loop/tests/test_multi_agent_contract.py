import re
from pathlib import Path
import subprocess
import tempfile
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

    def test_per_branch_time_and_token_usage_contract(self):
        status_path = (
            ROOT / ".github" / "skills" / "ralph-loop" / "references" / "multi-agent-status.md"
        )
        status_source = status_path.read_text(encoding="utf-8")
        status_guide = " ".join(status_source.lower().split())

        for requirement in (
            "resource_usage",
            "time_spent_seconds",
            "time_basis: wall_clock_elapsed",
            "started_at_utc",
            "updated_at_utc",
            "wall-clock difference from that leaf's `started_at_utc` to "
            "its report's `updated_at_utc`",
            "not active coding time",
            "token_spend",
            "`reported` when the provider reports all four counters",
            "`partial` when at least one counter is provider-reported",
            "`not_reported` when no provider token counter is available",
            "input_tokens",
            "output_tokens",
            "total_tokens",
            "cached_input_tokens",
            "source",
            "`source` naming the provider or session-usage source when known",
            "provider-reported token counters only",
            "do not estimate missing counters",
            "never zero",
            "not a monetary cost estimate",
            "cached_input_tokens` is a subset of `input_tokens`",
            "must not be added again to `total_tokens`",
            "must exactly mirror its leaf's current object",
            "schema_version: 2",
            "schema_version: 1",
            "legacy record",
            "do not backfill measurements",
        ):
            with self.subTest(requirement=requirement):
                assert_contains(
                    self,
                    status_guide,
                    requirement,
                    f"status guide must define {requirement!r}",
                )

        branch_index_example = status_source.split("branch_agent_index:", 1)[1].split(
            "\n```", 1
        )[0]
        index_entries = re.split(r"(?m)^  - run_id: ", branch_index_example)
        for index, entry in enumerate(index_entries):
            if not entry.strip():
                continue
            with self.subTest(index_entry=index):
                normalized_entry = " ".join(entry.lower().split())
                for field in (
                    "resource_usage:",
                    "time_spent_seconds:",
                    "time_basis: wall_clock_elapsed",
                    "token_spend:",
                    "input_tokens: null",
                    "output_tokens: null",
                    "total_tokens: null",
                    "cached_input_tokens: null",
                    "source: null",
                ):
                    assert_contains(
                        self,
                        normalized_entry,
                        field,
                        f"each branch_agent_index example must include {field!r}",
                    )

        leaf_example = status_source.split("### Agent leaf status example", 1)[1]
        leaf_example = leaf_example.split("```yaml", 1)[1].split("```", 1)[0]
        normalized_leaf = " ".join(leaf_example.lower().split())
        for field in (
            "schema_version: 2",
            "resource_usage:",
            "time_spent_seconds:",
            "time_basis: wall_clock_elapsed",
            "token_spend:",
            "status: not_reported",
            "input_tokens: null",
            "output_tokens: null",
            "total_tokens: null",
            "cached_input_tokens: null",
            "source: null",
        ):
            with self.subTest(leaf_field=field):
                assert_contains(
                    self,
                    normalized_leaf,
                    field,
                    f"agent leaf YAML example must include {field!r}",
                )

        worker_two_entry = next(
            entry for entry in index_entries if 'worker_id: "worker-02"' in entry
        )
        index_usage = worker_two_entry.split("resource_usage:", 1)[1].split(
            "status_path:", 1
        )[0]
        leaf_usage = leaf_example.split("resource_usage:", 1)[1].split(
            "base_origin_main_sha:", 1
        )[0]
        usage_fields = (
            "time_spent_seconds",
            "time_basis",
            "status",
            "input_tokens",
            "output_tokens",
            "total_tokens",
            "cached_input_tokens",
            "source",
        )
        index_usage_values = dict(
            re.findall(r"(?m)^[ \t]*(\w+):[ \t]*([^#\n]+)", index_usage)
        )
        leaf_usage_values = dict(
            re.findall(r"(?m)^[ \t]*(\w+):[ \t]*([^#\n]+)", leaf_usage)
        )
        self.assertEqual(
            {field: index_usage_values[field].strip() for field in usage_fields},
            {field: leaf_usage_values[field].strip() for field in usage_fields},
            "the worker-02 branch-index resource usage must mirror its leaf example",
        )

        for path in (
            ".github/skills/ralph-loop/SKILL.md",
            ".github/agents/ralph-loop.agent.md",
            ".github/skills/ralph-loop/references/multi-agent-orchestration.md",
        ):
            guidance = read_document(path)
            for requirement in (
                "resource_usage",
                "branch_agent_index",
                "wall-clock",
                "not active coding time",
                "provider-reported",
            ):
                with self.subTest(path=path, requirement=requirement):
                    assert_contains(
                        self,
                        guidance,
                        requirement,
                        f"{path} must reference {requirement!r}",
                    )

        readme = read_document("README.md")
        for requirement in (
            "per-branch time and token usage contract",
            "multi-agent-status.md#per-branch-time-and-token-usage",
            "branch-local wall-clock elapsed time",
            "provider-reported token counts",
            "not_reported",
        ):
            with self.subTest(document="README", requirement=requirement):
                assert_contains(
                    self,
                    readme,
                    requirement,
                    f"README must point to the resource-usage contract and summarize {requirement!r}",
                )

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
        current_branch = subprocess.run(
            ["git", "-C", str(ROOT), "branch", "--show-current"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        current_branch_slug = current_branch.lower().replace("/", "-")
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
                leaf_status = status_path.read_text(encoding="utf-8")
                leaf_match = re.search(
                    r"(?im)^\|\s*status\s*\|\s*`([^`]+)`\s*\|\s*$",
                    leaf_status,
                ) or re.search(
                    r"(?im)^-\s+\*\*status:\*\*\s*`([^`]+)`\s*$",
                    leaf_status,
                ) or re.search(
                    r"(?m)^status:\s*([A-Z_]+)\s*$",
                    leaf_status,
                )
                self.assertIsNotNone(leaf_match, "leaf status must expose a status field")
                status_relative = status_path.relative_to(ROOT).as_posix()
                matching_entries = [
                    entry
                    for entry in entries
                    if f'status_path: "{status_relative}"' in entry
                ]
                unintegrated_current_child = (
                    agent_folder.parent.parent.name == current_branch_slug
                    and leaf_match.group(1) in {"IN_PROGRESS", "AWAITING_MERGE"}
                    and re.search(
                        r"(?m)^worker_to_parent_merge:\s*\n\s+status:\s+PENDING\s*$",
                        leaf_status,
                    )
                    is not None
                )
                if not matching_entries:
                    # A new child leaf reaches the coordinator-owned dashboard
                    # only when its pending integration is coordinated.
                    self.assertTrue(
                        unintegrated_current_child,
                        "only an in-progress current child with a pending parent merge "
                        "may await coordinator dashboard integration",
                    )
                    continue
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

    def test_project_specific_ralph_prompts_include_task_relevant_skills(self):
        ralph_skill = read_document(".github/skills/ralph-loop/SKILL.md")

        for requirement in (
            "create or translate a project-specific ralph prompt",
            "the user's task",
            "current project plan",
            "current ralph prompt",
            "canonical skill catalog",
            "project-local `.github/skills` catalog",
            "skill descriptions and triggers",
            "do not guess a stack",
            "do not reuse a static list",
            "do not list every available skill",
            "the generated prompt itself must contain an explicit `## relevant skills` section",
            "each selected skill's name, canonical or project-local path or link, and the condition or reason it applies",
            "always include ralph loop",
            "tdd for behavior changes",
            "project memory for the required post-merge review",
            "domain-specific skills may be included only when their descriptions or triggers match",
            "verify that a project-local skill path exists before linking it",
            "list each skill only once",
            "do not list an unavailable local skill",
        ):
            with self.subTest(requirement=requirement):
                assert_contains(
                    self,
                    ralph_skill,
                    requirement,
                    f"Ralph prompt generation must include {requirement!r}",
                )

    def test_parent_child_orchestration_and_branch_cleanup_are_documented(self):
        agent = read_document(".github/agents/ralph-loop.agent.md")
        skill = read_document(".github/skills/ralph-loop/SKILL.md")
        orchestration = read_document(
            ".github/skills/ralph-loop/references/multi-agent-orchestration.md"
        )
        status = read_document(
            ".github/skills/ralph-loop/references/multi-agent-status.md"
        )
        cli_usage = read_document(
            ".github/skills/ralph-loop/references/copilot-cli-usage.md"
        )
        readme = read_document("README.md")

        for requirement in (
            "--orchestrator",
            "parent worktree",
            "child worktree",
            "the coordinator merges each completed child branch into the parent branch",
        ):
            with self.subTest(document="agent", requirement=requirement):
                assert_contains(
                    self,
                    agent,
                    requirement,
                    f"Ralph agent must define {requirement!r}",
                )

        for requirement in (
            "child branch",
            "git worktree remove",
            "git branch -d",
            "origin/main",
        ):
            with self.subTest(document="skill", requirement=requirement):
                assert_contains(
                    self,
                    skill,
                    requirement,
                    f"Ralph Loop skill must define {requirement!r}",
                )

        for requirement in (
            "parent branch",
            "child branch",
            "merge-base --is-ancestor",
            "git worktree remove <worker-worktree>",
            "git branch -d <worker-branch>",
            "git push origin --delete <worker-branch>",
            "parent merge",
            "origin/main",
        ):
            with self.subTest(document="orchestration", requirement=requirement):
                assert_contains(
                    self,
                    orchestration,
                    requirement,
                    f"orchestration reference must define {requirement!r}",
                )

        for requirement in (
            "parent_branch",
            "worker_to_parent_merge",
            "parent_to_main_merge",
            "verified_parent_sha",
            "verified_origin_main_sha",
        ):
            with self.subTest(document="status", requirement=requirement):
                assert_contains(
                    self,
                    status,
                    requirement,
                    f"status reference must define {requirement!r}",
                )

        for requirement in (
            "--orchestrator",
            "launcher-level",
            "not a native copilot cli flag",
        ):
            with self.subTest(document="cli usage", requirement=requirement):
                assert_contains(
                    self,
                    cli_usage,
                    requirement,
                    f"CLI guide must accurately describe {requirement!r}",
                )

        for requirement in ("--orchestrator", "parent branch", "child worktrees"):
            with self.subTest(document="README", requirement=requirement):
                assert_contains(
                    self,
                    readme,
                    requirement,
                    f"README must summarize {requirement!r}",
                )


class GitPipelineTests(unittest.TestCase):
    def test_workers_merge_into_parent_and_clean_up_only_after_verified_merges(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            remote = root / "origin.git"
            seed = root / "seed"
            repository = root / "repository"
            parent_worktree = root / "parent"
            parent_branch = "ralph/test-parent"
            worker_ids = ("worker-01", "worker-02")

            def git(
                cwd: Path, *args: str, expected_returncode: int = 0
            ) -> str:
                result = subprocess.run(
                    ["git", *args],
                    cwd=cwd,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(
                    result.returncode,
                    expected_returncode,
                    f"git {' '.join(args)} failed: {result.stderr}",
                )
                return result.stdout.strip()

            git(root, "init", "--bare", "--initial-branch=main", str(remote))
            git(root, "init", str(seed))
            git(seed, "checkout", "-b", "main")
            git(seed, "config", "user.name", "Ralph Pipeline Test")
            git(seed, "config", "user.email", "ralph-test@example.invalid")
            (seed / "README.md").write_text("seed\n", encoding="utf-8")
            git(seed, "add", "README.md")
            git(seed, "commit", "-m", "seed main")
            git(seed, "remote", "add", "origin", str(remote))
            git(seed, "push", "origin", "main")
            git(
                root,
                "clone",
                "--branch",
                "main",
                str(remote),
                str(repository),
            )
            git(repository, "config", "user.name", "Ralph Pipeline Test")
            git(repository, "config", "user.email", "ralph-test@example.invalid")
            git(repository, "fetch", "origin")

            git(
                repository,
                "worktree",
                "add",
                "-b",
                parent_branch,
                str(parent_worktree),
                "origin/main",
            )
            worker_files = []
            for worker_id in worker_ids:
                worker_worktree = root / worker_id
                worker_branch = f"ralph/test-{worker_id}"
                worker_file = f"{worker_id}.txt"
                worker_files.append(worker_file)
                parent_base = git(parent_worktree, "rev-parse", "HEAD")
                git(
                    repository,
                    "worktree",
                    "add",
                    "-b",
                    worker_branch,
                    str(worker_worktree),
                    parent_branch,
                )
                (worker_worktree / worker_file).write_text(
                    f"{worker_id} result\n", encoding="utf-8"
                )
                git(worker_worktree, "add", worker_file)
                git(
                    worker_worktree,
                    "commit",
                    "-m",
                    f"complete {worker_id} assignment",
                )
                worker_commit = git(worker_worktree, "rev-parse", "HEAD")
                git(
                    worker_worktree,
                    "merge-base",
                    "--is-ancestor",
                    parent_base,
                    worker_commit,
                )
                git(
                    worker_worktree,
                    "push",
                    "--set-upstream",
                    "origin",
                    worker_branch,
                )

                git(parent_worktree, "merge", "--ff-only", worker_branch)
                worker_merge_sha = git(parent_worktree, "rev-parse", "HEAD")
                self.assertEqual(worker_commit, worker_merge_sha)
                git(
                    parent_worktree,
                    "merge-base",
                    "--is-ancestor",
                    worker_merge_sha,
                    parent_branch,
                )
                git(repository, "worktree", "remove", str(worker_worktree))
                git(parent_worktree, "branch", "-d", worker_branch)
                git(repository, "push", "origin", "--delete", worker_branch)
                self.assertFalse(worker_worktree.exists())
                self.assertNotIn(
                    worker_branch,
                    git(repository, "branch", "--list", worker_branch),
                )
                self.assertEqual(
                    "",
                    git(
                        repository,
                        "ls-remote",
                        "--heads",
                        "origin",
                        f"refs/heads/{worker_branch}",
                    ),
                )

            parent_commit = git(parent_worktree, "rev-parse", "HEAD")
            git(
                parent_worktree,
                "push",
                "--set-upstream",
                "origin",
                parent_branch,
            )
            git(
                parent_worktree,
                "push",
                "origin",
                f"{parent_branch}:main",
            )
            git(repository, "fetch", "origin")
            git(
                repository,
                "merge-base",
                "--is-ancestor",
                parent_commit,
                "origin/main",
            )
            self.assertEqual(parent_commit, git(repository, "rev-parse", "origin/main"))

            git(repository, "push", "origin", "--delete", parent_branch)
            git(repository, "worktree", "remove", str(parent_worktree))
            git(repository, "merge", "--ff-only", "origin/main")
            git(repository, "branch", "-d", parent_branch)
            self.assertFalse(parent_worktree.exists())
            self.assertNotIn(
                parent_branch,
                git(repository, "branch", "--list", parent_branch),
            )
            self.assertEqual(
                "",
                git(
                    repository,
                    "ls-remote",
                    "--heads",
                    "origin",
                    f"refs/heads/{parent_branch}",
                ),
            )
            for worker_file, worker_id in zip(worker_files, worker_ids):
                self.assertEqual(
                    f"{worker_id} result",
                    git(repository, "show", f"origin/main:{worker_file}"),
                )


if __name__ == "__main__":
    unittest.main()
