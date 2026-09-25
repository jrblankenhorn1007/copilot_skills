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
again at the start of each worker iteration. If workers have separate
integration worktrees, each worker performs its own pulls. If workers share an
integration worktree, the coordinator serializes the pulls before launching
that worker; never have workers concurrently pull the same worktree. In
either case, the worker must reopen the current skills before editing. If the
refresh cannot safely complete, stop that iteration and preserve the affected
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
2. Create a fresh worktree and unique branch from the latest `origin/main`.
   For behavior changes, follow Red-Green-Refactor; for documentation-only
   changes, run the relevant documentation checks. Update this branch/agent's
   `docs/ralph/<branch-slug>/agents/<agent-id>/status.md` and `progress.md`
   on every loop, and coordinate the same-cycle aggregate-dashboard refresh
   with the coordinator. Maintain this branch's
   `docs/decisions/<branch-slug>/` index and a separate per-agent, per-PR
   record; use `pr-not-opened.md` when the normal integration path does not
   open a PR. Record recovered issues and successful verification there, not
   as unresolved blockers.
3. Run the scoped checks, commit the change, and report its base SHA, branch,
   commit SHA, changed paths, verification commands/results, and any blocker.
   Report `AWAITING_MERGE` after sign-off; the iteration is not complete until
   its remote merge is verified on `origin/main` and the coordinator's required
   post-merge memory review is complete.

### Worker-owned PR merge

The coordinator authorizes one worker PR at a time after reviewing its
sign-off, checks, and integration readiness. The worker who owns the branch
executes its own PR merge, using its own already-authenticated GitHub CLI
session and the repository's normal merge or merge-queue process. The
coordinator does not use its own credentials to merge a worker PR; it verifies
the resulting remote merge and owns the post-merge memory review. See the
[worker-owned PR merge guide](worker-pr-merging.md) for the exact protocol.

Never use `--admin` or override managed policy. If the worker's merge
permission is denied, preserve the branch and PR and report a sanitized
blocker. Do not hand off credentials or push directly to `main`.

The coordinator maintains the aggregate ledger at `docs/ralph-status.md` with
each assignment's worker, owned paths, dependencies, acceptance criteria,
base SHA, branch/commit, PR number or explicit no-PR state, branch
decision-record path, check results, implementation merge SHA,
`merge_actor_worker_id`, memory-review outcome and any memory follow-up merge
SHA, and state (for example: queued, ready, running, awaiting integration,
merged-and-verified, or blocked). Record evidence from the worker; do not mark
an assignment complete or release dependent work merely because a branch was
pushed or a pull request was opened.

After each worker's implementation merge is verified, the coordinator performs
the post-merge memory review using the
[Project Memory skill](../../project-memory/SKILL.md). The coordinator owns
changes to shared memory: workers do not edit the shared memory store on
feature branches, and memory updates use a fresh follow-up branch and the
repository's normal merge process. Verify any memory merge before marking the
iteration complete or releasing dependent work. Record a no-new-lesson outcome
when the review finds nothing durable. A memory-only follow-up is part of the
same iteration and does not recursively trigger another review.

After memory review is complete, the coordinator updates the ledger, evaluates
the acceptance criteria, and unlocks any satisfied dependencies. If the
assigned outcome is complete, the worker can take a different ready
assignment. If more work is needed for the same outcome, dispatch a new,
narrowly scoped iteration with the remaining criteria. Every re-dispatch
starts from a new worktree and branch based on the latest `origin/main`; do
not continue on the old iteration branch. Use only project-required
completion markers, and only after all required remote-main merges are
verified.

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

Keep branch decision indexes and per-agent/PR decision records at
`docs/decisions/<branch-slug>/README.md` and
`docs/decisions/<branch-slug>/agents/<agent-id>/pr-*.md`; use
`pr-not-opened.md` when no PR is part of the integration path. A worker stays
`AWAITING_MERGE` until the coordinator verifies integration and completes the
required post-merge memory review, including any warranted memory follow-up.
Only after that confirmation may the worker's leaf and dashboard status become
`COMPLETE`; update both sides together so their summaries remain synchronized.

## Git synchronization and integration

For both the coordinator and workers, never open, navigate, or automate a
browser for Git or GitHub repository operations. Use the Git CLI (`git`) for
local repository operations—status, diff, fetch/pull, branch/worktree, rebase,
commit, and push. Use the configured GitHub CLI (`gh`) or supported GitHub
integration/MCP tools for pull requests, checks, reviews, and merges. If the
required CLI or integration is unavailable or not authorized, report a
blocker; do not fall back to a browser. Continue to follow the existing Git
identity and authentication rules.

1. **Before branch creation:** after the per-iteration pull and skill refresh,
   follow the parent Ralph Loop skill's Git identity and authentication
   preflight, including `git fetch origin`. Confirm `origin/main` is available
   and create the worker's fresh branch from that ref. Fetch success proves
   read access only, so branch-push and merge permissions must be established
   through the repository's normal integration process. Preserve the worker
   branch and report a sanitized blocker if either write operation is denied;
   never pass credentials in worker instructions or change credential
   configuration without approval. Record the exact base SHA for the
   coordinator's ledger.
2. **Before publishing and again before integration:** run `git fetch origin`.
   If `origin/main` has advanced since the recorded base, rebase the feature
   branch onto the latest `origin/main`. Resolve conflicts only within the
   worker's ownership; stop and coordinate if a conflict reveals overlapping
   scope or a changed shared contract. Rerun all relevant checks after the
   rebase before publishing or requesting integration.
3. **Never force-push.** Prefer rebasing before first publication. If updating
   an already-published branch after a rebase would require a force-push,
   leave it intact and coordinate a fresh branch from current `origin/main`
   with only the unmerged changes replayed, then rerun checks and use the
   repository's normal publish process.
4. **Serialize authorization and worker-owned integration.** The coordinator
   authorizes one worker PR at a time; the branch-owning worker performs that
   PR's merge. A repository merge queue may serialize the actual merge, but
   it does not replace coordinator authorization or change the worker merge
   actor. After every update to `main`, run `git fetch origin` again and
   re-sync any remaining stale branches; rerun their checks after rebasing and
   before authorizing their merge. Do not rely on a branch's earlier
   up-to-date check after another worker has changed `main`.
5. **Verify every merge:** the worker merge actor records the SHA produced by
   the repository's remote merge process, fetches `origin`, and confirms that
   exact merge SHA is reachable from `origin/main` (for example, with
   `git merge-base --is-ancestor <merge-sha> origin/main`). Record the actor
   as `merge_actor_worker_id` in the worker status. The coordinator
   independently verifies the remote result before marking the worker
   complete or dispatching dependent work. With squash or merge-queue
   integration, verify the resulting merge SHA, not just the worker's
   original commit.

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
