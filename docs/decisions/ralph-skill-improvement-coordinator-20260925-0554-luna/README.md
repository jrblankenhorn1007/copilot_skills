# Decisions — `ralph/skill-improvement-coordinator-20260925-0554-luna`

- **Run:** `skills-improvement-20260925-0554-luna`
- **Coordinator task:** `skill-improvement-workflow-readme`
- **Workers:** `worker-01` Agentic Eval; `worker-02` Agent Skill Stack.
- **Parent base `origin/main`:**
  `e9fe3d175d1ca76b03fccdbe53431205b80e5c23`
- **Parent implementation commit:** pending.
- **Parent PR:** expected; see [coordinator PR-pending record](agents/coordinator/pr-pending.md).

## Decisions

1. The prior Agentic Eval, Agent Skill Stack, and coordinator changes are
   unmerged and were authored under an unknown model profile. They are
   read-only reference data: workers may inspect and selectively port worthy
   ideas, but must not claim those commits used the requested profile, modify
   the old branches, or treat them as already integrated.
2. Keep the worker scopes disjoint: worker-01 owns
   `.github/skills/agentic-eval/**`; worker-02 owns
   `.github/skills/agent-skill-stack/**`; the coordinator owns `README.md`,
   `docs/ralph-status.md`, and the parent coordinator's status/progress/
   decision records.
3. Use the latest repository Ralph parent/child lifecycle: both child branches
   start at the exact parent tip; the coordinator integrates them serially
   after reviewing their scoped checks and commit-bound self-attestations.
4. Explicitly configure both new workers as `gpt-6-luna`, reasoning effort
   `max`, context tier `default`. Do not rely on inheritance or infer a
   profile for prior work.
5. The parent will use the repository's remote PR integration path; direct
   pushes to `main`, force-pushes, and branch-protection bypasses are out of
   scope.

## Coordinator record

- [Coordinator PR-pending record](agents/coordinator/pr-pending.md)
- [Coordinator status](../../ralph/ralph-skill-improvement-coordinator-20260925-0554-luna/agents/coordinator/status.md)
- [Coordinator progress](../../ralph/ralph-skill-improvement-coordinator-20260925-0554-luna/agents/coordinator/progress.md)
