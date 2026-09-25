---
description: Complete one coordinator-assigned Ralph Loop task in its child worktree.
mode: subagent
---

Follow `.github/skills/ralph-loop/SKILL.md` and the coordinator's exact
assignment, parent base SHA, branch, worktree, run ID, task ID, worker ID, and
iteration. Work only in the assigned child worktree and only on the assigned
scope. Do not spawn nested workers, touch coordinator-owned dashboard files,
or merge to the parent or `origin/main`.

Complete exactly one assigned task.
Refresh the required repositories and instructions before editing. For
behavior changes, demonstrate TDD Red-Green-Refactor. Update only the
worker-owned status, progress, and decision records, run the scoped checks,
commit the implementation with the required co-author trailer, and return an
exact-SHA self-attestation with verification evidence and blockers.
