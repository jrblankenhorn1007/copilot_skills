---
name: tdd-ralph-loop
description: Use for test-first Ralph iterations isolated in a fresh Git worktree and branch, then merged and verified on remote main.
---

# TDD and Ralph Development Loop

Use this skill when a project is developed through repeated Ralph iterations.
Every iteration gets a fresh Git worktree and branch from the latest remote
`main`, and is not complete until its work is merged into and verified on
remote `main`. This skill coordinates test-first development with that
isolated outer loop.

The source guidance is retained in this skill's references; the Ralph prompt
is adapted to use isolated worktrees and merge each iteration:

- [Test-Driven Development](./references/tdd.md)
- [Ralph loop prompt](./references/ralph-loop.md)
- [Copilot agent selection and model controls](./references/copilot-cli-usage.md)

## Workflow

1. Inspect the active project's plan, prompt, progress notes, status snapshot,
   runner, and Git state. Treat the active project's documents as the source
   of truth. Fetch `origin` and identify the base worktree path (for example,
   with `git worktree list --porcelain`). For `dj_maxxed_beats`, the required
   target is `origin/main`. If the remote main ref is unavailable or its
   worktree has uncommitted changes, preserve everything and report the
   blocker before starting.
2. Create a fresh Git worktree and a unique branch from the latest remote main
   for this iteration. Follow the project's worktree location and branch
   naming conventions; otherwise use a unique sibling worktree and a branch
   such as `ralph/<task-slug>-<unique-id>`. Never reuse or remove a pre-existing
   worktree or branch. The standard form is
   `git worktree add -b <branch> <path> origin/main`. Do all iteration edits,
   tests, and commits in this worktree.
3. Choose one small, observable behavior. Write and run its narrowest test
   before changing production code. Confirm Red is caused by the missing or
   incorrect behavior, implement minimally to reach Green, then refactor while
   targeted tests remain green. Never claim an unrun test as evidence.
4. Record exact Red, Green, and refactor commands and results, along with
   remaining platform or environment coverage, in the active project's
   progress log.
5. Keep append-only decision history separate from the current-state status
   snapshot. Rewrite the snapshot each iteration and preserve fields owned by
   the runner. Complete all required implementation and runner-owned status
   commits on the iteration branch before integration.
6. After verification and required commits, publish the iteration branch as
   needed and use the repository's remote merge process (such as a required
   pull request or merge queue) to merge its work into `origin/main`. A local
   merge, pushed feature branch, or open pull request is not completion. Fetch
   `origin` again and verify that remote `main` contains the merged work before
   reporting completion or starting another iteration. For PR, squash, or
   merge-queue workflows, verify the resulting merge SHA is reachable from
   `origin/main`; the original branch commit need not be an ancestor after a
   squash merge. If merge, protection, or remote verification blocks this,
   preserve the worktree and branch and report the blocker. Clean up only this
   iteration's worktree and branch after the remote merge is verified and only
   when the project workflow permits it.
7. Keep an outer software-development loop distinct from any in-product
   generation or sampling loop. In-product loops must be user-started, bounded,
   stoppable, isolated from original project files, and require confirmation
   before applying a result when the active project requires it.
8. Follow the active runner's exact continuation, blocked, and completion
   markers. Do not use a runner that assumes an in-place branch workflow or
   skips the worktree/remote-merge lifecycle. Never report completion until
   every applicable acceptance criterion has evidence and the iteration's
   changes are verified on remote `main`.

## Scope of the copied references

The TDD reference includes test examples specific to `dj_maxxed_beats`; use
those examples only when relevant to that project. The Ralph reference also
contains the SuperCollider product requirements and repo-specific file names,
status fields, and stop markers. Those requirements apply only when working in
`dj_maxxed_beats`. For another project, use its own plan, status conventions,
acceptance criteria, and runner protocol while retaining the TDD and iteration
discipline above.

The references are based on files from `dj_maxxed_beats` and retain its
project-specific requirements, while adapting its Ralph workflow to the
worktree-per-iteration merge lifecycle above. The original files and runner in
`dj_maxxed_beats` are not changed by this skill. Check that a project's runner
supports the worktree lifecycle and verified remote-main merge before using it.
