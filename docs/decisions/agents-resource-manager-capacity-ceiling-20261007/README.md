# Decisions — `agents/resource-manager-capacity-ceiling-20261007`

- **Run ID:** `copilot-skills-resource-manager-capacity-ceiling-20261007`
- **Task ID:** `hardware-bounded-eight-agent-cap`
- **Branch:** `refs/heads/agents/resource-manager-capacity-ceiling-20261007`
- **Worktree:** `/Users/jrblankenhorn/copilot_skills.worktrees/resource-manager-capacity-ceiling-20261007`
- **Starting `origin/main` SHA:** `2fdbc958b76a5c31bbbbfc2d5ea8fe49812a3156`
- **Coordinator:** `coordinator - hardware-bounded eight-agent capacity`

## Decisions

### Keep eight as a ceiling, not a hardware-independent admission count

- **Context:** PR #6 sets the effective base admission limit to eight on every
  host. Its independent Security Reviewer found that an 8-GiB, 2-core host can
  admit eight total agents even though its RAM and CPU estimates are two and
  one.
- **Decision:** Keep `MAX_AGENTS = 8` as the global ceiling, but bound the
  effective base by both host estimates. Preserve degraded-pressure reduction
  and critical-pressure denial.
- **Rationale:** The user-requested maximum remains eight on hosts with enough
  resources while the manager does not knowingly over-admit small hosts.
- **Evidence:** PR #6's `resource_manager.py:194` sets
  `base_agents = MAX_AGENTS`; its small-host test expects eight despite
  estimates of two and one. The new hardware-bound assertion fails against
  that implementation and the cap-eight assertion fails against current main.
- **Consequence:** On smaller machines, the effective total may be less than
  eight; available capacity remains the upper bound for all worker requests.

### Preserve the Janitor-owned dashboard scope

- **Context:** The active Janitor task status still claims
  `docs/ralph-status.md` and has no verified sign-out.
- **Decision:** Keep this branch leaf blocked and pending dashboard indexing;
  do not edit the aggregate dashboard until the ledger records a release.
- **Consequence:** Dashboard synchronization and any integration gate that
  depends on that index remain pending.

## PR records

- [`coordinator` / PR #11](agents/coordinator/pr-11.md)
