# Decisions — `ralph/skill-improvement-coordinator-20260925-0554-luna`

- **Run:** `skills-improvement-20260925-0554-luna`
- **Coordinator task:** `skill-improvement-workflow-readme`
- **Workers:** `worker-01` Agentic Eval; `worker-02` Agent Skill Stack.
- **Parent base `origin/main`:**
  `e9fe3d175d1ca76b03fccdbe53431205b80e5c23`
- **First parent rebase onto `origin/main`:**
  `20293c720b18a1a21ff150f566823493b7a2717d`
- **First rebase tip:**
  `d7b0d02ede3666825e6b4fb64fe6f3dd641bb87f`
- **Previous parent rebase:** `36bf3fad31b2965dc6a0516a20ec9b2e6ac64355`;
  tip `c833b2d19c7bfa3a643ec6e2e7efd0dac467afa3`.
- **Latest parent rebase onto `origin/main`:**
  `7ee1307cb47f5a88cd6b46ee135444777ddeb665`.
- **Parent tip after latest rebase:** `9c94704bb0e999e497f4b9eeb0cf9c253b57b351`.
- **Coordinator README implementation commit after latest rebase:**
  `5e880f96087faa144803d865e56ee45fa40257a0`.
- **Final parent implementation commit:** pending worker integration.
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
6. The README will describe a small evidence-based handoff across existing
   skills rather than recommend that every task use the full skill stack.
   Documentation-only work uses link/doc checks, while executable behavior
   changes use the repository's TDD process.

## Coordinator record

- [Coordinator PR-pending record](agents/coordinator/pr-pending.md)
- [Coordinator status](../../ralph/ralph-skill-improvement-coordinator-20260925-0554-luna/agents/coordinator/status.md)
- [Coordinator progress](../../ralph/ralph-skill-improvement-coordinator-20260925-0554-luna/agents/coordinator/progress.md)

## Recovered issues

- `origin/main` advanced after the initial parent and child branches were
  created. The initial parent rebase stopped on a dashboard content conflict.
  The coordinator preserved the fetched remote dashboard, reapplied only this
  run's metadata, completed the rebase, and verified the refreshed main SHA
  is an ancestor of the parent.
- The first worker-02 dispatch returned no changes, checks, leaf records,
  commit, or sign-off. Its clean attempt branch/worktree remains preserved;
  the resolution is a fresh child branch from the refreshed parent with the
  same explicitly configured `gpt-6-luna` / `max` / `default` profile.
- After the workers signed off, `origin/main` advanced to
  `36bf3fad31b2965dc6a0516a20ec9b2e6ac64355`. The parent was rebased and
  three dashboard conflicts were resolved by preserving the full refreshed
  main dashboard. No assigned skill path changed upstream. Both unpublished
  child branches now need rebase/retest and renewed commit-bound sign-off
  before integration; their old reports are preserved as historical evidence.
- A subsequent refresh advanced `origin/main` to
  `d868d684564658bdc9488e27f5bfeaa592b04338`. The parent rebase completed
  cleanly; only unrelated status-sync commits were added upstream. The exact
  refreshed main state is preserved.
- A further canonical refresh advanced `origin/main` to
  `7ee1307cb47f5a88cd6b46ee135444777ddeb665`. The README workflow and both
  target skill changes remain absent from remote main; since d868, only the
  aggregate dashboard changed upstream. Rebase conflicts were limited to
  `docs/ralph-status.md`; the exact latest upstream dashboard was preserved
  during both conflicts. The rebased parent tip is
  `9c94704bb0e999e497f4b9eeb0cf9c253b57b351`, and the README implementation
  commit is now `5e880f96087faa144803d865e56ee45fa40257a0`.
- Preserve the previously signed-off child branches as historical evidence.
  Their base and sign-offs are stale; fresh child branches from the updated
  parent are required, and any ported changes need new checks and exact-SHA
  self-attestations under the explicitly requested profile.
- The read-only Docs Sync Audit script reported 36 repository-wide leads.
  The README contract-test path it flagged was confirmed to exist; Agent
  Skill Stack missing-script leads are assigned for worker-02 review, and
  unrelated historical status-document leads were left untouched. The run
  is not described as a clean full-repository audit.
