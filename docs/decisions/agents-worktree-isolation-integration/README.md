# Decisions — `agents/worktree-isolation-integration`

- **Branch:** `agents/worktree-isolation-integration`
- **Worktree:**
  `/Users/jrblankenhorn/copilot_skills.worktrees/worktree-isolation-integration`
- **Role:** coordinator (single-agent iteration; no child workers dispatched)
- **Supersedes/completes:** the original, never-merged
  [`agents/worktree-collision-diagnosis-fix`](../agents-worktree-collision-diagnosis-fix/README.md)
  branch from archived session `aaaf8789` ("Worktree confusion and collision
  fix"). That branch is preserved, unmerged, per the repository's "never
  delete an unmerged branch" rule.

## Agent/PR records

- [`coordinator` / PR #7](agents/coordinator/pr-7.md) — original PR, retained
  unchanged but blocked because its base is stale; the implementation is
  replayed for review on a fresh current-main branch.
- [Current-main replacement run](../agents-worktree-isolation-replay-final-sweep-20261007/README.md)
