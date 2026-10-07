# Decisions — `agents/worktree-isolation-replay-final-sweep-20261007`

- **Run ID:** `copilot-skills-worktree-isolation-replay-final-sweep-20261007`
- **Task:** Replay PR #7's worktree-isolation change on the current fetched `origin/main`.
- **Branch:** `agents/worktree-isolation-replay-final-sweep-20261007`
- **Worktree:** `/Users/jrblankenhorn/copilot_skills.worktrees/worktree-isolation-replay-final-sweep-20261007`
- **Base `origin/main` SHA:** `0366e2aed573894f3a63e37d71b24d99cd382a7d`
- **Current rebased `origin/main` SHA:** `e6ed4c20c5955af91c628b34f026b6eb63c09c70`
- **Implementation commit:** `9be82bda3ec6b4d2d3e42157df3a3a30c93e5f53`
- **PR:** Pending creation; the original PR #7 remains open and unchanged.
- **Merge:** `PENDING`.

## Agent and PR records

- [Coordinator status](../../ralph/agents-worktree-isolation-replay-final-sweep-20261007/agents/coordinator/status.md)
- [Coordinator progress](../../ralph/agents-worktree-isolation-replay-final-sweep-20261007/agents/coordinator/progress.md)
- [Coordinator pending PR record](agents/coordinator/pr-pending.md)

## Decision: replay on current main instead of changing stale PR #7

- **Context:** PR #7's base is `fb82e0d85ef80b26537c3fede01bcaefa422652d`, while the latest fetched `origin/main` is `e6ed4c20c5955af91c628b34f026b6eb63c09c70`. Its head is `7fd155ba0bd4814f85a890207bae71b4e13a7f8a`.
- **Decision:** Preserve PR #7 and its branch exactly as-is. Create a new branch from current main and cherry-pick its exact implementation commit; the replay succeeded without conflicts.
- **Rationale:** This avoids rewriting a published branch and preserves the old PR for audit while ensuring the replacement diff includes all changes already on current main.
- **Consequences:** The replacement PR must receive its own exact-SHA independent reviews. PR #7 is not mergeable as the integration path and remains open until the replacement is accepted or closed as superseded.
- Before publication, origin/main advanced by janitor status-only commits. The private replay branch was rebased onto `e6ed4c20c5955af91c628b34f026b6eb63c09c70` without conflicts; the rewritten implementation commit was retested.

## Verification and open gates

- Contract: 31 tests passed after rebase; routing: 9; specialist contract: 5; main-ownership publisher: 15; main-ownership contract: 8; Resource Manager: 15.
- The original branch's recorded Red/Green evidence is retained at `docs/ralph/agents-worktree-collision-diagnosis-fix/agents/coordinator/progress.md`; no replay Red phase is claimed.
- Both Code and Security reviews remain required. The latest Resource Manager inventory (`2026-10-07T16:37:33Z`) had one available slot; dispatch them serially, refreshing and reserving before each.
- The status and progress records include the worktree identity evidence, exact source/base/implementation SHAs, and memory handoff.
- `git diff origin/main...HEAD --check` and the staged status-record check passed.
