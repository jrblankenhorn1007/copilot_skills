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
