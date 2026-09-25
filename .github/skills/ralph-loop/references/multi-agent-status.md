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

## Schema versions

New or updated current-state leaf reports and aggregate dashboards use
`schema_version: 2`. Version 2 adds branch-local `resource_usage` to each
agent's `status.md` and its matching `branch_agent_index` record. A historical
leaf with `schema_version: 1`, or an older index row without
`resource_usage`, is a legacy record. Keep such history identifiable and
unchanged; do not backfill measurements that were not recorded. When a
legacy report is explicitly updated, include only values supported by its
timestamps and provider-reported telemetry, leaving unavailable values null
as defined below.

## Ownership and synchronization

The live [agent-sync ledger](../../../../docs/agent-sync/README.md) records
each task's edit scope separately from the durable Ralph dashboard. Main
transactions have one repository-wide record at
`docs/agent-sync/main/ownership.json` under the
[main ownership protocol](../../../../docs/agent-sync/main-ownership.md).
Before a status write or authorized merge, wait for the current main owner
to sign out. The status publisher must sign out immediately after the
verified status commit; that does not sign out the task or change its
leaf/dashboard state. Reacquire main for the next status write.

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
  `IN_PROGRESS`; it excludes `NOT_STARTED` (queued), `AWAITING_REVIEW`,
  `AWAITING_AUTHOR_DECISION`, `AWAITING_MERGE`, `BLOCKED`, and terminal
  workers.
- `overall_status` on the dashboard and `aggregate_status` for each run use
  the same meanings:
  - `IN_PROGRESS` while authorized work, review, checks, or integration can
    still proceed.
  - `BLOCKED` when the run cannot advance without external intervention. An
    individual worker being blocked does not block the whole run if other
    authorized work can continue.
  - `COMPLETE` only after every assigned task meets its acceptance criteria,
    required checks and sign-offs are recorded, every worker-to-parent merge
    is verified on the current parent branch, and the final parent-to-main
    merge is verified on fetched `origin/main`; the post-merge memory review
    and any required memory follow-up merge must also be complete and verified.
    For a single-branch run, verify its final merge on fetched `origin/main`.
    A pushed branch, child merge alone, or open PR is not complete.
- A worker's `status` is one of `NOT_STARTED`, `IN_PROGRESS`,
  `AWAITING_REVIEW`, `AWAITING_AUTHOR_DECISION`, `AWAITING_MERGE`, `BLOCKED`,
  `COMPLETE`, `FAILED`, or `CANCELLED`. For PR-backed work, use
  `AWAITING_REVIEW` after worker sign-off while the independent review is
  pending or running; use `AWAITING_AUTHOR_DECISION` when findings or the
  two-round limit require the author agent to act. A current clean report, or
  a recorded `ACCEPT_FINDINGS_AND_REQUEST_MERGE` choice after the final
  author-agent action, may advance to `AWAITING_MERGE` only after all other
  gates are satisfied. The no-PR path skips review and retains its existing
  integration state. In a
  parent/child run, keep a worker `AWAITING_MERGE` until its child change is
  integrated and verified on the current parent branch; after that child
  merge, the worker may become `COMPLETE` while the overall run remains
  `IN_PROGRESS` until final parent-to-main verification and the coordinator's
  post-merge memory review (including any warranted memory follow-up) are
  complete. For a single-branch run, the worker remains subject to its final
  remote merge and memory-review gates.
- `merge_actor_worker_id` records the stable worker ID that performed the
  remote PR merge action: the worker who submitted or queued the merge action.
  For a worker-owned PR, it must match the branch owner's `worker_id`; use
  `null` until the merge is verified. Coordinator authorization and
  verification do not make the coordinator the merge actor, and a GitHub
  merge-queue identity does not replace the worker ID. Parent/child runs
  record child-to-parent and parent-to-main integration in their separate
  merge objects; a coordinator's local parent integration is not a worker
  PR merge actor.

### PR review state and evidence

Every PR-backed leaf status and dashboard branch/agent entry carries the same
`review` object. Its `status` is exactly one of:

- `NOT_APPLICABLE` — the repository's normal integration has no PR; do not
  launch a reviewer or alter the coordinator-managed fast-forward path.
- `PENDING` — a PR exists and a review is not yet running, or the last report
  became stale and another permitted round is needed.
- `IN_PROGRESS` — the required independent reviewer pass is running.
- `CLEAN` — all required reviewers completed the current base/head pass with
  zero unresolved findings.
- `FINDINGS` — all required reviewers completed the current pass with one or
  more unresolved findings; the worker waits in `AWAITING_AUTHOR_DECISION`.
- `BLOCKED` — a reviewer cannot complete or the review cannot safely proceed;
  merge authorization is blocked.
- `LIMIT_REACHED` — 2 completed review rounds have been reached; no third
  reviewer pass may start, and the author agent must act on the follow-up
  report alone.
- `AUTHOR_DECISION_RECORDED` — the author agent recorded its final action and
  rationale; merge eligibility still depends on that action, current SHAs,
  and every independent repository gate.

Use these exact fields in the `review` object:

```yaml
review:
  status: PENDING
  reviewer_agents: ["Ralph Code Reviewer"]
  reviewed_base_sha: null
  reviewed_head_sha: null
  rounds_completed: 0
  max_rounds: 2
  unresolved_finding_count: 0
  author_decision:
    status: NOT_REQUIRED
    choice: null
    rationale: null
    recorded_at_utc: null
```

`reviewer_agents` lists the independent `Ralph Code Reviewer` and, when the
diff is security-sensitive, `Ralph Security Reviewer`. Store the PR's current
base and head SHAs in `pull_request.base_sha` and `pull_request.head_sha`;
`reviewed_base_sha` and `reviewed_head_sha` identify the exact completed
report. Both must equal the current PR SHAs before merge authorization. If
either current SHA changes, the old report is stale and cannot authorize a
merge. Below the cap, set the review back to `PENDING` until a fresh report
for both current SHAs completes. Preserve the completed-round count and the
previous report SHAs as evidence; never reset the count. After findings in
round 1, the author agent acts on the report before one follow-up review. A
clean initial report may proceed without an unnecessary follow-up. After
round 2, set `LIMIT_REACHED`; the author agent acts on the follow-up report
alone and records its final action and rationale as
`AUTHOR_DECISION_RECORDED`. Do not launch a third reviewer pass.

One review round is one complete pass for one exact base/head pair. The first
completed reviewer report counts as round 1; if a security review is required,
its report and the code review report for that same pair are part of the same
pass.
Increment `rounds_completed` only when all required reviewers have completed
that pass; `max_rounds` is always exactly 2. A completed clean pass sets
`unresolved_finding_count` to 0. Keep reported findings unresolved until a
fresh report verifies them or the author agent explicitly chooses to accept
the remaining findings after the final report.

`author_decision.status` is exactly `NOT_APPLICABLE`, `NOT_REQUIRED`,
`PENDING`, or `RECORDED`. Use `NOT_APPLICABLE` for a no-PR fast-forward,
`NOT_REQUIRED` before findings need action or after a clean report, and
`PENDING` after findings or at the two-round limit until the author agent acts.
The only choices are `FIX_MANUALLY`, `ACCEPT_FINDINGS_AND_REQUEST_MERGE`,
`ESCALATE_FOR_HUMAN_REVIEW`, and `CLOSE`; use `choice: null` unless status is
`RECORDED`. Record the choice, non-empty rationale, and
`recorded_at_utc`. After round 2, the author agent's final action is
mandatory. Accepting findings permits only normal merge consideration; it
does not waive CI, branch protection, or required human approval.
`FIX_MANUALLY` followed by a new commit makes the report stale; obtain any
required human review through the normal process, not a third agent review.
`CLOSE` does not authorize a merge.

For a `NOT_OPENED` fast-forward iteration, the review record is explicitly
not applicable and carries no reviewer or author decision:

```yaml
pull_request:
  status: NOT_OPENED
  number: null
  url: null
review:
  status: NOT_APPLICABLE
  reviewer_agents: []
  reviewed_base_sha: null
  reviewed_head_sha: null
  rounds_completed: 0
  max_rounds: 2
  unresolved_finding_count: 0
  author_decision:
    status: NOT_APPLICABLE
    choice: null
    rationale: null
    recorded_at_utc: null
```

### Iteration history and merge evidence

- Keep the agent's `status.md` current; keep `iteration_history` in its
  `progress.md`. Add one entry for each worker iteration and retain prior
  entries. Do not replace earlier evidence on a retry. Every fresh-branch
  retry gets its own branch/agent folder and dashboard index entry. If
  a single-branch iteration is rebased onto newer `origin/main`, record the
  new SHA in `rebased_onto_origin_main_sha`. For a parent/child run, record a
  child's latest parent tip in `rebased_onto_parent_sha` and the parent's
  latest main base in `parent_rebased_onto_origin_main_sha`. Update the final
  `implementation_commit_sha`, rerun relevant checks, and obtain a new
  sign-off bound to that rewritten SHA.
- Record the implementation SHA separately from its integration SHA. In a
  parent/child run, a worker's `worker_to_parent_merge.sha` and the parent's
  `parent_to_main_merge.sha` may differ from each other and from the worker's
  `implementation_commit_sha`, including after squash or merge-queue
  integration. Verify each worker merge on the parent and the final parent
  merge on fetched `origin/main`, recording the verified ref and tip,
  verification method, and time. Do not require an implementation commit
  itself to remain an ancestor after squash integration.
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

### Per-branch time and token usage

Every schema-version-2 agent leaf and its matching aggregate
`branch_agent_index` record carry the same branch-local `resource_usage`
object:

```yaml
resource_usage:
  time_spent_seconds: 600
  time_basis: WALL_CLOCK_ELAPSED
  token_spend:
    status: NOT_REPORTED
    input_tokens: null
    output_tokens: null
    total_tokens: null
    cached_input_tokens: null
    source: null
```

The example duration is illustrative; record the measured elapsed seconds.
`time_spent_seconds` is the wall-clock difference from that leaf's
`started_at_utc` to its report's `updated_at_utc`, in seconds. The
`time_basis: WALL_CLOCK_ELAPSED` label is required: this is elapsed time,
including pauses and non-coding work, not active coding time. Recompute it
whenever `updated_at_utc` changes. If either timestamp is unavailable for a
legacy report, use `null` rather than inventing a duration.

`token_spend` records provider-reported token counters only; it is not a
monetary cost estimate. Its fields are `input_tokens`, `output_tokens`,
`total_tokens`, and `cached_input_tokens`, plus `source` naming the provider
or session-usage source when known (`null` otherwise). Use non-negative
integers only for counters the provider reports; do not estimate missing
counters, derive `total_tokens` from other fields, or treat null as zero.

Use these `token_spend.status` values:

- `REPORTED` when the provider reports all four counters.
- `PARTIAL` when at least one counter is provider-reported and one or more
  counters are unavailable; store exact reported integers and `null` for each
  unavailable counter.
- `NOT_REPORTED` when no provider token counter is available; set all four
  counters to `null` (never zero) and set `source` to the known source or
  `null`.

`cached_input_tokens` is a subset of `input_tokens`; it is already included
there and must not be added again to `total_tokens`. When input is reported,
the cached-input count cannot exceed it. Each branch-index object's
`resource_usage` must exactly mirror its leaf's current object in the same
coordinator/worker synchronization cycle; these are per-branch values, not
run-wide sums.

### Parent/child integration, rebase, and cleanup

Keep the upstream status layout: `docs/ralph-status.md` remains the one
coordinator-owned dashboard, and the branch/agent index continues to point to
the canonical `docs/ralph/<branch-slug>/agents/<agent-id>/status.md` and
`progress.md` leaves. Do not create a per-run dashboard or copy full
iteration/rebase history into the aggregate dashboard.

In a parent/child run, record the coordinator's parent branch, parent
worktree, and `parent_base_origin_main_sha` in its current leaf status and
progress records. The parent branch/worktree are created from `origin/main`.
Record a child's exact branch and worktree in its worker leaf; each child
branch and worktree is based on the current parent tip, **not** directly on
`origin/main`. The child's `base_parent_sha` is the exact parent commit used
as its base. Preserve the run's canonical `base_origin_main_sha` as the
parent's original main base.

Integrate child branches serially into the parent. Record each current
`worker_to_parent_merge` with its exact merge SHA, `verified_parent_ref`,
`verified_parent_sha`, verification method, and UTC time. A push, local
unverified merge, or child merge by itself does not complete the run. Only
after all worker merges and final acceptance checks are verified does the
coordinator integrate the completed parent to `origin/main`. Record the
current `parent_to_main_merge` SHA, `verified_remote_ref`,
`verified_origin_main_sha`, verification method, and UTC time in the
coordinator's run/leaf state. Verify that final merge on fetched
`origin/main`; no worker child branch merges directly to `origin/main`.
Use `PENDING`, `VERIFIED`, or `BLOCKED` for both worker-to-parent and
parent-to-main merge-object `status` values. A merge is `VERIFIED` only when
the exact resulting merge SHA is reachable from the target parent/main ref
and the observed target tip, verification method, and time are recorded.

Use these current-state fields in the canonical leaf records:

- Parent: `parent_branch`, `parent_worktree`,
  `parent_base_origin_main_sha`, `parent_rebased_onto_origin_main_sha`,
  `parent_implementation_commit_sha`, `parent_to_main_merge`, and
  `parent_cleanup`.
- Worker child: `branch`, `worktree`, `parent_branch`, `parent_worktree`,
  `parent_base_origin_main_sha`, `base_parent_sha`,
  `rebased_onto_parent_sha`, `implementation_commit_sha`,
  `worker_to_parent_merge`, and `cleanup`.
- `parent_to_main_merge` records the parent-only remote integration. A child
  worker's `worker_to_parent_merge` records the child-to-parent integration;
  do not represent that merge as a verified child-to-main merge.

Keep rebase evidence append-only in the owning `progress.md`: record parent
rebases in the coordinator's `parent_rebase_history` and child rebases in the
worker's `child_rebase_history`, including old and new parent SHAs, rewritten
implementation commit SHA, exact retest commands/results, and timestamps.
The current status fields are `parent_rebased_onto_origin_main_sha` for a
parent rebased onto newer `origin/main` and `rebased_onto_parent_sha` for a
child rebased onto a newer parent. A rewritten child commit needs fresh checks
and a new self-attestation bound to its exact new implementation SHA. If a
parent rebase rewrites a previously verified child merge, preserve the old
merge proof in `worker_to_parent_merge_history`, update the current merge
record, and verify it again on the rebased parent.

Cleanup follows integration, never the reverse. After a worker-to-parent
merge is verified, the coordinator may remove that child's worktree/local
branch and, when published, its remote ref if repository policy permits. The
parent worktree/local branch may be removed only after the parent-to-main
merge is verified on fetched `origin/main`. Keep branches and worktrees for
unmerged changes; never force-delete an unmerged branch. Record worktree and
local-branch cleanup as `PENDING`, `REMOVED`, or `BLOCKED`; record remote-ref
cleanup as `NOT_PUBLISHED`, `PENDING`, `DELETED`, or `BLOCKED`. Record
safe-cleanup failures as blockers and preserve the affected branch/worktree.

### Current-state leaf and append-only evidence

Every agent's `status.md` describes only the current state of that
branch/agent assignment. It must identify at least the run and task IDs,
stable `worker_id` and `worker_name`, `runtime_agent_id` (or `null`), branch
and slug, worker worktree, current iteration and `status`, base/rebased
`origin/main` SHAs, current implementation commit, checks, blockers, next
action, PR state, decision-record path, `merge_actor_worker_id`, merge
verification state, sign-off/signature state, the full `review` object above,
and the current `resource_usage` object. For a PR, record its current
`base_sha` and `head_sha` alongside the PR state so the stored review SHAs can
be compared before authorization. The coordinator copies the same review
evidence into that branch/agent's dashboard entry. For parent/child work,
also include the parent branch/worktree/base and the worker's original
`base_parent_sha` and latest `rebased_onto_parent_sha`, plus the appropriate
worker-to-parent or parent-to-main merge records and cleanup state.
It may be written as Markdown with a YAML block or a table, but keep the
field names and enum values unambiguous.

### Learning handoff

Each coordinator and worker includes this `memory_handoff` in its current
leaf `status.md` and returns the same object with its sign-off/final report.
The coordinator's aggregate report must preserve its own handoff and every
worker's handoff without inferring missing reports:

```yaml
memory_handoff:
  implementation_summary: "<concise summary of what was implemented>"
  lesson_candidates:
    - rule: "<reusable proposed rule>"
      why: "<why the rule matters>"
      scope: "<optional applicability>"
      evidence:
        - "<specific source, test/check, review correction, or integration observation>"
  no_durable_lessons_reason: null
```

`lesson_candidates` may be an empty list. When it is empty,
`no_durable_lessons_reason` must explain why; when candidates are present,
that reason is `null`. Each candidate needs a reusable `rule`, a `why`, and
specific `evidence`; `scope` is optional. Report only lessons that may outlive
the current task, not task chronology or speculation. Never include
credentials, secrets, or personal data. This handoff is evidence for the
post-merge **Project Memory Update** agent, not authorization to change shared
memory before the final implementation merge is verified on fetched
`origin/main`.

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
schema_version: 2
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
    active_worker_count: 0
    base_origin_main_sha: "<full SHA>"
    created_at_utc: "2026-09-25T00:00:00Z"
    updated_at_utc: "2026-09-25T00:00:00Z"
    next_action: "Worker-02: record the author decision for the current review findings."
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
    status: AWAITING_REVIEW
    iteration: 1
    merge_actor_worker_id: null
    pull_request:
      status: OPEN
      number: "<PR number>"
      url: "<PR URL>"
      base_sha: "<current full base SHA>"
      head_sha: "<current full head SHA>"
    review:
      status: IN_PROGRESS
      reviewer_agents: ["Ralph Code Reviewer"]
      reviewed_base_sha: null
      reviewed_head_sha: null
      rounds_completed: 0
      max_rounds: 2
      unresolved_finding_count: 0
      author_decision:
        status: NOT_REQUIRED
        choice: null
        rationale: null
        recorded_at_utc: null
    resource_usage:
      time_spent_seconds: 600 # illustrative; calculate from the leaf timestamps
      time_basis: WALL_CLOCK_ELAPSED
      token_spend:
        status: NOT_REPORTED
        input_tokens: null
        output_tokens: null
        total_tokens: null
        cached_input_tokens: null
        source: null
    status_path: "docs/ralph/ralph-orchestration-worker-01-<unique-id>/agents/worker-01/status.md"
    progress_path: "docs/ralph/ralph-orchestration-worker-01-<unique-id>/agents/worker-01/progress.md"
    decision_record_path: "docs/decisions/ralph-orchestration-worker-01-<unique-id>/agents/worker-01/pr-pending.md"
    decision_index_path: "docs/decisions/ralph-orchestration-worker-01-<unique-id>/README.md"
    next_action: "Coordinator: finish the code review for the current PR SHAs."
  - run_id: "<run-id>"
    task_ids: ["<task-id>"]
    worker_id: "worker-02"
    worker_name: "worker-02 / status schema"
    branch: "ralph/status-schema-worker-02-<unique-id>"
    branch_slug: "ralph-status-schema-worker-02-<unique-id>"
    status: AWAITING_AUTHOR_DECISION
    iteration: 1
    merge_actor_worker_id: null
    pull_request:
      status: OPEN
      number: "<PR number>"
      url: "<PR URL>"
      base_sha: "<reviewed full base SHA>"
      head_sha: "<reviewed full head SHA>"
    review:
      status: FINDINGS
      reviewer_agents: ["Ralph Code Reviewer", "Ralph Security Reviewer"]
      reviewed_base_sha: "<reviewed full base SHA>"
      reviewed_head_sha: "<reviewed full head SHA>"
      rounds_completed: 1
      max_rounds: 2
      unresolved_finding_count: 2
      author_decision:
        status: PENDING
        choice: null
        rationale: null
        recorded_at_utc: null
    resource_usage:
      time_spent_seconds: 420 # illustrative; calculate from the leaf timestamps
      time_basis: WALL_CLOCK_ELAPSED
      token_spend:
        status: NOT_REPORTED
        input_tokens: null
        output_tokens: null
        total_tokens: null
        cached_input_tokens: null
        source: null
    status_path: "docs/ralph/ralph-status-schema-worker-02-<unique-id>/agents/worker-02/status.md"
    progress_path: "docs/ralph/ralph-status-schema-worker-02-<unique-id>/agents/worker-02/progress.md"
    decision_record_path: "docs/decisions/ralph-status-schema-worker-02-<unique-id>/agents/worker-02/pr-<number>.md"
    decision_index_path: "docs/decisions/ralph-status-schema-worker-02-<unique-id>/README.md"
    next_action: "Worker-02: review findings and record the next author action."
```

The branch/agent index is deliberately explicit rather than a glob-only list:
the coordinator must refresh it when folders are added and check it against
the repository tree at each loop boundary.

### Agent leaf status example

The following is the current-state shape for one agent's `status.md`; detailed
iteration history and full check evidence remain in its sibling `progress.md`.

```yaml
schema_version: 2
run_id: "<stable run ID>"
task_ids: ["<task ID>"]
worker_id: "worker-02"
worker_name: "<stable display name>"
runtime_agent_id: "<host-provided agent/session ID or null>"
branch: "<exact branch ref>"
branch_slug: "<lowercase branch with slashes replaced by hyphens>"
iteration: 1
status: AWAITING_REVIEW
started_at_utc: "<ISO 8601 UTC timestamp>"
updated_at_utc: "<ISO 8601 UTC timestamp>"
resource_usage:
  time_spent_seconds: 420 # illustrative; calculate from started_at_utc and updated_at_utc
  time_basis: WALL_CLOCK_ELAPSED
  token_spend:
    status: NOT_REPORTED
    input_tokens: null
    output_tokens: null
    total_tokens: null
    cached_input_tokens: null
    source: null
base_origin_main_sha: "<full SHA>"
rebased_onto_origin_main_sha: null
implementation_commit_sha: "<exact full implementation commit SHA>"
pull_request:
  status: OPEN
  number: "<PR number>"
  url: "<PR URL>"
  base_sha: "<current full base SHA>"
  head_sha: "<current full head SHA>"
review:
  status: IN_PROGRESS
  reviewer_agents: ["Ralph Code Reviewer"]
  reviewed_base_sha: null
  reviewed_head_sha: null
  rounds_completed: 0
  max_rounds: 2
  unresolved_finding_count: 0
  author_decision:
    status: NOT_REQUIRED
    choice: null
    rationale: null
    recorded_at_utc: null
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
next_action: "Coordinator: complete review for the current base/head SHAs before authorizing merge."
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

For a parent/child run, keep the canonical leaf fields above and add the
following current parent/worker integration fields to the owning leaves. Put
the full rebase and merge history in each owner's append-only `progress.md`,
not in `docs/ralph-status.md`.

```yaml
# Current coordinator/parent state
parent_branch: "ralph/example-parent"
parent_worktree: "<path to coordinator's parent worktree>"
parent_base_origin_main_sha: "<full origin/main SHA used to create the parent>"
parent_rebased_onto_origin_main_sha: null
parent_implementation_commit_sha: null
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

# Current worker-child state
branch: "ralph/example-worker-02"
worktree: "<path to worker-02 worktree>"
parent_branch: "ralph/example-parent"
parent_worktree: "<path to coordinator's parent worktree>"
parent_base_origin_main_sha: "<same parent main base SHA>"
base_parent_sha: "<full parent tip used to create this child branch>"
rebased_onto_parent_sha: null
worker_to_parent_merge:
  status: PENDING
  sha: null
  verified_parent_ref: "refs/heads/ralph/example-parent"
  verified_parent_sha: null
  verification_method: null
  verified_at_utc: null
cleanup:
  worktree: PENDING
  local_branch: PENDING
  remote_ref: NOT_PUBLISHED
```

When a child is rebased, retain its original `base_parent_sha`, set
`rebased_onto_parent_sha` to the exact new parent tip, and append the previous
and new parent SHAs, rewritten implementation SHA, retest evidence, and time
to that worker's progress history. When the parent is rebased, update
`parent_rebased_onto_origin_main_sha` and append the old/new parent and main
SHAs and retest evidence to the coordinator's progress history. If a parent
rebase rewrites a verified child integration, append the old merge proof to
the worker's `worker_to_parent_merge_history` before replacing the current
verification.

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
  "parent_branch": "<coordinator's parent branch>",
  "parent_worktree": "<coordinator's parent worktree path>",
  "parent_base_origin_main_sha": "<full origin/main SHA used for the parent>",
  "base_parent_sha": "<full parent branch SHA used as this child's base>",
  "rebased_onto_parent_sha": "<full parent SHA after child rebase, or null>",
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
