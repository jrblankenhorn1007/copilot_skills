# Decisions — `agents/worktree-isolation-replay-final-sweep-20261007`

- **Run ID:** `copilot-skills-worktree-isolation-replay-final-sweep-20261007`
- **Task:** Replay PR #7's worktree-isolation change on the current fetched `origin/main`.
- **Branch:** `agents/worktree-isolation-replay-final-sweep-20261007`
- **Worktree:** `/Users/jrblankenhorn/copilot_skills.worktrees/worktree-isolation-replay-final-sweep-20261007`
- **Base `origin/main` SHA:** `0366e2aed573894f3a63e37d71b24d99cd382a7d`
- **Implementation commit:** `9c7b94e23a1e7791804041bfabf8e724fc9cae98`
- **PR:** Pending creation; the original PR #7 remains open and unchanged.
- **Merge:** `PENDING`.

## Agent and PR records

- [Coordinator status](../../ralph/agents-worktree-isolation-replay-final-sweep-20261007/agents/coordinator/status.md)
- [Coordinator progress](../../ralph/agents-worktree-isolation-replay-final-sweep-20261007/agents/coordinator/progress.md)
- [Coordinator pending PR record](agents/coordinator/pr-pending.md)

## Decision: replay on current main instead of changing stale PR #7

- **Context:** PR #7's base is `fb82e0d85ef80b26537c3fede01bcaefa422652d`, while fetched `origin/main` is `0366e2aed573894f3a63e37d71b24d99cd382a7d`. Its head is `7fd155ba0bd4814f85a890207bae71b4e13a7f8a`.
- **Decision:** Preserve PR #7 and its branch exactly as-is. Create a new branch from current main and cherry-pick its exact implementation commit; the replay succeeded without conflicts.
- **Rationale:** This avoids rewriting a published branch and preserves the old PR for audit while ensuring the replacement diff includes all changes already on current main.
- **Consequences:** The replacement PR must receive its own exact-SHA independent reviews. PR #7 is not mergeable as the integration path and remains open until the replacement is accepted or closed as superseded.

## Verification and open gates

- Contract: 31 tests; routing: 9; specialist contract: 5; main-ownership publisher: 15; main-ownership contract: 8; Resource Manager: 15; all passed on the replay commit.
- The original branch's recorded Red/Green evidence is retained at `docs/ralph/agents-worktree-collision-diagnosis-fix/agents/coordinator/progress.md`; no replay Red phase is claimed.
- Both Code and Security reviews remain required. The latest Resource Manager inventory (`2026-10-07T16:37:33Z`) had one available slot; dispatch them serially, refreshing and reserving before each.
- The status and progress records include the worktree identity evidence, exact source/base/implementation SHAs, and memory handoff.
