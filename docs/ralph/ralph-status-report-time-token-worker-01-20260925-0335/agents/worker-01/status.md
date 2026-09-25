# Worker status — branch time and token reporting

```yaml
schema_version: 2
run_id: "copilot-skills-status-report-time-token-20260925"
task_ids: ["branch-status-resource-usage"]
worker_id: "worker-01"
worker_name: "worker-01 / branch time and token reporting"
runtime_agent_id: "copilotcli:/b3f44ce6-c093-476d-ab74-b633b1be1939"
iteration: 1
status: AWAITING_MERGE
started_at_utc: "2026-09-25T04:08:07Z"
updated_at_utc: "2026-09-25T04:53:27Z"
branch: "ralph/status-report-time-token-worker-01-20260925-0335"
branch_slug: "ralph-status-report-time-token-worker-01-20260925-0335"
worktree: "/Users/jrblankenhorn/copilot_skills.worktrees/ralph-status-report-time-token-worker-01-20260925-0335"
base_origin_main_sha: "8da9310fda1b2e3042a379081dfb0675f1b22d6b"
rebased_onto_origin_main_sha: null
parent_branch: "ralph/status-report-time-token-20260925-0335"
parent_worktree: "/Users/jrblankenhorn/copilot_skills.worktrees/ralph-status-report-time-token-coordinator-20260925-0335"
parent_base_origin_main_sha: "8da9310fda1b2e3042a379081dfb0675f1b22d6b"
base_parent_sha: "74c6b1bb24f01bb7876bb489c810f1309a718373"
rebased_onto_parent_sha: null
implementation_commit_sha: "8848ebe818af7bb8d86e2b4e541cf4dbf4528a3"
resource_usage:
  time_spent_seconds: 2720
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
  reason: "The coordinator-reviewed, verified fast-forward into the parent branch does not use a PR."
merge_actor_worker_id: null
decision_record_path: "docs/decisions/ralph-status-report-time-token-worker-01-20260925-0335/agents/worker-01/pr-not-opened.md"
decision_index_path: "docs/decisions/ralph-status-report-time-token-worker-01-20260925-0335/README.md"
worker_to_parent_merge:
  status: PENDING
  sha: null
  verified_parent_ref: "refs/heads/ralph/status-report-time-token-20260925-0335"
  verified_parent_sha: null
  verification_method: null
  verified_at_utc: null
cleanup:
  worktree: PENDING
  local_branch: PENDING
  remote_ref: NOT_PUBLISHED
checks:
  - command: "python3 .github/skills/ralph-loop/tests/test_multi_agent_contract.py"
    result: PASS
  - command: "git diff --check"
    result: PASS
blockers: []
next_action: "Coordinator: review this sign-off, integrate the child into the parent, and mirror resource_usage into its dashboard index entry."
worker_sign_off:
  status: RECEIVED
  attestation_kind: SELF_ATTESTATION
  cryptographic_signature_status: NOT_CRYPTOGRAPHICALLY_SIGNED
  attested_at_utc: "2026-09-25T04:53:27Z"
  statement: "I, worker-01, sign off iteration 1 for branch-status-resource-usage at exact implementation commit 8848ebe818af7bb8d86e2b4e541cf4dbf4528a3."
commit_signature_verification:
  status: NOT_CRYPTOGRAPHICALLY_SIGNED
  verifier: null
  evidence: null
  verified_at_utc: null
```
