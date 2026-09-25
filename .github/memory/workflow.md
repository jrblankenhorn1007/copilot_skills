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

## Verify Git access in stages

- **Rule:** Check configured commit identity and remote read, branch-push, and
  merge access separately; a successful `git fetch` proves read access only.
  Use the approved credential provider and keep credentials out of agent
  prompts, URLs, command output, and files.
- **Why:** Local identity, remote read access, and write/integration
  authorization are distinct, so validating them separately makes failures
  diagnosable without unsafe credential handling.
- **Scope:** Follow the [Ralph Loop Git identity and authentication
  preflight](../skills/ralph-loop/SKILL.md#git-identity-and-authentication).
