# Ralph Branch Decision Index

- **Run ID:** `copilot_skills-worktree-collision-20260924`
- **Task IDs:** `worktree-session-binding-check`, `worktree-identity-protocol`
- **Branch ref:** `refs/heads/agents/worktree-collision-diagnosis-fix`
- **Branch slug:** `agents-worktree-collision-diagnosis-fix`
- **Base `origin/main` SHA:** `8da9310fda1b2e3042a379081dfb0675f1b22d6b`
- **Worktree:** `/Users/jrblankenhorn/copilot_skills.worktrees/worktree-collision-diagnosis-fix`
- **Coordinator:** `coordinator` — worktree collision diagnosis.
- **Pull request:** `NOT_OPENED`; the repository's recorded process is a
  verified fast-forward to `origin/main`.
- **Integration:** `PENDING`.

## Agent records

- [Coordinator no-PR and integration record](agents/coordinator/pr-not-opened.md)
- [Coordinator status](../../ralph/agents-worktree-collision-diagnosis-fix/agents/coordinator/status.md)
- [Coordinator progress](../../ralph/agents-worktree-collision-diagnosis-fix/agents/coordinator/progress.md)

## Diagnosis and decisions

- Git worktree registration showed no duplicate paths or attached branches.
  It did show 83 worktrees and one detached worktree at the latest scan.
- The host started worker-01 in the coordinator's default task worktree,
  despite a different child path/branch/base in the prompt. The worker stopped
  before edits. A second session-creation attempt also selected an
  auto-generated worktree rather than the requested parent. These are
  reproducible host/session binding failures, not evidence of duplicate Git
  registrations.
- Preserve the diverged root `main`; do not reset or rebase its local-only
  commits. The implementation uses the verified platform-assigned task
  worktree fast-forwarded to current `origin/main`.
- Define collision-resistant `run-id`/`dispatch-id`/`worker-id` path and
  branch identities, preflight local/remote refs and worktree paths, bind
  host sessions explicitly, and stop before edits on any mismatch. If the
  host cannot bind worker worktrees, do not dispatch in parallel.
- The worktree contract and regression tests are one cohesive assignment.
  Only one worker was attempted; the coordinator proceeds sequentially.

## Integration

- Implementation commit: `PENDING`.
- Remote-main integration: `PENDING`.
- Post-merge memory review: `PENDING`.
