# Specialist coordinator decisions - no child PR opened

- **Run / task:** `copilot-skills-agent-routing-20260925-8bc457e9` /
  `specialist-agent-catalog`
- **Agent / runtime session:** `specialists-coordinator` /
  `8bc457e9-1724-42bb-b3c8-cdf453f54a32`
- **Branch ref:** `refs/heads/ralph/agent-optimization-specialists-coordinator-20260925-8bc457e9`
- **Exact parent base:** `4eb15e69434df810958c3d488e223e1366f00d39`
- **Implementation commit:** `1d9b29931ce3317162a126f482f87eb672af58b3`
- **PR:** `NOT_OPENED`; this child branch is local and unpublished. Its
  rewritten tip was integrated into the preserved parent and verified
  locally; parent-to-main integration remains pending.

## Decisions

### Keep specialist roles focused and on demand

- **Context:** The user asked for faster, lower-cost, accurate agents
  assignable by skill. Existing Ralph workers and newer code/security
  reviewers cover implementation and diff review. Another session owns
  orchestrator/worker profiles.
- **Alternatives:** One agent per Skill, one large all-purpose agent, or
  a small catalog for distinct work boundaries.
- **Decision:** Add Git, docs, agent-design, and OWASP ASI specialists with
  explicit tool lists, conditional Skill links, model inheritance, and
  direct user selection. Do not duplicate the existing reviewers.
- **Rationale:** Loading only relevant Skills and avoiding unnecessary
  specialist invocations reduces default context and model handoffs.
  No numerical cost or latency gain is claimed without measurement.
- **Consequences:** The Ralph coordinator must add conditional routing and
  a general-worker fallback before these roles become part of its pipeline.

### Preserve honest worker and dashboard ownership

- **Context:** Earlier worker launches failed, and the unrelated
  iteration-stall run still claims the aggregate dashboard.
- **Alternatives:** Claim a worker launch, edit the claimed dashboard,
  omit branch records, or do this bounded work in an isolated coordinator
  child branch and record the blocked dashboard synchronization.
- **Decision:** Use a coordinator-owned child, sign in before editing,
  keep its own leaf records, and wait to index them until the foreign
  owner signs out.
- **Rationale:** It avoids misreporting parallelism and respects exclusive
  edit scopes. The child branch remains preserved for parent integration.
- **Consequences:** The dashboard-index contract stays blocked until the
  owner releases `docs/ralph-status.md`; this is not a passing full-suite run.

## Verification and unresolved blockers

- Test-first Red: 4 expected failures because the four agents were absent.
- Green and post-refactor: all 4 specialist contract tests passed.
- Staged diff whitespace check: passed.
- Related 18-test contract run: 17 passed, exactly 1 failed because this
  new status leaf is not yet linked from the dashboard claimed by another
  agent.
- **Unresolved:** The foreign dashboard claim prevents indexing this new
  leaf and passing the broader Ralph dashboard contract. Parent routing,
  remote-main merge, and post-merge memory review are still pending.

### Resolution of the shared-file and integration blockers

The previous owner released its dashboard claim. The parent rebase mapped
the original implementation `1d9b29931ce3317162a126f482f87eb672af58b3`
and child tip `cb8ba5bb4cac293b130e7be0a443cb6d42bb1b93` to
`3a46abd5089f096804af6c0dc38daab35ddcfdcf` and
`74854cd8992e9ab5563f3e95c48ba7270482004a`. The tip's owned-file
contents are identical. The latter tip is an ancestor of parent
`56340cb2f89a738d560532046332c3794b5fec5c` via verified merge
`1f2f5488241f905f072f0fce94351f1b1264fd1b`. Both child dashboard
entries are now indexed and 13 focused tests pass. The deployed Ralph
coordinator allowlist now includes all four specialists; final remote-main
verification and memory review remain pending.
