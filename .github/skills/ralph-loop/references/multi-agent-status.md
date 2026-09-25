# Multi-agent Ralph status snapshot

Use one durable, run-level status snapshot to show the overall Ralph run and
each worker's current status and iteration history. The coordinator is the
**only writer** of that shared snapshot. Workers send structured updates and
sign-offs to the coordinator; they do not concurrently edit the aggregate
status file or maintain competing copies. The coordinator records a report
only after checking its commit and verification evidence.

Keep one canonical snapshot at a durable path for the run and record that path
in `snapshot_path`. Update the current status fields in place, but retain every
worker iteration entry and sign-off so earlier attempts remain auditable.
Record the host's runtime agent/session ID when available, separately from the
stable run-scoped worker ID; use `null` rather than inventing one. Timestamps
use ISO 8601 UTC (`...Z`); SHA fields contain full Git object IDs, not
abbreviations.

## Status and verification rules

- `requested_worker_count` is the number assigned when the run is planned.
  `effective_worker_count` is the number of distinct workers actually
  launched; if it is lower than requested, record why in the split plan.
  `active_worker_count` is the number of workers currently marked
  `IN_PROGRESS`; it excludes `NOT_STARTED` (queued), blocked, awaiting-merge,
  and terminal workers.
- `aggregate_status` is exactly one of:
  - `IN_PROGRESS` while authorized work, review, checks, or integration can
    still proceed.
  - `BLOCKED` when the run cannot advance without external intervention.
    An individual worker being blocked does not block the whole run if other
    authorized work can continue.
  - `COMPLETE` only after every assigned task meets its acceptance criteria,
    required checks and sign-offs are recorded, and every required merge is
    verified on fetched `origin/main`, and the post-merge memory review is
    complete. Any memory follow-up merge must also be verified before
    completion. A pushed branch or open PR is not complete.
- A worker's `status` is one of `NOT_STARTED`, `IN_PROGRESS`,
  `AWAITING_MERGE`, `BLOCKED`, `COMPLETE`, `FAILED`, or `CANCELLED`.
  Mark a worker `COMPLETE` only after its assigned work is merged, the remote
  merge is verified, and the coordinator's post-merge memory review is
  complete. Any memory follow-up merge must also be verified.
- Keep `iteration_history` for each worker. Add one entry for each iteration;
  do not replace a prior iteration when retrying. If `origin/main` moves and
  an iteration is rebased before integration, record the new SHA in
  `rebased_onto_origin_main_sha`, update the final implementation commit SHA,
  and obtain a new sign-off bound to that rewritten SHA.
- Record the iteration's `implementation_commit_sha` separately from
  `merge.sha`. They can differ after a squash or merge-queue merge. Verify the
  resulting merge SHA on fetched `origin/main` and record the observed remote
  SHA, verification method, and time; do not require the implementation
  commit itself to remain an ancestor after a squash merge.
- Each check records the exact command or procedure and its result:
  `PASS`, `FAIL`, `NOT_RUN`, or `BLOCKED`. List blockers explicitly; use an
  empty list only when there are none. Keep run-level and worker-level
  `next_action` specific and current.
- Each iteration records its `pull_request` number/URL and state, or
  `NOT_OPENED` when the normal integration path has no PR, plus a
  `decision_record_path` under `docs/decisions/<branch-slug>/`. Keep a separate
  record for each agent/PR pair; while an expected PR number is pending, use
  `agents/<agent-id>/pr-pending.md`; when no PR is part of the integration
  path, use `agents/<agent-id>/pr-not-opened.md`. The record captures decisions
  and recovered issues; only current unresolved issues belong in the status
  snapshot's `blockers`.

## Worker sign-off and signatures

Before handing an iteration to the coordinator for integration, each worker
returns a structured sign-off containing the run/task IDs, stable worker ID
and name, runtime agent/session ID when available, iteration number,
branch/worktree, base SHA, exact full
`implementation_commit_sha`, checks, blockers, and UTC attestation time. Its
statement must explicitly identify the same worker ID, iteration, and exact
commit SHA. The coordinator stores the payload under that iteration and
rejects or requests a fresh sign-off if the final commit SHA changes.

A normal worker message is a **self-attestation**, not a cryptographic
signature. Record its `cryptographic_signature_status` as
`NOT_CRYPTOGRAPHICALLY_SIGNED`. Track commit-signature verification separately
from the sign-off: set the implementation commit's status to `VERIFIED` only
when Git verifies that exact commit (for example, `git verify-commit
<full-sha>`) or GitHub reports the exact commit's signature as verified. Record
the verifier, evidence, and time. If there is no such proof—including when a
commit is unsigned, a signature cannot be checked, or only the worker claims
it is signed—label it `NOT_CRYPTOGRAPHICALLY_SIGNED`. A verified commit
signature proves the commit signature, not that a separate status message was
cryptographically signed; keep those facts distinct.

A worker sign-off payload has this shape (the same payload is retained in the
snapshot):

```json
{
  "run_id": "<stable run ID>",
  "task_ids": ["<task ID>"],
  "worker_id": "worker-02",
  "worker_name": "<stable display name>",
  "runtime_agent_id": "<host-provided agent/session ID or null>",
  "iteration": 1,
  "branch": "<iteration branch>",
  "worktree": "<iteration worktree path>",
  "pull_request": {
    "status": "NOT_OPENED",
    "number": null,
    "url": null
  },
  "decision_record_path": "docs/decisions/<branch-slug>/agents/worker-02/pr-not-opened.md",
  "base_origin_main_sha": "<full origin/main SHA>",
  "implementation_commit_sha": "<exact full final commit SHA>",
  "checks": [
    { "command": "<exact command>", "result": "PASS" }
  ],
  "blockers": [],
  "attested_at_utc": "<ISO 8601 UTC timestamp>",
  "attestation_kind": "SELF_ATTESTATION",
  "cryptographic_signature_status": "NOT_CRYPTOGRAPHICALLY_SIGNED",
  "statement": "I, worker-02, sign off iteration 1 for <task ID> at commit <exact full final commit SHA>."
}
```

## Snapshot template and two-worker example

The following is illustrative only; replace all placeholder paths, timestamps,
IDs, and SHAs with evidence from the actual run.

```yaml
schema_version: 1
snapshot_path: "runs/<run-id>/multi-agent-status.md"
snapshot_revision: 4
run_id: "example-run-2026-09-24"
task_ids: [task-orchestration, task-status]
requested_worker_count: 2
effective_worker_count: 2
active_worker_count: 0
base_origin_main_sha: "<full SHA fetched at run start>"
aggregate_status: IN_PROGRESS
split_plan:
  - task_id: task-orchestration
    worker_id: worker-01
    scope: "Write the orchestration guide."
    depends_on: []
  - task_id: task-status
    worker_id: worker-02
    scope: "Define the multi-agent status schema."
    depends_on: []
created_at_utc: "2026-09-24T23:10:00Z"
updated_at_utc: "2026-09-24T23:17:00Z"
next_action: "Coordinator: merge worker-02's iteration, fetch origin, and verify its merge SHA."

workers:
  - worker_id: worker-01
    worker_name: "worker-01 / orchestration"
    runtime_agent_id: "<host-provided agent/session ID or null>"
    task_ids: [task-orchestration]
    status: COMPLETE
    started_at_utc: "2026-09-24T23:10:00Z"
    updated_at_utc: "2026-09-24T23:16:00Z"
    next_action: null
    iteration_history:
      - iteration: 1
        branch: "ralph/orchestration-worker-01-<unique-id>"
        worktree: "<path to worker-01 worktree>"
        pull_request:
          status: NOT_OPENED
          number: null
          url: null
        decision_record_path: "docs/decisions/ralph-orchestration-worker-01-<unique-id>/agents/worker-01/pr-not-opened.md"
        base_origin_main_sha: "<full SHA>"
        rebased_onto_origin_main_sha: null
        implementation_commit_sha: "<exact full worker-01 implementation commit SHA>"
        merge:
          status: VERIFIED
          sha: "<full resulting merge SHA>"
          verified_remote_ref: "refs/heads/main"
          verified_origin_main_sha: "<full fetched origin/main SHA containing the merge SHA>"
          verification_method: "git merge-base --is-ancestor <merge SHA> origin/main"
          verified_at_utc: "2026-09-24T23:16:00Z"
        checks:
          - command: "git diff --check"
            result: PASS
        blockers: []
        timestamps:
          started_at_utc: "2026-09-24T23:10:00Z"
          implementation_committed_at_utc: "2026-09-24T23:14:00Z"
          signed_off_at_utc: "2026-09-24T23:15:00Z"
          merge_verified_at_utc: "2026-09-24T23:16:00Z"
        worker_sign_off:
          status: RECEIVED
          run_id: "example-run-2026-09-24"
          task_ids: [task-orchestration]
          worker_id: worker-01
          worker_name: "worker-01 / orchestration"
          runtime_agent_id: "<same host-provided ID or null>"
          iteration: 1
          branch: "ralph/orchestration-worker-01-<unique-id>"
          worktree: "<path to worker-01 worktree>"
          base_origin_main_sha: "<same full SHA as the iteration record>"
          implementation_commit_sha: "<same exact full worker-01 implementation commit SHA>"
          checks:
            - command: "git diff --check"
              result: PASS
          blockers: []
          attestation_kind: SELF_ATTESTATION
          cryptographic_signature_status: NOT_CRYPTOGRAPHICALLY_SIGNED
          attested_at_utc: "2026-09-24T23:15:00Z"
          statement: "I, worker-01, sign off iteration 1 for task-orchestration at commit <same exact full worker-01 implementation commit SHA>."
        commit_signature_verification:
          status: NOT_CRYPTOGRAPHICALLY_SIGNED
          verifier: null
          evidence: null
          verified_at_utc: null

  - worker_id: worker-02
    worker_name: "worker-02 / status snapshot"
    runtime_agent_id: "<host-provided agent/session ID or null>"
    task_ids: [task-status]
    status: AWAITING_MERGE
    started_at_utc: "2026-09-24T23:10:00Z"
    updated_at_utc: "2026-09-24T23:17:00Z"
    next_action: "Coordinator: integrate this iteration and verify the remote merge."
    iteration_history:
      - iteration: 1
        branch: "ralph/status-worker-02-<unique-id>"
        worktree: "<path to worker-02 worktree>"
        base_origin_main_sha: "<full SHA>"
        rebased_onto_origin_main_sha: null
        implementation_commit_sha: "<exact full worker-02 commit SHA>"
        merge:
          status: PENDING
          sha: null
          verified_remote_ref: "refs/heads/main"
          verified_origin_main_sha: null
          verification_method: null
          verified_at_utc: null
        checks:
          - command: "git diff --check"
            result: PASS
        blockers: []
        timestamps:
          started_at_utc: "2026-09-24T23:10:00Z"
          implementation_committed_at_utc: "2026-09-24T23:16:00Z"
          signed_off_at_utc: "2026-09-24T23:17:00Z"
          merge_verified_at_utc: null
        worker_sign_off:
          status: RECEIVED
          run_id: "example-run-2026-09-24"
          task_ids: [task-status]
          worker_id: worker-02
          worker_name: "worker-02 / status snapshot"
          runtime_agent_id: "<same host-provided ID or null>"
          iteration: 1
          branch: "ralph/status-worker-02-<unique-id>"
          worktree: "<path to worker-02 worktree>"
          base_origin_main_sha: "<same full SHA as the iteration record>"
          implementation_commit_sha: "<same exact full worker-02 commit SHA>"
          checks:
            - command: "git diff --check"
              result: PASS
          blockers: []
          attestation_kind: SELF_ATTESTATION
          cryptographic_signature_status: NOT_CRYPTOGRAPHICALLY_SIGNED
          attested_at_utc: "2026-09-24T23:17:00Z"
          statement: "I, worker-02, sign off iteration 1 for task-status at commit <same exact full worker-02 commit SHA>."
        commit_signature_verification:
          status: NOT_CRYPTOGRAPHICALLY_SIGNED
          verifier: null
          evidence: null
          verified_at_utc: null
```
