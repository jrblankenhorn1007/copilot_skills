# Security Review — PR #6

## Scope and disposition

- PR: https://github.com/jrblankenhorn1007/copilot_skills/pull/6
- Reviewed base/head: `2fdbc958b76a5c31bbbbfc2d5ea8fe49812a3156` /
  `d9fab82e1490a13729318eb58bb65561df9c4a31`
- Round 1: Code Reviewer `CLEAN`; Security Reviewer `FINDINGS`.
- Round 2: Code Reviewer `CLEAN`; Security Reviewer `CLEAN`, but its rationale
  contradicted the exact reviewed source and test. The coordinator verified
  the discrepancy at the exact head.
- Final action at the two-round limit: `ESCALATE_FOR_HUMAN_REVIEW`. No third
  agent review is permitted. The current PR head changed to
  `9a8912e093ed631e01a28122e84c8768e9df2a40` to record this disposition.
  A subsequent documentation-only commit added this summary, so the current
  PR head is newer still. The prior reports are stale for the current head
  and human review is required.

## Finding

| # | Severity | File | Lines | Vulnerability | Confidence |
|---|----------|------|-------|---------------|------------|
| 1 | 🟡 MEDIUM | `.github/skills/resource-manager/scripts/resource_manager.py` | 194 | The effective base ignores the hardware-derived RAM/CPU estimates. For an 8-GiB, 2-core host with 4 GiB available, the manager can admit an orchestrator plus seven child slots, increasing the risk of memory/CPU exhaustion and host unavailability. Degraded pressure only reduces the cap by one; the critical-pressure guard prevents new admissions but does not stop already admitted agents. | High |

The round-two Security Reviewer reported that the effective limit remained
bounded by RAM/CPU estimates and that the small-host limit was one. That
statement does not match the exact source: `base_agents = MAX_AGENTS` at line
194, and `test_capacity_uses_configured_limit_and_reports_hardware_guidance`
expects eight slots for an 8-GiB, 2-core host while reporting RAM/CPU
estimates of 2/1. The coordinator therefore did not treat the round-two
`CLEAN` conclusion as resolving finding R1.

The effective eight-agent policy was explicitly requested, and the Resource
Manager skill documents that the configured limit can exceed hardware
estimates. That user direction does not eliminate the availability risk or
the need for human disposition. No source or test assertion was changed to
hide the finding.

## Verification and remaining gates

- Resource Manager tests: **16/16 passed**.
- Related routing, specialist-agent, main-ownership publisher, and
  main-ownership contract suites: **9/9, 6/6, 15/15, and 8/8 passed**.
- Ralph contract suite: **29/30 passed**. The one failure is the missing
  pipeline-evaluation coordinator dashboard entry; the same failure
  reproduces on fetched `origin/main` and is unrelated to this PR. The
  dashboard remains in the Janitor task's edit scope.
- GitHub reports no hosted checks.
- Do not merge until a human reviews the current PR head, applicable test and
  approval gates are satisfied, and the merge result is verified on fetched
  `origin/main`.
