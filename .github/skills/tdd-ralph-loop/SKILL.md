---
name: tdd-ralph-loop
description: Use for test-first Ralph iterations isolated in a fresh Git worktree and branch, then merged into the base branch.
---

# TDD and Ralph Development Loop

Use this skill when a project is developed through repeated Ralph iterations.
Every iteration gets a fresh Git worktree and branch, and is merged into its
base branch after verification. This skill coordinates test-first development
with that isolated outer loop.

The source guidance is retained in this skill's references; the Ralph prompt
is adapted to use isolated worktrees and merge each iteration:

- [Test-Driven Development](./references/tdd.md)
- [Ralph loop prompt](./references/ralph-loop.md)

## Workflow

1. Inspect the active project's plan, prompt, progress notes, status snapshot,
   runner, and Git state. Treat the active project's documents as the source
   of truth. Identify its integration/base branch and worktree path (for
   example, with `git worktree list --porcelain`); if either is unclear or the
   base checkout has uncommitted changes, preserve everything and resolve the
   blocker before starting.
2. Create a fresh Git worktree and a unique branch from the base branch for
   this iteration. Follow the project's worktree location and branch-naming
   conventions; otherwise use a unique sibling worktree and a branch such as
   `ralph/<task-slug>-<unique-id>`. Never reuse or remove a pre-existing
   worktree or branch. The standard form is
   `git worktree add -b <branch> <path> <base-branch>`. Do all iteration edits,
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
6. After verification and required commits, merge the iteration branch into
   its base branch as the final integration step. Verify the merge succeeded.
   If the base is dirty, a conflict occurs, or the merge otherwise fails,
   preserve the worktree and branch and report the blocker; do not claim the
   iteration is complete. Clean up only this iteration's worktree and branch
   after a verified merge and only when the project workflow permits it.
7. Keep an outer software-development loop distinct from any in-product
   generation or sampling loop. In-product loops must be user-started, bounded,
   stoppable, isolated from original project files, and require confirmation
   before applying a result when the active project requires it.
8. Follow the active runner's exact continuation, blocked, and completion
   markers. Do not use a runner that assumes an in-place branch workflow or
   skips the worktree/merge lifecycle. Never report completion until every
   applicable acceptance criterion has evidence and the iteration branch is
   merged.

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
supports this lifecycle before using it.
