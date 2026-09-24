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

1. Confirm its assigned outcome, acceptance criteria, dependencies, and owned
   paths with the coordinator. Read relevant memory before work and stay
   within the assigned scope.
2. Create a fresh worktree and unique branch from the latest `origin/main`.
   For behavior changes, follow Red-Green-Refactor; for documentation-only
   changes, run the relevant documentation checks. Update progress, status,
   and decision records only as required by the project's protocol.
3. Run the scoped checks, commit the change, and report its base SHA, branch,
   commit SHA, changed paths, verification commands/results, and any blocker.
   The iteration is not complete until its remote merge is verified on
   `origin/main`.

The coordinator maintains a ledger with each assignment's worker, owned
paths, dependencies, acceptance criteria, base SHA, branch/commit, check
results, implementation merge SHA, memory-review outcome and any memory
follow-up merge SHA, and state (for example: queued, ready, running, awaiting
integration, merged-and-verified, or blocked). Record evidence from the
worker; do not mark an assignment complete or release dependent work merely
because a branch was pushed or a pull request was opened.

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

## Git synchronization and integration

1. **Before branch creation:** fetch `origin`, confirm `origin/main` is
   available, and create the worker's fresh branch from that ref. Record the
   exact base SHA for the coordinator's ledger.
2. **Before publishing and again before integration:** fetch `origin`. If
   `origin/main` has advanced since the recorded base, rebase the feature
   branch onto the latest `origin/main`. Resolve conflicts only within the
   worker's ownership; stop and coordinate if a conflict reveals overlapping
   scope or a changed shared contract. Rerun all relevant checks after the
   rebase before publishing or requesting integration.
3. **Never force-push.** Prefer rebasing before first publication. If updating
   an already-published branch after a rebase would require a force-push,
   leave it intact and coordinate a fresh branch from current `origin/main`
   with only the unmerged changes replayed, then rerun checks and use the
   repository's normal publish process.
4. **Serialize integration.** The coordinator should integrate one worker
   branch at a time. A repository merge queue may provide equivalent
   serialization, but after every update to `main`, fetch `origin` again and
   re-sync any remaining stale branches; rerun their checks after rebasing
   and before their integration. Do not rely on a branch's earlier
   up-to-date check after another worker has changed `main`.
5. **Verify every merge:** record the SHA produced by the repository's remote
   merge process, fetch `origin`, and confirm that exact merge SHA is
   reachable from `origin/main` (for example, with
   `git merge-base --is-ancestor <merge-sha> origin/main`) before marking the
   worker iteration complete or dispatching dependent work. With squash or
   merge-queue integration, verify the resulting merge SHA, not just the
   worker's original commit.

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
