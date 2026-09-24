---
name: ralph-loop
description: Use for Ralph-style development runs; coordinate configurable workers, capture categorized lessons, and verify remote-main integration.
---

# Ralph Loop

Use this skill to run one bounded outer software-development iteration. It
guides project discovery, worktree isolation, verification, and integration.
It does not replace the active project's plan, acceptance criteria, runner,
tests, status protocol, or decision history; read and follow those sources.

## First-run orchestration

For multi-agent work, the first top-level Ralph Loop invocation is the
orchestrator, not an implementation worker. Its first run plans and dispatches
the configured workers before taking on any worker assignment; it does not
count toward `workers=N`. The default is two workers. If fewer than two useful,
independent assignments are ready, launch only the available work and record
why; never invent or duplicate assignments to meet the default.

Configure the orchestrator's model and supported parameters for the initial
session, and configure worker defaults or per-worker overrides at dispatch.
See [multi-agent orchestration](./references/multi-agent-orchestration.md) for
the run configuration and [Copilot agent selection and model controls](./references/copilot-cli-usage.md)
for applying it in supported harnesses.

## Required setup

1. Read the active project's implementation plan, Ralph prompt or runner,
   progress log, current status snapshot, decision log, and applicable local
   instructions. Read the project's memory index and relevant categories when
   available using the [Project Memory skill](../project-memory/SKILL.md), and
   validate those lessons against current sources. Treat the active project's
   artifacts as the source of truth for scope, filenames, runner behavior, and
   completion markers.
2. Confirm the requested work advances a clear acceptance criterion. If there
   is no active task or the requested scope is unclear, ask for direction
   rather than inventing a project goal.
3. Fetch the configured remote and identify its latest `main` ref and the
   worktree where that branch is checked out. If remote `main` is unavailable,
   the integration checkout is detached, or its worktree has uncommitted
   changes, preserve the current state and report the blocker.
4. Check that any project runner supports the fresh-worktree and verified
   remote-merge lifecycle below. Do not invoke a runner that assumes an
   in-place branch, pushes before integration, or skips remote verification.

## Iteration workflow

1. Perform one coherent implementation iteration per invocation. Create a
   fresh worktree and unique branch from the latest remote `main` before
   editing, following the project's location and naming conventions. Otherwise
   use:

   ```sh
   git worktree add -b <branch> <path> origin/main
   ```

   Do not reuse or remove another task's worktree or branch. Make all changes,
   tests, and commits for the iteration in the new worktree.
2. For behavior changes, follow the project's TDD requirements and the
   [TDD skill](../tdd/SKILL.md): write and run the narrowest relevant failing
   test first, implement to Green, then refactor with targeted checks passing.
   A documentation-only change does not require fabricated behavior tests;
   use the repository's available documentation and diff checks instead.
3. Run the narrowest relevant checks and inspect the resulting diff. Record
   exact Red, Green, and refactor commands and results, plus unverified
   platforms or environment gaps, in the project's designated progress log
   when its protocol requires one.
4. Update the current-state status snapshot and append-only decision history
   only as required by the active project. Preserve runner-owned fields and do
   not create project status artifacts that its workflow does not use.
5. Complete the implementation commit and any required runner-managed status
   commit on the iteration branch before integration. Do not amend commits or
   use destructive Git operations.
6. Publish the iteration branch as needed and use the repository's remote
   merge process to integrate it into `origin/main`. An open pull request,
   pushed branch, or local merge is not completion. Fetch `origin` again and
   verify the resulting merge SHA is reachable from remote `main`. For squash
   or merge-queue flows, verify the merge result rather than requiring the
   iteration commit itself to remain an ancestor.
7. After the implementation content is merged and verified on fetched
   `origin/main`, perform a memory review using the
   [Project Memory skill](../project-memory/SKILL.md). Keep reusable lessons
   in the project's categorized memory store. If a memory change is warranted,
   make it on a fresh follow-up branch from the latest `origin/main`, integrate
   it through the same remote merge process, and verify its merge before
   completing the iteration. This is part of the same iteration, not a new
   iteration, and does not trigger another memory review. Never write directly
   to `main` or amend the merged implementation branch. If no durable lesson
   emerged, leave memory unchanged and record that outcome in the active
   progress or status record when one exists.
8. If validation, implementation merge, memory update, or remote verification
   is blocked, preserve the affected worktree and branch and report the
   blocker. Remove only this iteration's worktree and branch, and only after
   all required merges are verified and when the project's workflow permits
   cleanup.
9. Follow the active project's exact continuation, blocked, and completion
   markers, and emit them only when their conditions are met. Never report
   completion before the implementation merge and any required memory merge
   are verified on fetched remote `main`.

## Worker status and sign-off

When the first top-level run delegates work, the coordinator owns the overall
status snapshot and records every worker's individual iteration, sign-off,
and remote merge verification. Workers use fresh worktrees and branches,
refresh from `origin/main` before starting and before integration, and
rebase/retest if main moves. See the
[multi-agent orchestration](./references/multi-agent-orchestration.md) and
[multi-agent status](./references/multi-agent-status.md) references for the
split-plan, worker configuration, synchronization, and attestation contract.

Keep this outer development loop distinct from any in-product generation or
sampling loop. When the product has such a loop, follow its project-specific
requirements for user initiation, bounds, stoppability, isolation, and
confirmation before applying results.

## References

- [Test-Driven Development](../tdd/SKILL.md) for behavior-changing code work.
- [Multi-agent orchestration](./references/multi-agent-orchestration.md) for
  splitting a project into independent worker assignments.
- [Multi-agent status snapshots](./references/multi-agent-status.md) when a
  Ralph run delegates work to multiple agents.
- [Copilot agent selection and model controls](./references/copilot-cli-usage.md).
- The [SuperCollider AI Music Agent Ralph prompt](./references/ralph-loop.md)
  is specific to `dj_maxxed_beats`; its product requirements and file names do
  not apply to other projects.
