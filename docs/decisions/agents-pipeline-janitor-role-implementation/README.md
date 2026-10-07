# Ralph Branch Decision Index

- **Run ID:** `copilot-skills-worktree-janitor-20261007`
- **Task ID:** `pipeline-worktree-janitor-role`
- **Branch ref:** `refs/heads/agents/pipeline-janitor-role-implementation`
- **Branch slug:** `agents-pipeline-janitor-role-implementation`
- **Starting `origin/main` SHA:** `fb82e0d85ef80b26537c3fede01bcaefa422652d`
- **Coordinator:** `coordinator` - worktree janitor role implementation.
- **Implementation commit:** `968fc69e0b215b508cbe7cbb3e428ece42d68b0d`
  (rebased onto `65ada24c7ff117ea82a6ce92ac718953b2d8222f`).
- **Integration record:** [Coordinator no-PR record](agents/coordinator/pr-not-opened.md)
- **Status:** `BLOCKED`; [coordinator status](../../ralph/agents-pipeline-janitor-role-implementation/agents/coordinator/status.md)
- **Progress:** [Coordinator progress](../../ralph/agents-pipeline-janitor-role-implementation/agents/coordinator/progress.md)

## Decisions

### Gate worker cleanup on coordinator-verified integration

- **Context:** The pipeline already required verified child-to-parent merges
  before cleanup, but had no explicit state to queue worker worktrees for a
  dedicated cleanup role.
- **Alternatives:** Let workers declare their own worktrees ready, have the
  coordinator remove them directly, or use a coordinator-owned READY gate and
  a constrained Janitor.
- **Decision:** The coordinator alone sets `cleanup.worktree: READY` after
  verifying the exact child-to-parent merge, worker sign-out, no active
  session owner, and a clean worker worktree. The Janitor rechecks these
  facts before removing the exact worker child worktree.
- **Rationale:** Readiness depends on parent integration and host session
  ownership, which the worker cannot independently establish. An explicit
  gate makes cleanup resumable when agent capacity is unavailable.
- **Consequences:** A missing or inconsistent gate leaves the worktree intact
  and cleanup blocked/queued; the coordinator records `REMOVED` or `BLOCKED`
  from the Janitor's report.

### Limit Janitor authority to worker worktrees

- **Context:** The requested outcome is reducing worker-created worktrees,
  not deleting parent workspaces or branch history.
- **Alternatives:** Have the Janitor also delete local branches, remote refs,
  or coordinator parent worktrees.
- **Decision:** The Janitor removes only the exact worker child worktree,
  without force. Local branch cleanup remains a separate coordinator action;
  the Janitor never deletes local/remote branches or refs and never edits
  status records.
- **Rationale:** Narrow Git authority minimizes data loss and preserves the
  existing branch and status ownership contracts.
- **Consequences:** Unmarked, dirty, active, unmerged, parent, and main
  worktrees remain untouched; branch cleanup remains governed by existing
  merge and repository-policy checks.

### Serialize because the host had no available agent slots

- **Context:** The live Resource Manager reported zero available slots.
- **Decision:** Dispatch no workers or specialists; the coordinator completed
  the implementation serially. Runtime routing of the Janitor was not
  exercised.
- **Consequences:** Agentic evaluation records static text outcomes as
  `PASS` where supported and runtime routing as `UNKNOWN`.

### Preserve the dashboard edit scope

- **Context:** The full dashboard-index contract test reports that this
  coordinator leaf is not indexed, while a separate active run owns
  `docs/ralph-status.md`.
- **Decision:** Do not edit the shared dashboard until its current owner
  records sign-out or releases the path. Keep the run blocked and preserve its
  worktree meanwhile.
- **Rationale:** The aggregate dashboard has one coordinator owner; the task
  ledger is the authority for edit-scope conflicts.
- **Consequences:** Final dashboard synchronization, implementation
  integration, and the required post-merge memory review remain pending. The
  full multi-agent suite passes with a narrow exception for only this
  `BLOCKED` coordinator leaf while its exact pending shared scope is recorded;
  the aggregate dashboard is still incomplete and cannot be synchronized yet.
