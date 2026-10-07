# Coordinator Decision Record — No PR Opened

- **Run ID:** `copilot_skills-worktree-collision-20260924`
- **Task IDs:** `worktree-session-binding-check`, `worktree-identity-protocol`
- **Coordinator:** `coordinator` — worktree collision diagnosis.
- **Branch ref:** `refs/heads/agents/worktree-collision-diagnosis-fix`
- **Worktree:** `/Users/jrblankenhorn/copilot_skills.worktrees/worktree-collision-diagnosis-fix`
- **Base `origin/main` SHA:** `8da9310fda1b2e3042a379081dfb0675f1b22d6b`
- **Implementation commit SHA:** pending.
- **PR:** `NOT_OPENED`; the repository's recorded no-PR process is a
  verified fast-forward to `origin/main`.
- **Status:** `IN_PROGRESS`.

## Decisions

### Fail closed on host/session worktree mismatch

- **Context:** A worker session received an explicit child path, branch, and
  base SHA but was launched in the original task worktree. It stopped before
  edits. A separate session-creation attempt generated a different worktree
  from the default branch instead of using the requested parent.
- **Alternatives:** Trust the path in the prompt, let agents switch branches
  themselves, or require host binding and verify the actual session before
  editing.
- **Decision:** Require the host to bind each agent to its assigned absolute
  worktree and require path/root/branch/base/clean/registry checks before
  edits. If binding is unavailable, do not dispatch in parallel; use a
  verified sequential session only when project policy permits.
- **Rationale:** Git registered no duplicate paths or attached branches;
  the demonstrated mismatch was between the expected child and actual agent
  session context.
- **Consequences:** Workers report `BLOCKED` with no edits on mismatch. Do not
  change directory or check out another branch and continue with an editor
  still bound elsewhere.

### Use unique run and dispatch identities

- **Context:** The existing two-worker fixture used paths named only by
  `worker-id` and branches named only by worker ID. That does not model two
  concurrent runs or retries.
- **Alternatives:** Keep worker-ID-only paths and rely on Git errors, or
  include run and dispatch IDs and preflight every candidate.
- **Decision:** Require unique run and dispatch IDs plus the stable worker ID
  in worktree and branch names; check local refs, remote refs, and registered
  worktrees before creating them.
- **Rationale:** The identifiers distinguish concurrent runs and retries
  before a session is launched, rather than relying on a collision error
  after allocation.
- **Consequences:** Retries use fresh paths/branches and remain attributable
  in status records.

## Verification and recovered issues

- The initial root `main` `git pull --ff-only` failed because the clean local
  branch had 8 local-only commits and lagged `origin/main`; the commits were
  preserved. The task worktree was fast-forwarded from
  `9558f99cc34cbed8dd1d24f4f15fc03f5d78b6ea` to
  `8da9310fda1b2e3042a379081dfb0675f1b22d6b`.
- A temporary-Git test initially compared a `/var` path to Git's canonical
  `/private/var` worktree path. The check now resolves the path; the focused
  tests pass.
- Contract Red/Green, full-suite result, and final remote verification will
  be recorded here before integration.

## Unresolved blockers

- None currently. Full-suite validation, remote integration, and the required
  post-merge memory review remain pending.
