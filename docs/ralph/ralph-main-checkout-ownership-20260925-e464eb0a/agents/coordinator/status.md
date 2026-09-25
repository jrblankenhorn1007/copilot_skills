# Coordinator status - exclusive main ownership

```yaml
schema_version: 2
run_id: "copilot-skills-main-checkout-ownership-20260925-e464eb0a"
task_ids: ["main-checkout-ownership", "status-publisher-exclusivity", "ralph-refresh-handoff"]
worker_id: "coordinator"
worker_name: "coordinator / main ownership handoff"
runtime_agent_id: "copilotcli:/e464eb0a-8639-4fda-8608-3416a4bc5eae"
iteration: 1
status: BLOCKED
started_at_utc: "2026-09-25T05:45:49Z"
updated_at_utc: "2026-09-25T06:50:38Z"
branch: "ralph/main-checkout-ownership-20260925-e464eb0a"
branch_slug: "ralph-main-checkout-ownership-20260925-e464eb0a"
worktree: "/Users/jrblankenhorn/copilot_skills.worktrees/ralph-main-checkout-ownership-20260925-e464eb0a"
parent_branch: "ralph/main-checkout-ownership-20260925-e464eb0a"
parent_worktree: "/Users/jrblankenhorn/copilot_skills.worktrees/ralph-main-checkout-ownership-20260925-e464eb0a"
base_origin_main_sha: "ad4e663aa21259946ec112f7831b822529117b3b"
parent_base_origin_main_sha: "ad4e663aa21259946ec112f7831b822529117b3b"
parent_rebased_onto_origin_main_sha: "20293c720b18a1a21ff150f566823493b7a2717d"
parent_implementation_commit_sha: null
implementation_commit_sha: null
resource_usage:
  time_spent_seconds: 3889
  time_basis: WALL_CLOCK_ELAPSED
  token_spend:
    status: NOT_REPORTED
    input_tokens: null
    output_tokens: null
    total_tokens: null
    cached_input_tokens: null
    source: null
pull_request:
  status: NOT_OPENED
  number: null
  url: null
  reason: "No PR has been opened; final integration is waiting on shared dashboard ownership."
merge_actor_worker_id: null
decision_record_path: "docs/decisions/ralph-main-checkout-ownership-20260925-e464eb0a/agents/coordinator/pr-not-opened.md"
decision_index_path: "docs/decisions/ralph-main-checkout-ownership-20260925-e464eb0a/README.md"
parent_to_main_merge:
  status: PENDING
  sha: null
  verified_remote_ref: "refs/heads/main"
  verified_origin_main_sha: null
  verification_method: null
  verified_at_utc: null
parent_cleanup:
  worktree: PENDING
  local_branch: PENDING
  remote_ref: NOT_PUBLISHED
memory_review:
  status: PENDING
  owner: coordinator
  outcome: null
checks:
  - command: "cd .github/skills/ralph-loop/tests && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest test_main_ownership_contract test_main_ownership_publisher test_multi_agent_contract"
    result: PASS
    evidence: "35 tests passed after rebasing onto 20293c720b18a1a21ff150f566823493b7a2717d."
  - command: "git diff --check"
    result: PASS
blockers:
  - "The iteration-stall run still owns docs/ralph-status.md and has not signed out; do not overwrite its dashboard or merge incomplete status records."
next_action: "Wait for the dashboard owner to sign out, synchronize this leaf with the aggregate dashboard, then commit, rebase, retest, and integrate on fetched origin/main."
worker_count:
  requested: 2
  effective: 0
  note: "The main reservation script and status contract were tightly coupled; no independent worker assignment was ready, and the earlier host worker launches were unavailable."
```
