---
name: ralph-loop
description: Use for one focused Ralph-style development iteration in a fresh worktree and branch, then verify its merge to remote main.
---

# Ralph Loop

Use this skill to run one bounded outer software-development iteration. It
guides project discovery, worktree isolation, verification, and integration.
It does not replace the active project's plan, acceptance criteria, runner,
tests, status protocol, or decision history; read and follow those sources.

## Required setup

1. Read the active project's implementation plan, Ralph prompt or runner,
   progress log, current status snapshot, decision log, and applicable local
   instructions. Treat those artifacts as the source of truth for scope,
   filenames, runner behavior, and completion markers.
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
7. If validation, merge, or remote verification is blocked, preserve the
   iteration worktree and branch and report the blocker. Remove only this
   iteration's worktree and branch, and only after a verified merge and when
   the project's workflow permits cleanup.
8. Follow the active project's exact continuation, blocked, and completion
   markers, and emit them only when their conditions are met. Never report
   completion before the changes are verified on fetched remote `main`.

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
