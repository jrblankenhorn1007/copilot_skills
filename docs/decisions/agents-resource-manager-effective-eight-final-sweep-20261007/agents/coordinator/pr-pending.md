# Coordinator — Replacement PR Pending

- **Run/task:** `copilot-skills-resource-manager-effective-eight-20261007` /
  `replay-review-and-integrate-capacity-fix`
- **Branch:** `agents/resource-manager-effective-eight-final-sweep-20261007`
- **Worktree:**
  `/Users/jrblankenhorn/copilot_skills.worktrees/resource-manager-effective-eight-final-sweep-20261007`
- **Original base:** `035c0e3e6ce05362c7a785191f527c8bf9985073`
- **Current fetched base:** `2abcbe040582e68cacc7192d2388fc5eaae7a816`
- **Implementation commits:** `91239bc123b4a3edf3a0f73e9edb6cd40ac967d0`,
  `acbf286dcef68f56b428b92e49b4f3e83fdf9316`.
- **Replacement PR:** pending creation; original PR #6 remains open until the
  replacement is published and verified.
- **State:** `IN_PROGRESS`; merge `PENDING`; memory review `PENDING`.
- **Review:** `PENDING`; no review round has completed for the replacement
  branch. Independent Ralph Code and Security reviewers are required.

## Change summary

The user requested that the Resource Manager's configured maximum be eight.
The first source commit raised `MAX_AGENTS` to eight; the follow-up made that
the effective configured base admission limit while retaining the separate
live-pressure safeguards. Hardware estimates remain diagnostic; degraded
pressure reduces the limit by one, and critical pressure still blocks new
admissions. Eight is the total-agent cap, including the coordinator.

The published source branch is not rewritten. Because main advanced after that
PR was opened, its implementation/test changes were replayed onto a fresh
branch from current main. The original Code and Security reports were clean
for PR #6's old base/head pair (`fb82e0d8...` / `95b9b020...`), but are stale
for this replacement PR and will not authorize its merge.

## Verification

- Existing Red/Green evidence is preserved in the two replayed implementation
  commit messages and the original PR #6 decision record.
- On the current synchronized branch:
  `test_resource_manager.py` 16/16, `test_multi_agent_contract.py` 29/29,
  `test_skill_aware_routing.py` 9/9, `test_specialist_agent_contract.py`
  5/5, `test_main_ownership_publisher.py` 15/15,
  `test_main_ownership_contract.py` 8/8, and `git diff --check` all pass.
- Do not report an old PR review as current evidence for the replacement PR.

## Decisions and consequences

- Keep the configured total limit at eight while preserving degraded and
  critical pressure checks as distinct safety controls.
- Use a fresh branch from current `origin/main` rather than rewrite the
  published PR #6 branch; this preserves its history and avoids force-pushing.
- Merge only after current-branch tests, independent exact-SHA reviews, and
  repository merge/ownership gates pass.

## Unresolved blockers

- None at this point. PR creation, current-branch reviews, and integration
  remain pending; reviewer dispatch requires a fresh live inventory and
  atomic Resource Manager reservations.
