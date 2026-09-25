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
- **Previous parent rebase onto `origin/main`:**
  `7ee1307cb47f5a88cd6b46ee135444777ddeb665`.
- **Previous parent rebase onto `origin/main`:**
  `2b0e3b002d9596eea6773ad7a1a33654613d0008`.
- **Latest parent rebase onto `origin/main`:**
  `4f5fee342c7e08ce556ae10c8a693f9e30a2ee2b`.
- **Parent tip after latest rebase:** `6578ae99a01a35528363d5a228927469765da855`.
- **Coordinator README implementation commit after latest rebase:**
  `2d6b04af1b89f969deec057a0f5b5b6dd42167c9`.
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
- [Verified worker-01 replay](../ralph-skill-eval-worker-01-replay-20260925-1234-luna/README.md)
- [Verified worker-02 replay](../ralph-skill-stack-worker-02-replay-20260925-1254-luna/README.md)

Worker-01's Agentic Eval implementation is byte-identical to its separately
signed-off Luna source commit. Its fresh child implementation is
`110028610887e4d879a0129fcb81f417faf51eef`, and the no-PR child merge
`478f97845fba19f3f3b3ac87d7a01d294ae331db` is verified on the parent.
The replay was carried out serially by the existing runtime; that runtime's
current model profile is not reported.

Worker-02's Agent Skill Stack four-file replay is byte-identical to Luna
source `1b9cfde1a44b6176fce261b35d69a790612f3d69`. Its fresh
implementation `a9d48f751e5f4932b4e1e3a554f29a996ad71980` and no-PR
child merge `45fbd82b1bdd2112d3e720221567aac118892775` are verified
on the parent. This existing runtime's model profile remains unreported;
its worker memory handoff is preserved for post-parent-merge review.

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
- The current Ralph guidance permits fetch-only instruction refresh without
  modifying the shared local `main` checkout. The unpublished parent rebased
  cleanly onto `2b0e3b0` after the coordinator's verified agent-sync sign-in.
  Current upstream had omitted this run from the aggregate dashboard; only
  this run's coordinator entry was reapplied. The initially failing Ralph
  contract check now passes all 20 tests; 74 focused local Markdown links
  resolve. The Resource Manager presently permits no new worker or
  independent reviewer agents, so both child integrations remain pending
  their renewed sign-offs and the parent PR remains unopened.
- A second fetch-only refresh rebased the parent onto `4f5fee3`. One
  dashboard conflict was resolved by combining the newer upstream overview
  and revision with this run's entry, preserving all 10 upstream runs and 22
  agent rows. The rewritten README retains upstream specialist documentation.
  Targeted validation then passed 20 Ralph contract tests, YAML synchronization
  for 11 runs/23 rows, 85 focused links, and ancestry/whitespace checks. The
  host limit rose to two agents, but both are active; apparent capacity was
  not treated as permission to dispatch a worker.
- The read-only Docs Sync Audit script reported 36 repository-wide leads.
  The README contract-test path it flagged was confirmed to exist; Agent
  Skill Stack missing-script leads are assigned for worker-02 review, and
  unrelated historical status-document leads were left untouched. The run
  is not described as a clean full-repository audit.
