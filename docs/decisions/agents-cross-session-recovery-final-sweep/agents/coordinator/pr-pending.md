# Coordinator — Parent PR Pending

- **Agent:** `coordinator`
- **Branch:** `agents/cross-session-recovery-final-sweep`
- **Worktree:**
  `/Users/jrblankenhorn/copilot_skills.worktrees/cross-session-recovery-final-sweep`
- **Base `origin/main`:** `fb82e0d85ef80b26537c3fede01bcaefa422652d`
- **Implementation commits:** `169dbc19` (raises the configured ceiling) and
  `bd1ae36f` (makes eight the effective base admission limit while retaining
  critical-pressure stops).
- **PR:** #6 — <https://github.com/jrblankenhorn1007/copilot_skills/pull/6>
- **Current state:** `IN_PROGRESS`; parent-to-main merge is `PENDING`.
- **Review:** `BLOCKED`; no review round has completed. The independent Ralph
  Code Reviewer and Ralph Security Reviewer must review the exact PR SHAs.

## Change summary

User directly instructed: "set max agents to 8, commit that fix, and
continue." The initial commit raised `MAX_AGENTS` from 4 to 8, but a follow-up
check showed this only raised the upper ceiling: the memory/CPU-derived
formula still produced an effective limit of 2 on this 8 GiB, six-core host.
The follow-up change makes `MAX_AGENTS` the effective base admission limit of
8, while preserving the existing degraded-pressure reduction and critical
pressure fail-closed behavior. RAM- and CPU-derived estimates remain
available as diagnostics, not as admission caps. Updated the Resource Manager
skill to state this explicitly.

## TDD evidence

- **Initial Red:** added `test_global_agent_ceiling_is_eight`, pinning
  `manager.MAX_AGENTS == 8` and a 64 GiB/32-core host's computed capacity to
  `8`; it failed as expected with `AssertionError: 8 != 4`.
- **Initial Green:** changed `MAX_AGENTS = 4` to `MAX_AGENTS = 8`; all 16
  Resource Manager tests passed. This raised the hard ceiling but did not yet
  make eight the effective host limit.
- **Effective-capacity Red:** changed the 8 GiB/six-core and small-host
  capacity tests to expect a configured limit of 8, degraded pressure to
  reduce it to 7, and critical pressure to remain 0. Running
  `python3 .github/skills/resource-manager/tests/test_resource_manager.py -v`
  failed as expected: effective capacity remained 2 (normal host), 1 (small
  host), and 1 (degraded memory), respectively.
- **Registry-fixture update:** updated admission tests to fill the configured
  eight slots rather than assuming the old two/three-agent hardware-derived
  limit. The tests still assert rejection at capacity and under concurrent
  reservations.
- **Green:** set `base_agents = MAX_AGENTS`, retaining the existing pressure
  checks. The targeted suite then passed all 16 tests.
- **Regression sweep:** also reran
  `test_multi_agent_contract.py` (29 passed),
  `test_skill_aware_routing.py` (9 passed),
  `test_specialist_agent_contract.py` (5 passed),
  `test_main_ownership_publisher.py` (15 passed), and
  `test_main_ownership_contract.py` (8 passed) — all green after the
  effective-limit follow-up.
- `git diff --check` — clean (no whitespace issues).

## Risk assessment (for reviewer-gate routing)

This diff increases the Resource Manager's actual admission limit to eight
even on hosts whose RAM/CPU estimates are lower. The memory/CPU pressure
estimates are still reported, degraded pressure reduces the limit by one,
and critical pressure still blocks new admissions. This is an intentional
resource-policy change with greater resource-exhaustion risk on smaller
hosts; do not describe the hardware estimates as admission constraints.
Require an independent **Ralph Code Reviewer**. The coordinator also requests
a **Ralph Security Reviewer** as a conservative check of this resource
admission-control policy change; neither review may be replaced by
self-review.

## Unresolved blockers

- At the latest fresh inventory (`2026-10-07T05:10:15Z`), the configured
  base is `8` but effective `capacity.max_agents` is `0` because one-minute
  load was `9.46` on a six-core host, crossing the critical load threshold.
  There are 3 active agents and no available slots. The code and tests now
  report the requested configured limit correctly; the unchanged critical
  pressure safeguard temporarily prevents all new admissions. Do not launch
  reviewers until a fresh inventory reports `can_spawn: true` and atomic
  reservations succeed.
- The PR is not yet merged; complete review, CI, required approvals, and the
  normal merge gate before recording remote-main verification.
