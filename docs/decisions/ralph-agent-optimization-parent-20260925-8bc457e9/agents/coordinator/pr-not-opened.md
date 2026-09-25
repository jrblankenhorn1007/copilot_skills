# Coordinator decision record - no PR opened yet

- **Run:** `copilot-skills-agent-routing-20260925-8bc457e9`
- **Tasks:** `specialist-agent-catalog`, `skill-aware-ralph-routing`,
  `agent-routing-integration`
- **Agent ID / runtime ID:** `coordinator` / `null`
- **Branch ref:** `refs/heads/ralph/agent-optimization-parent-20260925-8bc457e9`
- **Worktree:** `/Users/jrblankenhorn/copilot_skills.worktrees/ralph-agent-optimization-parent-20260925-8bc457e9`
- **Base `origin/main`:** `8da9310fda1b2e3042a379081dfb0675f1b22d6b`
- **Implementation commit:** `082f0d0dd543b516f875a232357390fcdadadffc` (local parent before final rebase)
- **PR:** `NOT_OPENED`; previous Ralph iterations used a verified no-PR
  fast-forward when repository policy allowed it. A PR will be used if
  repository policy requires one.

## Decisions

### Prefer a small role catalog over one wrapper per skill

- **Context:** The repository already has ten discoverable Agent Skills and
  one Ralph Loop custom agent. The request prioritizes speed, cost, and
  accuracy while allowing assignment of skill-specific expertise.
- **Alternatives:** Add a custom agent for every Skill, always run all Skills
  in one agent, or group related Skills into a few task-boundary specialists.
- **Decision:** Add focused Git, agent design, documentation, and ASI posture
  roles. Use skill descriptions for conditional selection; count only
  general implementation workers toward `workers=N`, but count every
  launched specialist toward shared Resource Manager host capacity.
- **Rationale:** On-demand Skill loading and narrow delegation avoid repeated
  context and unnecessary model calls without obscuring authority.
- **Consequences:** Routing must avoid duplicate investigations and preserve
  the parent/child Git lifecycle; validate representative routing and fallback
  cases, not hypothetical percentage speedups.

### Isolate the new iteration from unpublished local main commits

- **Context:** Canonical local `main` is clean but two commits ahead of
  `origin/main`; those commits belong to another recovery iteration.
- **Alternatives:** Change local `main`, include unrelated commits, or branch
  from the exact fetched `origin/main` SHA.
- **Decision:** Create an isolated parent from fetched `origin/main` and
  preserve the existing local commits unchanged.
- **Rationale:** This follows the Ralph parent/child protocol and avoids
  absorbing unrelated unpublished work.
- **Consequences:** Fetch and recheck the remote tip before integration;
  preserve the parent branch if permission or policy blocks the normal merge.

## Verification and unresolved blockers

- Baseline Ralph contract suite: **PASS**, 13 tests.
- After the remote advanced to `9dc821917a5ffe32517c44131c1211291d9b1014`,
  the parent split-plan commit was rebased before worker dispatch. The
  dashboard and decision index conflicted with the separate prompt recovery
  run; retaining both runs resolved the conflict. The existing Ralph contract
  suite then passed all 14 tests, and the new parent tip
  `2039e03b288b0b98e0b424b80b0e91ba65febf0e` contains the remote base.
- At baseline no blocker had been established. Remote write and merge
  permissions remain unverified until the actual publication/integration step.
- The coordinator, not a launched worker, implemented the two disjoint
  children after earlier host worker launches failed. Their signed-out
  commits are reachable from the parent through verified local merges
  `c37f00081b4cb3cbae565437bcd8c8da709a8c3e` and
  `082f0d0dd543b516f875a232357390fcdadadffc`;
  the combined 8-test specialist/routing contract passed. The separate
  role-hierarchy owner still claims shared entrypoint, README,
  dashboard, and Ralph contract paths. Preserve this parent and wait for
  that owner's published release before rebasing or wiring those files.
- Resource Manager capacity is shared by the router, Orchestrator, workers,
  reviewers, and specialists even though only implementation workers
  count toward `workers=N`. Read-only audit/design specialists must not
  receive `execute` merely to manage the registry: their caller must
  reserve and maintain verified host accounting, or block dispatch and
  use an authorized, capacity-admitted fallback. A `BLOCKED` task record
  with sign-out but no explicit scope release is not assumed to transfer
  another coordinator's shared paths. The blocked role-hierarchy owner
  subsequently confirmed the shared edit claim's release, and this run
  claimed those paths in task revision 2. Its separate role implementation
  remains unmerged: adapt the deployed Ralph coordinator now and preserve
  that branch for later rebase rather than silently integrating unfinished
  worker sign-off.

### Deploy routing in the current profile; leave the role branch isolated

- **Context:** The separate Orchestrator/Worker change is blocked and
  unmerged, but its owner released the overlapping edit scope. Both
  coordinator-owned specialist children are locally verified in the
  parent after rebase; the dashboard now indexes them.
- **Decision:** Add the four focused names to the existing Ralph Loop
  `agents:` allowlist and route bounded work conditionally there. Keep
  its Ralph Loop implementation worker and both independent reviewers.
  Treat the standalone Orchestrator/Worker profiles as a later, separately
  verified handoff, not as a shipped dependency of this change.
- **Verification:** Fifteen targeted contracts failed for the missing
  allowlist/current-role guidance and passed after wiring. The
  dashboard-index contract and twelve specialist/routing tests also passed.
  Full-suite checks, final rebase, remote-main merge, and memory review
  remain pending. Use the short `MERGE` reservation and normal repository
  process for remote integration, then release main promptly.

Subsequent pre-rebase validation passed all 55 Ralph and 15 Resource Manager
tests, plus both original-to-rebased child owned-file tree comparisons. The
tested routing change is committed at
`2d7db54f144449d5ee938c1a8de614a50c8201e8`; fetched
`origin/main` advanced to `55c30b3eb3c8e1cdf735ff4b987c9235bf5456e6`
with only other tasks' status transactions. This run must rebase and retest
before a main reservation; the separate role branch remains unmerged.
