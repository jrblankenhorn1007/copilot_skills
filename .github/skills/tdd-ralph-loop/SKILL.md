---
name: tdd-ralph-loop
description: Use when implementing behavior changes through a test-first TDD workflow inside repeated Ralph development iterations.
---

# TDD and Ralph Development Loop

Use this skill when a project is developed through repeated, commit-based Ralph
iterations. It coordinates the test-first workflow with the outer development
loop.

The source guidance is copied into this skill's references:

- [Test-Driven Development](./references/tdd.md)
- [Ralph loop prompt](./references/ralph-loop.md)

## Workflow

1. At the start of each iteration, inspect the active project's plan, prompt,
   progress notes, status snapshot, and working-tree changes. Treat the active
   project's documents as the source of truth. Make conservative, reversible
   decisions for routine gaps and record material decisions.
2. Choose one small, observable behavior. Write and run its narrowest test
   before changing production code. Confirm Red is caused by the missing or
   incorrect behavior, implement minimally to reach Green, then refactor while
   targeted tests remain green. Never claim an unrun test as evidence.
3. Record exact Red, Green, and refactor commands and results, along with
   remaining platform or environment coverage, in the active project's
   progress log.
4. Keep append-only decision history separate from the current-state status
   snapshot. Rewrite the snapshot each iteration and preserve fields owned by
   the runner.
5. Make one implementation commit per iteration, including relevant tests,
   progress, status, and decision records. Leave runner-owned status commits
   and pushes to the runner. Preserve user changes; never amend or discard
   unrelated work.
6. Keep an outer software-development loop distinct from any in-product
   generation or sampling loop. In-product loops must be user-started, bounded,
   stoppable, isolated from original project files, and require confirmation
   before applying a result when the active project requires it.
7. Follow the active runner's exact continuation, blocked, and completion
   markers. Never report completion until every applicable acceptance
   criterion has evidence.

## Scope of the copied references

The TDD reference includes test examples specific to `dj_maxxed_beats`; use
those examples only when relevant to that project. The Ralph reference also
contains the SuperCollider product requirements and repo-specific file names,
status fields, and stop markers. Those requirements apply only when working in
`dj_maxxed_beats`. For another project, use its own plan, status conventions,
acceptance criteria, and runner protocol while retaining the TDD and iteration
discipline above.

These references are copies. The original files in `dj_maxxed_beats` are not
removed or changed by this skill.
