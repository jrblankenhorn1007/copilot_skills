# Multi-Agent Ralph Loop Orchestration

The first, top-level **Ralph Loop** invocation is the **Orchestrator**
(coordinator), not an implementation worker. Its first run reads the project
plan, splits ready work, and dispatches the configured worker agents before
implementing any worker assignment itself. The orchestrator is not counted in
`workers=N`. This is the default multi-agent workflow under the
[Ralph Loop skill](../SKILL.md); behavior changes also follow the
[TDD skill](../../tdd/SKILL.md). Each worker performs one complete, isolated
Ralph iteration and follows the active project's instructions and status
protocol.

## Per-iteration repository and skill refresh

The orchestrator and every worker iteration, including a re-dispatch after a
merge, must complete the per-iteration refresh in the
[Ralph Loop skill](../SKILL.md#refresh-repositories-and-instructions-on-every-iteration)
before planning or editing. This pulls the canonical `copilot_skills` checkout
and the active project's primary integration worktree with
`git pull --ff-only`, then re-reads the applicable skills and project
instructions. If both checkouts are the same repository, pull it once.

The coordinator performs and records the refresh before planning its run and
again immediately before each worker iteration. When workers share the
canonical or active-project integration worktree, the coordinator serializes
any required `git pull --ff-only` before dispatch; workers must not
concurrently pull or update that shared main worktree. If separate integration
worktrees need refreshing, refresh them one at a time and record their
resulting SHAs. In every case, each worker reopens the current skills before
editing and receives the exact parent branch and tip to use. If the refresh
cannot safely complete, stop that iteration and preserve the affected
worktrees.

## Role configuration

Resolve the run configuration before launching the top-level session. Supply
it in the request or through the selected harness's supported session controls:

```yaml
orchestrator:
  model: null
  reasoning_effort: null
  context_tier: null
workers:
  count: 2
  model: inherit
  reasoning_effort: inherit
  context_tier: inherit
  overrides: {}
```

For the orchestrator, `null` means use the model and parameters selected for
the initial session or the harness defaults. Worker fields can be configured
independently; `inherit` uses the orchestrator's value, and
`overrides.<worker-id>` can replace the shared worker setting for a specific
worker. Set the orchestrator profile before starting the first session and
apply each worker's profile when launching that worker. Model IDs, reasoning
effort, context tier, and any additional parameters must be supported by the
selected model and harness. If a harness cannot apply a requested
worker-specific setting, report that limitation and use the supported
inherited/default value rather than claiming the override was applied. This
block defines run behavior; it is not a new Copilot settings-file schema.

## Worker count and split plan

An orchestration request may specify `workers=N`, the desired number of
concurrent worker agents. If omitted, use the default `workers=2`. `N` counts
workers only, not the orchestrator; it is a parallelism request, not a target
number of iterations or a reason to invent work.

In the first run, the coordinator reads the project's plan, instructions,
current status, relevant memory categories, and working-tree state, then
writes a split plan and launches the ready workers. When at least `N` useful,
independent assignments are ready, launch exactly `N` workers in that first
run. If fewer than `N` ready assignments can advance acceptance criteria
safely, launch only that smaller number. Do not pad the run with overlapping,
duplicate, or speculative tasks.

Each assignment should state:

- a bounded outcome and observable acceptance criteria, including relevant
  checks;
- exclusive path ownership, covering implementation, tests, and documentation
  that belong to the change;
- dependencies and the condition that makes the assignment ready.

Keep worker-owned paths disjoint. Give a shared interface or file to one
worker, or serialize the changes to it; do not ask concurrent workers to edit
the same paths. Dispatch only work whose dependencies are satisfied. If a
dependency is still being built, leave its dependents queued rather than
having workers wait on or duplicate that work.

The coordinator can fill newly available worker slots as dependencies clear
or more useful work is identified, applying the configured worker profile to
each new dispatch.

## Worker iterations and coordinator tracking

Each dispatch gives one worker one scoped Ralph iteration, not a long-lived
shared checkout. The worker must:

1. Complete or verify the per-iteration repository and skill refresh, then
   confirm its assigned outcome, acceptance criteria, dependencies, and owned
   paths with the coordinator. Read relevant memory before work and stay
   within the assigned scope.
2. Work in a fresh child worktree and unique child branch based on the exact
   current tip of the coordinator parent branch, not directly on
   `origin/main`. The coordinator first creates the parent worktree and branch
   from the latest fetched `origin/main`. Record the parent `origin/main` base
   SHA, parent branch/worktree, and child `base_parent_sha`. If the parent
   advances before integration, rebase the child onto its latest tip, record
   `rebased_onto_parent_sha`, rerun relevant checks, and obtain a new sign-off
   bound to the rewritten implementation commit.

   Store each worker current-state summary and dated verification evidence at
   `docs/ralph/<branch-slug>/agents/<agent-id>/status.md` and `progress.md`.
   Update both leaf files on every loop and worker-state transition, preserving
   prior progress evidence; keep the coordinator-owned `docs/ralph-status.md`
   synchronized through the coordinator rather than editing it directly. A
   worker reports `AWAITING_MERGE` after sign-off and remains in that state
   until the coordinator verifies its worker-to-parent integration. The
   worker may then become `COMPLETE`; the overall run remains in progress
   until the final parent-to-main merge is verified on fetched `origin/main`
   and the post-merge memory review is complete.

   For behavior changes, follow Red-Green-Refactor; for documentation-only
   changes, run the relevant documentation checks. Maintain this child branch
   `docs/decisions/<branch-slug>/` index and a separate per-agent, per-PR
   record; use `pr-not-opened.md` when child-to-parent integration does not
   open a PR, and state why. Record recovered issues and successful
   verification there, not as unresolved blockers.
3. Run scoped checks, commit the implementation and any required metadata,
   and report `base_parent_sha`, `rebased_onto_parent_sha` when applicable,
   branch, implementation commit SHA, changed paths, verification
   commands/results, and any blocker. The worker integration target is the
   parent branch; workers do not merge their child branches directly to
   `origin/main`. For a PR-backed child-to-parent integration, report
   `AWAITING_REVIEW` after sign-off; the coordinator completes the review gate
   below before authorizing the child branch owner to merge that PR into the
   parent. For a no-PR child-to-parent fast-forward, record review
   `NOT_APPLICABLE` and let the coordinator verify the integration. If the
   parent-to-main integration uses a PR, apply the same review gate to that
   exact PR before its normal merge. A no-PR parent fast-forward retains the
   existing coordinator-managed path. The run is complete only after
   remote-main verification and the coordinator's required post-merge memory
   review.
### Independent pre-merge review gate

For every PR-backed iteration, whether child-to-parent or parent-to-main,
after branch-owner sign-off and before any merge action, the coordinator
launches an independent **Ralph Code Reviewer**. Also launch
**Ralph Security Reviewer** if the diff touches authentication or
authorization, untrusted input, secrets or sensitive data, cryptography,
process execution, external boundaries, dependencies, or security
configuration. The reviewer is not the author, follows
`.github/skills/ralph-pr-review/SKILL.md`, and is read-only; it reports
findings without editing files, applying fixes, or merging.
Complete review before coordinator authorization for a worker-owned child PR
and before the coordinator merges its own parent PR.

Each review pass is bound to the exact full base and head commit SHAs. Before
authorization, the coordinator confirms both still match the current PR. A
changed base or head invalidates the earlier report and blocks merge until a
fresh review is complete. A clean report is evidence only; it does not
guarantee correctness or replace required CI, branch protection rules, or
human approvals.

Keep review findings evidence-bounded and grounded in the changed code and
available project context. Prioritize design, functionality, edge cases,
complexity, correctness, and tests. Noncritical personal style preferences
and nits are not merge blockers unless they violate a written project
standard. Use structured findings and an adversarial check for relevance;
do not add unverified numeric scores or broad autonomous fixing.

There are at most **2 completed review rounds per branch/PR**: one initial
review and, when needed, one follow-up review after the author agent acts on
the first report. One round is one complete pass for an exact base/head pair; any
required code and security reports for that pair form one pass. A clean
initial report may proceed through the normal merge gates without an
unnecessary follow-up. After round 2, the author agent acts on the follow-up
report alone, records its final action and rationale, and does not launch a
third reviewer pass. Its choices are `FIX_MANUALLY`,
`ACCEPT_FINDINGS_AND_REQUEST_MERGE`, `ESCALATE_FOR_HUMAN_REVIEW`, or `CLOSE`.
Acceptance permits only normal merge consideration and does not override
required CI, branch protection, or human approval. A later base/head change
remains stale; if the author agent changes the head after the follow-up, do
not merge on that stale report. Obtain any required human review or continue
through a new PR under the normal process, not a third agent review on the
same branch/PR.

When a child-to-parent or parent-to-main integration uses a coordinator-managed
fast-forward without a PR, set review status to `NOT_APPLICABLE`, launch no
reviewers, and preserve that existing path.

### Worker-owned PR merge

The coordinator authorizes one worker PR at a time after reviewing its
sign-off, checks, and integration readiness. The worker who owns the branch
executes its own PR merge, using its own existing authentication through the
configured GitHub CLI (`gh`) or supported GitHub integration/MCP tools and the
repository's normal merge or merge-queue process. The coordinator does not
use its own credentials to merge a worker PR; it verifies the resulting
remote merge and owns the post-merge memory review. See the
[worker-owned PR merge guide](worker-pr-merging.md) for the exact protocol.

Never use `--admin` or override managed policy. If the worker's merge
permission is denied, preserve the branch and PR and report a sanitized
blocker. Do not hand off credentials or push directly to `main`.

The coordinator maintains the aggregate ledger at `docs/ralph-status.md` with
the parent branch/worktree and its `origin/main` base; each assignment's
worker, owned paths, dependencies, acceptance criteria, child base and rebase
SHAs, branch and implementation commit, PR number or explicit no-PR state,
branch decision-record path, and exact check results. For every PR, also
record review status and reviewer agents, current and reviewed base/head SHAs,
rounds completed and maximum, unresolved finding count, and any explicit
author decision and rationale. Record the worker-to-parent merge SHA and
verification, the implementation/remote merge SHA and verification where
applicable, and `merge_actor_worker_id` for a worker-owned PR merge. Also
record the final parent-to-main merge SHA and verification,
worktree/branch/remote-ref cleanup state, memory-review outcome and any
memory follow-up merge SHA, and current state (for example: queued, ready,
running, awaiting review, awaiting author decision, awaiting integration,
merged-and-verified, or blocked). Record evidence from the worker; do not
mark an assignment complete or release dependent work merely because a
branch was published or a pull request was opened.


The coordinator serializes child-branch integration into the parent branch.
After each worker-to-parent merge, verify the resulting integration SHA is
reachable from the parent branch before marking that worker complete or
releasing dependent work. Once all child changes are integrated, run the
final acceptance checks on the parent branch, merge the parent to remote
`origin/main` through the repository's normal process, fetch, and verify the
resulting remote-main merge SHA. Only after that parent merge is verified does
the coordinator perform the post-merge memory review using the
[Project Memory skill](../../project-memory/SKILL.md). The coordinator owns
changes to shared memory: workers do not edit the shared memory store on
feature branches, and memory updates use a fresh follow-up branch and the
repository's normal merge process. Verify any memory merge before marking the
overall run complete. Record a no-new-lesson outcome
when the review finds nothing durable. A memory-only follow-up is part of the
same iteration and does not recursively trigger another review.

After each verified worker-to-parent merge, the coordinator updates the ledger,
evaluates dependencies, and can dispatch newly ready work. A re-dispatched
worker uses a fresh child worktree and branch from the then-current parent tip;
do not continue on the old child branch. After final acceptance and verified
parent-to-main integration, any new outer iteration starts from a fresh
parent worktree and branch based on the latest `origin/main`. Use only
project-required completion markers, and only after all required remote-main
merges and memory follow-ups are verified.

In the final user-facing report, begin with `Task completed: YES` or
`Task completed: NO`. Only unresolved blockers belong in the failure summary;
the branch's per-agent/per-PR decision record retains recovered issues and
their successful verification.

## Branch-scoped documentation and synchronized status

Resolve all paths from the active project's repository root. Generated Ralph
run, status, progress, and decision records belong inside that repository's
`docs/` folder; do not create or update root-level Ralph status or progress
files. Use this shared layout:

```text
docs/
  ralph-status.md
  ralph/<branch-slug>/agents/<agent-id>/
    status.md
    progress.md
  decisions/<branch-slug>/
    README.md
    agents/<agent-id>/pr-<number>.md
```

Derive `<branch-slug>` from the exact Git branch ref by lowercasing it and
replacing `/` with `-`. Use the stable run-scoped `<agent-id>` assigned by the
coordinator (for example, `worker-01`); do not use a display name or transient
runtime agent/session ID.

The coordinator is the sole owner and writer of `docs/ralph-status.md`. The
dashboard must list every existing branch/agent folder under `docs/ralph/`,
linking its `status.md` and `progress.md`, and show the current state. Each
worker owns its assigned branch/agent leaf files: `status.md` holds the
current-state summary, and `progress.md` records dated loop evidence and
verification. On every loop and every worker-state transition, the worker
updates both leaf files and sends their paths, state, and evidence to the
coordinator; the coordinator refreshes the affected dashboard entry in that
same coordination cycle. Keep the dashboard entry, leaf status, and progress
summary consistent on the run/worker state, iteration, branch, checks,
blockers, next action, and merge/memory-review state. Preserve entries for
unaffected branch/agent folders so the dashboard continues to surface all of
them. Workers do not edit the aggregate dashboard.

For schema-version-2 current reports, each leaf and its matching
`branch_agent_index` row carry the same branch-local `resource_usage` object.
Workers update the object with their leaf report; the coordinator mirrors it
into the row in that same synchronization cycle. The elapsed-seconds field
is wall-clock time from `started_at_utc` through `updated_at_utc`, not active
coding time. Token counts come only from provider-reported usage, with
unavailable counters null and the documented `REPORTED`, `PARTIAL`, or
`NOT_REPORTED` status. Preserve version-1 records as legacy rather than
inventing historical measurements. See the
[per-branch time and token usage contract](multi-agent-status.md#per-branch-time-and-token-usage)
for the field schema and cached-input rule.

Keep branch decision indexes and per-agent/PR decision records at
`docs/decisions/<branch-slug>/README.md` and
`docs/decisions/<branch-slug>/agents/<agent-id>/pr-*.md`; use
`pr-not-opened.md` when no PR is part of the integration path. In a
parent/child run, a worker stays `AWAITING_MERGE` until the coordinator
verifies its child-to-parent integration; then its leaf and dashboard entry
may become `COMPLETE`. The overall run remains `IN_PROGRESS` until the parent
merge is verified on fetched `origin/main` and the required post-merge memory
review, including any warranted memory follow-up, is complete. Update the
leaf and dashboard together so their summaries remain synchronized.

## Git synchronization and integration

For both the coordinator and workers, never open, navigate, or automate a
browser for Git or GitHub repository operations. Use the Git CLI (`git`) for
local repository operations—status, diff, fetch/pull, branch/worktree, rebase,
commit, and push. Use the configured GitHub CLI (`gh`) or supported GitHub
integration/MCP tools for pull requests, checks, reviews, and merges. If the
required CLI or integration is unavailable or not authorized, report a
blocker; do not fall back to a browser. Continue to follow the existing Git
identity and authentication rules.

1. **Create the parent before its workers:** after the per-iteration refresh,
   including the required pull and skill refresh, follow the parent Ralph
   Loop skill's Git identity and authentication preflight, including
   `git fetch origin`. Confirm that the attached integration worktree is
   clean and `origin/main` is available. Create a fresh parent worktree and
   branch from that fetched ref, for example:

   ```sh
   git worktree add -b <parent-branch> <parent-worktree> origin/main
   ```

   Record the exact `origin/main` base SHA, parent branch, and parent worktree.
   Fetch success proves read access only; branch-push and merge permissions
   must be established through the repository's normal integration process.
   Preserve branches and report a sanitized blocker if write access is denied;
   never pass credentials in worker instructions or change credential
   configuration without approval. Record the exact base SHA for the
   coordinator's ledger.
2. **Create child branches from the parent:** each worker's fresh worktree and
   unique branch must start at the current parent branch tip, for example:

   ```sh
   git worktree add -b <worker-branch> <worker-worktree> <parent-branch>
   ```

   Record the full `base_parent_sha`. Do not base a worker child branch
   directly on `origin/main`.
3. **Re-sync and retest before integration:** run `git fetch origin` before
   publishing or integrating and compare each child with the current parent
   tip. If another child has advanced the parent, rebase the stale child onto
   the latest parent branch and rerun its relevant checks. If `origin/main`
   advances, the coordinator first rebases the parent onto the latest fetched
   `origin/main`, reruns the parent checks, and then rebases/retests any
   remaining children onto the updated parent. If this rewrites an already
   verified child integration, record the old and new parent-side SHAs and
   re-verify every affected child merge on the rebased parent. Resolve
   conflicts only within owned paths; stop and coordinate when conflicts
   reveal overlapping scope or a changed shared contract. Fetch again before
   final remote integration. A fetch proves read access, not write
   permission.
4. **Never force-push.** Prefer rebasing before first publication. If updating
   an already-published child branch after a rebase would require a
   force-push, leave it intact and coordinate a fresh unique child branch from
   the current parent with only the unmerged changes replayed; rerun checks
   and use the repository's normal publish process. For a single-branch
   iteration, use a fresh branch from current `origin/main`. Do not delete an
   old branch while its changes remain unmerged.
5. **Serialize authorization and worker-owned PR merges:** for a PR-backed
   iteration, the coordinator authorizes one worker PR at a time and the
   branch-owning worker performs that PR's merge using its own authenticated
   session. A merge queue may serialize the remote merge, but does not replace
   coordinator authorization or change the worker merge actor. After every
   update to `main`, fetch `origin` again and re-sync remaining stale
   branches. Do not rely on an earlier up-to-date check after another worker
   changes `main`. A parent/child child-to-parent integration remains
   serialized in the parent; no worker child branch merges directly to
   `origin/main`.
6. **Verify each child merge on the parent:** the coordinator integrates one
   worker branch at a time. Record the resulting worker-to-parent integration
   SHA and confirm that exact SHA is reachable from the parent branch, for
   example:

   ```sh
   git merge-base --is-ancestor <worker-to-parent-merge-sha> <parent-branch>
   ```

   For squash or other non-fast-forward integration, verify the resulting
   integration SHA on the parent, not merely the worker's original commit.
   Rebase and retest remaining stale children after each parent update.
   If a worker-owned PR is part of the configured integration path, its
   branch owner records the resulting remote merge SHA and
   `merge_actor_worker_id`; verify the exact SHA against its target ref. The
   coordinator independently verifies child-to-parent integration before
   marking that worker complete or releasing dependent work.
7. **Integrate and verify the parent on remote main:** after all worker merges
   are verified on the parent, run the final acceptance checks on the parent
   worktree. Fetch `origin`; if `origin/main` advanced from the parent's base,
   rebase the parent onto the latest `origin/main` and rerun final acceptance
   checks. If that rebase rewrites child integrations, record the old/new
   parent-side SHAs and re-verify each affected child merge on the parent. Use
   the repository's required remote merge process, fetch `origin` again, and
   verify the resulting parent-to-main merge SHA on fetched `origin/main`, for
   example:

   ```sh
   git merge-base --is-ancestor <parent-to-main-merge-sha> origin/main
   ```

   With squash or merge-queue integration, verify the resulting remote-main
   SHA rather than requiring the parent's original commit to remain an
   ancestor. A child merge, parent push, local merge, or open PR alone is not
   proof of final integration.
8. **Clean up only verified merges:** after a worker-to-parent merge has been
   verified on the parent, and only if its worktree is clean, the coordinator
   may remove the worker worktree and local branch:

   ```sh
   git worktree remove <worker-worktree>
   git branch -d <worker-branch>
   ```

   If the worker branch was published, delete its remote ref only after that
   parent merge is verified and repository policy permits it:

   ```sh
   git push origin --delete <worker-branch>
   ```

   Remove the parent worktree and local branch only after its parent-to-main
   merge is verified on fetched `origin/main`:

   ```sh
   git worktree remove <parent-worktree>
   git branch -d <parent-branch>
   ```

   If the parent branch was published, delete its remote ref only after that
   verification and when policy permits it:

   ```sh
   git push origin --delete <parent-branch>
   ```

   Never delete an unmerged branch. Do not force-remove a worktree or
   force-delete a branch when Git refuses safe cleanup; preserve it and report
   the blocker.

## Example split

Request: “Implement input validation and report formatting from the current
plan; `workers=2`.” Assume both tasks use already-established contracts and
do not need to change shared files.

| Worker | Assignment | Exclusive paths | Dependency | Acceptance |
| --- | --- | --- | --- | --- |
| 1 | Validate incoming records | `src/validation/**`, `tests/validation/**` | Existing record contract | Malformed records are rejected; targeted validation tests pass. |
| 2 | Format generated reports | `src/reporting/**`, `tests/reporting/**` | Existing report contract | Required report fields are formatted; targeted formatting tests pass. |

These assignments are independent and have disjoint ownership, so the
coordinator can dispatch exactly two workers. If either task needs a shared
contract change first, assign that change to one worker and wait for its
verified merge before dispatching dependent work.
