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

The parent was then rebased with merge topology retained onto fetched main
`70b98bbf0ab35620f7c33b5d9789187560c699df`, preserving the prior
tip at `424ad90d079fcdba82222dc530ec99926b547450`. The rewritten
deployed-routing implementation is
`d0b35a12d425f016a5a9d918bc0bece0ba16896f`; child merges are
`491772f476bdade69bb332600fd27e86d6f997bf` and
`691d5b4dbb18a87768294326fc924f28b1490249`, with ancestor and
owned-content checks passing. The separate role coordinator resumed
in status revision 3 and explicitly narrowed its editing scope around
this run's shared files; it has not merged those new roles. Await the
post-rebase contracts, normal main integration, and memory review.

Post-rebase verification passed all 55 Ralph and 15 Resource Manager
tests, with clean whitespace and exact owned-file/ancestry proofs for both
children. This parent uses the repository's established no-PR fast-forward
path, so independent PR review is `NOT_APPLICABLE`, not silently skipped.
Remote-main verification and post-merge memory review remain pending.

### Verified reserved main merge and post-merge lesson

The branch owner reserved `MERGE` on remote main at
`7a8f0253393b4e81053009b68afda1a42c38bcbb`, joined the sign-in
commit into the isolated parent, and used an authorized non-force
fast-forward. The result `0b7db073e365e6c1c6e29d410c424d7c7637c9bf`
was fetched and verified on remote main; reservation release
`5b7f729d8f48c90c5f2e1f5a7ef6ab29217db76c` was verified with
main `FREE`. The child tips and the complete deployed pipeline tree
remain reachable and unchanged on later fetched main
`86fde358a421f64f4c979b24d0127e6797470bf9`.

The post-merge Project Memory review found a transferable ancestry
invariant missing from the main-ownership protocol: the reservation
sign-in advances remote main even when nobody checks out `main`. A
parent prepared beforehand cannot fast-forward without incorporating
that sign-in commit. A test-first fresh-branch follow-up records the
invariant in the protocol, publisher guide, orchestration reference,
and workflow memory; its 8 targeted checks pass. Preserve task
`IN_PROGRESS` until that follow-up and final status synchronization
are independently verified on fetched main.

### Completion after the verified memory follow-up

The protocol and workflow-memory follow-up was rebased, passed 10
targeted tests, and used a second authorized no-PR fast-forward.
Commit `74f3efe14e4ee3bd9638969ad5b222978ae942c5` was verified
on fetched remote main; the `MERGE` reservation was released at
`aebecf7ace8a778dd50017bc975d021a62c0017c`. On that fetched
tip the full Ralph suite passed **56** tests and Resource Manager
passed **15**. This run can transition to `COMPLETE` after the
coordinator's synchronized status-only follow-up is fetched and
verified; publish task-scope sign-outs separately afterward.
