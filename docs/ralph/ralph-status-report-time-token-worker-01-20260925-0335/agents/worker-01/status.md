# Worker status — branch time and token reporting

```yaml
schema_version: 2
run_id: "copilot-skills-status-report-time-token-20260925"
task_ids: ["branch-status-resource-usage"]
worker_id: "worker-01"
worker_name: "worker-01 / branch time and token reporting"
runtime_agent_id: "copilotcli:/b3f44ce6-c093-476d-ab74-b633b1be1939"
iteration: 1
status: COMPLETE
started_at_utc: "2026-09-25T04:08:07Z"
updated_at_utc: "2026-09-25T06:22:24Z"
branch: "ralph/status-report-time-token-worker-01-20260925-0335"
branch_slug: "ralph-status-report-time-token-worker-01-20260925-0335"
worktree: "/Users/jrblankenhorn/copilot_skills.worktrees/ralph-status-report-time-token-worker-01-20260925-0335"
base_origin_main_sha: "8da9310fda1b2e3042a379081dfb0675f1b22d6b"
rebased_onto_origin_main_sha: null
parent_branch: "ralph/status-report-time-token-20260925-0335"
parent_worktree: "/Users/jrblankenhorn/copilot_skills.worktrees/ralph-status-report-time-token-coordinator-20260925-0335"
parent_base_origin_main_sha: "8da9310fda1b2e3042a379081dfb0675f1b22d6b"
parent_rebased_onto_origin_main_sha: "e9fe3d175d1ca76b03fccdbe53431205b80e5c23"
base_parent_sha: "74c6b1bb24f01bb7876bb489c810f1309a718373"
rebased_onto_parent_sha: "a2b8c0f2ff99b9a5447accd6cfdd93e550c50ade"
implementation_commit_sha: "5f0c7af5bd237fa06dde3b4a4edd9e95db7470b7"
resource_usage:
  time_spent_seconds: 8057
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
  status: VERIFIED
  sha: "019ab357f25e1b04133bacb242460e063d94be9d"
  verified_parent_ref: "refs/heads/ralph/status-report-time-token-20260925-0335"
  verified_parent_sha: "5634ff3377e54cce5281a1256ba2f0c169ebf31f"
  verification_method: "git merge-base --is-ancestor 019ab357f25e1b04133bacb242460e063d94be9d HEAD"
  verified_at_utc: "2026-09-25T06:04:57Z"
worker_to_parent_merge_history:
  - status: SUPERSEDED_BY_PARENT_REBASE
    sha: "14ea97483e70f97bdf1203ec388bb6d6a7d90f9c"
    verified_parent_ref: "refs/heads/ralph/status-report-time-token-20260925-0335"
    verified_parent_sha: "14ea97483e70f97bdf1203ec388bb6d6a7d90f9c"
    verification_method: "git merge-base --is-ancestor 14ea97483e70f97bdf1203ec388bb6d6a7d90f9c HEAD"
    verified_at_utc: "2026-09-25T05:40:07Z"
    superseded_by_parent_rebase_onto_origin_main_sha: "e9fe3d175d1ca76b03fccdbe53431205b80e5c23"
cleanup:
  worktree: PENDING
  local_branch: PENDING
  remote_ref: NOT_PUBLISHED
memory_review_status: COMPLETE
memory_review_outcome: "No separate durable lesson warranted; the resource-usage rule is explicit and tested in the Ralph status contract."
checks:
  - command: "python3 .github/skills/ralph-loop/tests/test_multi_agent_contract.py"
    result: PASS
    evidence: "15 tests passed in the rebased child worktree."
  - command: "git diff --check"
    result: PASS
  - command: "PYTHONDONTWRITEBYTECODE=1 python3 /Users/jrblankenhorn/copilot_skills.worktrees/ralph-status-report-time-token-coordinator-20260925-0335/.github/skills/ralph-loop/tests/test_multi_agent_contract.py"
    result: PASS
    evidence: "15 tests passed on the parent after rebasing onto origin/main e9fe3d175d1ca76b03fccdbe53431205b80e5c23."
blockers: []
next_action: null
worker_sign_off:
  status: RECEIVED
  attestation_kind: SELF_ATTESTATION
  cryptographic_signature_status: NOT_CRYPTOGRAPHICALLY_SIGNED
  attested_at_utc: "2026-09-25T05:39:04Z"
  statement: "I, worker-01, re-attest iteration 1 for branch-status-resource-usage at exact implementation commit 5f0c7af5bd237fa06dde3b4a4edd9e95db7470b7 after rebasing onto parent a2b8c0f2ff99b9a5447accd6cfdd93e550c50ade and rerunning all checks."
commit_signature_verification:
  status: NOT_CRYPTOGRAPHICALLY_SIGNED
  verifier: null
  evidence: null
  verified_at_utc: null
```
