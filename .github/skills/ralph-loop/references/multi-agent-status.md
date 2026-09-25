# Multi-agent Ralph status dashboard and leaf records

Use one canonical aggregate dashboard at the active project's
`docs/ralph-status.md`. Keep agent-owned run records under `docs/ralph/`,
organized by branch and agent. All paths in this guide are relative to the
active repository root.

## Durable documentation layout

```text
docs/
  ralph-status.md
  ralph/
    <branch-slug>/
      agents/
        <agent-id>/
          status.md
          progress.md
  decisions/
    <branch-slug>/
      README.md
      agents/
        <agent-id>/
          pr-<number>.md
          pr-pending.md
          pr-not-opened.md
```

- `docs/ralph-status.md` is the stable dashboard for the active project. It
  shows overall status and indexes every branch/agent leaf folder, including
  completed or otherwise terminal work.
- `docs/ralph/<branch-slug>/agents/<agent-id>/status.md` contains that agent's
  current state for the branch.
- `docs/ralph/<branch-slug>/agents/<agent-id>/progress.md` keeps that agent's
  iteration history and supporting evidence.
- `docs/decisions/<branch-slug>/README.md` and
  `docs/decisions/<branch-slug>/agents/<agent-id>/pr-*.md` remain the
  branch-scoped decision records. Their existing rules are summarized below.

Derive `<branch-slug>` from the exact branch ref by lowercasing it and
replacing each `/` with `-`. Use the stable run-scoped worker ID for
`<agent-id>` (for example, `worker-02`); keep the runtime agent/session ID in
the record as data, not as the path name. Keep repository-artifact links
repository-relative; the required `worktree` value in a sign-off may be an
absolute host path.

All generated Ralph run, status, progress, and decision records belong inside
the active repository's `docs/` directory. Do not create or update
root-level Ralph status/progress snapshots, per-run snapshot directories, or
competing aggregate dashboards. Keep prior branch/agent folders so their
evidence remains auditable; add each folder to the aggregate index rather than
overwriting it with a later branch.

## Ownership and synchronization

The coordinator is the **sole writer** of `docs/ralph-status.md`. Workers
maintain only their own branch/agent `status.md`, `progress.md`, and decision
records, then send the coordinator the exact paths, current state, checks,
sign-off, and any merge evidence. Workers must not edit the aggregate
dashboard or keep competing copies of it.

Treat each worker state transition as one serialized status update:

1. The worker records the transition in its leaf `status.md` and appends the
   supporting evidence to its `progress.md`.
2. The coordinator checks those records, updates the matching dashboard
   branch/agent entry and affected run counts/status, and verifies that both
   leaf links resolve.
3. The transition is not considered current or complete, and the coordinator
   does not move to the next loop/dispatch boundary, until the leaf records
   and dashboard show the same state.

Apply this synchronization at dispatch/start, block or unblock, check and
sign-off, awaiting integration, merge verification, and post-merge memory
review. Serialize dashboard writes when workers report concurrently. At each
loop boundary, reconcile the dashboard against every `docs/ralph/**/agents/*`
folder; it must not omit a branch/agent folder or show a stale status. Update
the dashboard timestamp/revision and its overall status at the same time as
the affected index entries.

The dashboard is the project-wide index and roll-up; each `status.md` is the
source of truth for its agent's current state, and `progress.md` is the
source of truth for its iteration evidence. Do not copy full agent histories
into the dashboard. Retain the compact status and links there so leaf evidence
has one canonical home.

## Status and verification rules

- `requested_worker_count` is the number assigned when the run is planned.
  `effective_worker_count` is the number of distinct workers actually
  launched; if it is lower than requested, record why in the split plan.
  `active_worker_count` is the number of workers currently marked
  `IN_PROGRESS`; it excludes `NOT_STARTED` (queued), blocked, awaiting-merge,
  and terminal workers.
- `overall_status` on the dashboard and `aggregate_status` for each run use
  the same meanings:
  - `IN_PROGRESS` while authorized work, review, checks, or integration can
    still proceed.
  - `BLOCKED` when the run cannot advance without external intervention. An
    individual worker being blocked does not block the whole run if other
    authorized work can continue.
  - `COMPLETE` only after every assigned task meets its acceptance criteria,
    required checks and sign-offs are recorded, every required merge is
    verified on fetched `origin/main`, and the post-merge memory review is
    complete. Any memory follow-up merge must also be verified. A pushed
    branch or open PR is not complete.
- A worker's `status` is one of `NOT_STARTED`, `IN_PROGRESS`,
  `AWAITING_MERGE`, `BLOCKED`, `COMPLETE`, `FAILED`, or `CANCELLED`. Mark it
  `COMPLETE` only after its assigned work is merged, the remote merge is
  verified, and the coordinator's post-merge memory review is complete. Any
  memory follow-up merge must also be verified.
- `merge_actor_worker_id` records the stable worker ID that performed the
  remote PR merge action: the worker who submitted or queued the merge action.
  For a worker-owned PR, it must match the branch owner's `worker_id`; use
  `null` until the merge is verified. Coordinator authorization and
  verification do not make the coordinator the merge actor, and a GitHub
  merge-queue identity does not replace the worker ID.
- Keep the agent's `status.md` current; keep `iteration_history` in its
  `progress.md`. Add one entry for each worker iteration and retain prior
  entries. Do not replace earlier evidence on a retry. Every fresh-branch
  retry gets its own branch/agent folder and dashboard index entry. If
  `origin/main` moves and an iteration is rebased before integration, record
  the new SHA in `rebased_onto_origin_main_sha`, update the final
  `implementation_commit_sha`, and obtain a new sign-off bound to that
  rewritten SHA.
- Record the iteration's `implementation_commit_sha` separately from
  `merge.sha`. They can differ after a squash or merge-queue merge. Verify the
  resulting merge SHA on fetched `origin/main` and record the observed remote
  SHA, verification method, and time; do not require the implementation
  commit itself to remain an ancestor after a squash merge.
- Each check records the exact command or procedure and its result: `PASS`,
  `FAIL`, `NOT_RUN`, or `BLOCKED`. List blockers explicitly; use an empty
  list only when there are none. Keep run-level and worker-level
  `next_action` specific and current.
- Each iteration records its `pull_request` number/URL and state, or
  `NOT_OPENED` when the normal integration path has no PR, plus a
  `decision_record_path` under `docs/decisions/<branch-slug>/`. Keep a
  separate record for each agent/PR pair; while an expected PR number is
  pending, use `agents/<agent-id>/pr-pending.md`; when no PR is part of the
  integration path, use `agents/<agent-id>/pr-not-opened.md`. The record
  captures decisions and recovered issues; only current unresolved issues
  belong in the status snapshot's `blockers`.
- Timestamps use ISO 8601 UTC (`...Z`); SHA fields contain full Git object
  IDs, not abbreviations. Use `null` for unavailable runtime agent/session
  IDs instead of inventing one.

### Current-state leaf and append-only evidence

Every agent's `status.md` describes only the current state of that
branch/agent assignment. It must identify at least the run and task IDs,
stable `worker_id` and `worker_name`, `runtime_agent_id` (or `null`), branch
and slug, current iteration and `status`, base/rebased `origin/main` SHAs,
current implementation commit, checks, blockers, next action, PR state,
decision-record path, `merge_actor_worker_id`, merge verification state, and
sign-off/signature state.
It may be written as Markdown with a YAML block or a table, but keep the
field names and enum values unambiguous.

Append iteration evidence to `progress.md`, including the exact commands and
results, important decisions, rebase/retest details, sign-off payload, the
merge command and `merge_actor_worker_id` when available, and recovered
failures with their resolution.
For behavior changes, retain exact Red, Green, and refactor commands/results.
For documentation-only changes, record that TDD Red/Green/Refactor was not
applicable and list the documentation checks actually run; do not fabricate
a failing behavior test. Keep historical iteration entries even when
`status.md` advances to a newer state.

### Aggregate dashboard example

The coordinator maintains a single `docs/ralph-status.md`. The example below
shows the required roll-up and branch/agent index; repeat a run entry and
index row for every tracked run and every `docs/ralph/<branch-slug>/agents/<agent-id>/`
folder. Retain rows for completed, failed, cancelled, or superseded branches
so the dashboard indexes every leaf folder.

```yaml
schema_version: 1
snapshot_path: "docs/ralph-status.md"
snapshot_revision: 1
updated_at_utc: "2026-09-25T00:00:00Z"
overall_status: IN_PROGRESS
current_run_ids: ["<run-id>"]

runs:
  - run_id: "<run-id>"
    task_ids: ["<task-id>"]
    aggregate_status: IN_PROGRESS
    requested_worker_count: 2
    effective_worker_count: 2
    active_worker_count: 1
    base_origin_main_sha: "<full SHA>"
    created_at_utc: "2026-09-25T00:00:00Z"
    updated_at_utc: "2026-09-25T00:00:00Z"
    next_action: "Coordinator: authorize worker-02's PR; worker-02 then merges and verifies it."
    split_plan:
      - task_id: "<worker-01-task>"
        worker_id: "worker-01"
        scope: "Complete the independent orchestration assignment."
        depends_on: []
      - task_id: "<worker-02-task>"
        worker_id: "worker-02"
        scope: "Complete the independent status-schema assignment."
        depends_on: []

branch_agent_index:
  - run_id: "<run-id>"
    task_ids: ["<task-id>"]
    worker_id: "worker-01"
    worker_name: "worker-01 / orchestration"
    branch: "ralph/orchestration-worker-01-<unique-id>"
    branch_slug: "ralph-orchestration-worker-01-<unique-id>"
    status: IN_PROGRESS
    iteration: 1
    merge_actor_worker_id: null
    status_path: "docs/ralph/ralph-orchestration-worker-01-<unique-id>/agents/worker-01/status.md"
    progress_path: "docs/ralph/ralph-orchestration-worker-01-<unique-id>/agents/worker-01/progress.md"
    decision_record_path: "docs/decisions/ralph-orchestration-worker-01-<unique-id>/agents/worker-01/pr-pending.md"
    decision_index_path: "docs/decisions/ralph-orchestration-worker-01-<unique-id>/README.md"
    next_action: "Worker-01: finish the assigned checks and report its leaf update."
  - run_id: "<run-id>"
    task_ids: ["<task-id>"]
    worker_id: "worker-02"
    worker_name: "worker-02 / status schema"
    branch: "ralph/status-schema-worker-02-<unique-id>"
    branch_slug: "ralph-status-schema-worker-02-<unique-id>"
    status: AWAITING_MERGE
    iteration: 1
    merge_actor_worker_id: null
    status_path: "docs/ralph/ralph-status-schema-worker-02-<unique-id>/agents/worker-02/status.md"
    progress_path: "docs/ralph/ralph-status-schema-worker-02-<unique-id>/agents/worker-02/progress.md"
    decision_record_path: "docs/decisions/ralph-status-schema-worker-02-<unique-id>/agents/worker-02/pr-<number>.md"
    decision_index_path: "docs/decisions/ralph-status-schema-worker-02-<unique-id>/README.md"
    next_action: "Coordinator: authorize worker-02; worker-02: merge and verify its PR."
```

The branch/agent index is deliberately explicit rather than a glob-only list:
the coordinator must refresh it when folders are added and check it against
the repository tree at each loop boundary.

### Agent leaf status example

The following is the current-state shape for one agent's `status.md`; detailed
iteration history and full check evidence remain in its sibling `progress.md`.

```yaml
schema_version: 1
run_id: "<stable run ID>"
task_ids: ["<task ID>"]
worker_id: "worker-02"
worker_name: "<stable display name>"
runtime_agent_id: "<host-provided agent/session ID or null>"
branch: "<exact branch ref>"
branch_slug: "<lowercase branch with slashes replaced by hyphens>"
iteration: 1
status: AWAITING_MERGE
started_at_utc: "<ISO 8601 UTC timestamp>"
updated_at_utc: "<ISO 8601 UTC timestamp>"
base_origin_main_sha: "<full SHA>"
rebased_onto_origin_main_sha: null
implementation_commit_sha: "<exact full implementation commit SHA>"
pull_request:
  status: OPEN
  number: "<PR number>"
  url: "<PR URL>"
merge_actor_worker_id: null
decision_record_path: "docs/decisions/<branch-slug>/agents/<agent-id>/pr-<number>.md"
decision_index_path: "docs/decisions/<branch-slug>/README.md"
merge:
  status: PENDING
  sha: null
  verified_remote_ref: "refs/heads/main"
  verified_origin_main_sha: null
  verification_method: null
  verified_at_utc: null
checks:
  - command: "<exact command>"
    result: PASS
blockers: []
next_action: "Worker-02: after coordinator authorization, merge the PR and verify its remote SHA."
worker_sign_off:
  status: RECEIVED
  attestation_kind: SELF_ATTESTATION
  cryptographic_signature_status: NOT_CRYPTOGRAPHICALLY_SIGNED
  attested_at_utc: "<ISO 8601 UTC timestamp>"
  statement: "I, worker-02, sign off iteration 1 at the exact implementation commit above."
commit_signature_verification:
  status: NOT_CRYPTOGRAPHICALLY_SIGNED
  verifier: null
  evidence: null
  verified_at_utc: null
```

### Worker sign-off and signatures

Before handing an iteration to the coordinator for integration, each worker
returns a structured sign-off containing the run/task IDs, stable worker ID
and name, runtime agent/session ID when available, iteration number,
branch/worktree, base SHA, exact full `implementation_commit_sha`, checks,
blockers, and UTC attestation time. Its statement must explicitly identify
the same worker ID, iteration, and exact commit SHA. The coordinator stores
the full payload in the agent's `progress.md` iteration entry and records the
current sign-off state in `status.md`. The coordinator rejects or requests a
fresh sign-off if the final commit SHA changes.

A normal worker message is a **self-attestation**, not a cryptographic
signature. Record its `cryptographic_signature_status` as
`NOT_CRYPTOGRAPHICALLY_SIGNED`. Track commit-signature verification
separately from the sign-off: set the implementation commit's status to
`VERIFIED` only when Git verifies that exact commit (for example,
`git verify-commit <full-sha>`) or GitHub reports the exact commit's signature
as verified. Record the verifier, evidence, and time. If there is no such
proof—including when a commit is unsigned, a signature cannot be checked, or
only the worker claims it is signed—label it
`NOT_CRYPTOGRAPHICALLY_SIGNED`. A verified commit signature proves the
commit signature, not that a separate status message was cryptographically
signed; keep those facts distinct.

A worker sign-off payload has this shape (retain the full payload in the
matching `progress.md`; summarize its current state in `status.md`):

```json
{
  "run_id": "<stable run ID>",
  "task_ids": ["<task ID>"],
  "worker_id": "worker-02",
  "worker_name": "<stable display name>",
  "runtime_agent_id": "<host-provided agent/session ID or null>",
  "iteration": 1,
  "branch": "<iteration branch>",
  "worktree": "<path to worker worktree>",
  "pull_request": {
    "status": "NOT_OPENED",
    "number": null,
    "url": null
  },
  "decision_record_path": "docs/decisions/<branch-slug>/agents/worker-02/pr-not-opened.md",
  "base_origin_main_sha": "<full origin/main SHA>",
  "implementation_commit_sha": "<exact full implementation commit SHA>",
  "checks": [
    { "command": "<exact command>", "result": "PASS" }
  ],
  "blockers": [],
  "attested_at_utc": "<ISO 8601 UTC timestamp>",
  "attestation_kind": "SELF_ATTESTATION",
  "cryptographic_signature_status": "NOT_CRYPTOGRAPHICALLY_SIGNED",
  "statement": "I, worker-02, sign off iteration 1 for <task ID> at commit <exact full implementation commit SHA>."
}
```

### Decision record rules

For each iteration, retain its `decision_record_path` under
`docs/decisions/<branch-slug>/`. The branch index is
`docs/decisions/<branch-slug>/README.md`; keep one agent/PR record at
`agents/<agent-id>/pr-<number>.md`. If a PR is expected but not numbered yet,
use `agents/<agent-id>/pr-pending.md`. If the normal integration path does
not open a PR, use `agents/<agent-id>/pr-not-opened.md` and state why no PR
was opened. Move a pending record to the numbered PR path when a PR is
assigned, and update the branch index before merging.

Each agent/PR record captures the branch, base and implementation commit
SHAs, stable agent ID and runtime ID when available, PR number/URL or why
none was opened, and decisions with context, alternatives, rationale, and
consequences. Log recovered failures with a sanitized diagnostic, resolution,
and passing verification; keep unresolved blockers separate. Never record
credentials, tokens, or raw secret-bearing command output. The agent
responsible for a branch maintains its decision index and records and commits
them with that branch before integration; the coordinator checks them with
the leaf records, checks, and diff.
