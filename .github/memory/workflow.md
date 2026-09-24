# Workflow

## Keep post-merge follow-ups reviewable

- **Rule:** Deliver work discovered after a change has merged as a new,
  reviewable change based on the current main branch; do not write directly to
  main or amend an already integrated branch.
- **Why:** The merged branch is no longer an integration path, and follow-up
  work still needs the repository's normal checks and merge verification.
- **Gotcha:** A lesson found during post-merge review cannot be added to a
  change that has already merged.

## Preserve published branch history during synchronization

- **Rule:** Keep published branch history immutable; when its base advances,
  replay only outstanding changes on a fresh branch from the latest `main`.
- **Why:** Rewriting a published ref can invalidate coordination and requires
  a force-push; a fresh branch preserves reviewable history.
- **Scope:** Follow the [Ralph synchronization
  workflow](../skills/ralph-loop/references/multi-agent-orchestration.md).
- **Gotcha:** Do not rebase and force-push a published iteration branch when
  `main` advances.
