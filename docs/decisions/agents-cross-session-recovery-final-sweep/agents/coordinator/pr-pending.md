# Coordinator — Parent PR Pending

- **Agent:** `coordinator`
- **Branch:** `agents/cross-session-recovery-final-sweep`
- **Worktree:**
  `/Users/jrblankenhorn/copilot_skills.worktrees/cross-session-recovery-final-sweep`
- **Base `origin/main`:** `fb82e0d85ef80b26537c3fede01bcaefa422652d`
- **Implementation commit:** `169dbc19` (`fix(resource-manager): raise global
  agent ceiling to eight`)
- **PR:** pending creation; will be updated with number/URL once opened.
- **Current state:** `IN_PROGRESS`; parent-to-main merge is `PENDING`.
- **Review:** `BLOCKED`; required reviewer is the Ralph Code Reviewer per
  `.github/skills/ralph-loop/references/worker-pr-merging.md`. No review
  round has completed.

## Change summary

User directly instructed: "set max agents to 8, commit that fix, and
continue." `MAX_AGENTS` in
`.github/skills/resource-manager/scripts/resource_manager.py` was hardcoded
at `4`, capping both the memory- and CPU-derived admission limits even on
hosts with capacity to spare. Raised the constant to `8` and updated the two
corresponding sentences in `.github/skills/resource-manager/SKILL.md` ("capped
at four agents" → "capped at eight agents", twice). No other file mentions
this specific numeric cap (verified via repo-wide grep); all other "four"
matches in the repo are unrelated (specialist counts, memory-type taxonomies,
etc.).

## TDD evidence

- **Red:** added `test_global_agent_ceiling_is_eight` to
  `.github/skills/resource-manager/tests/test_resource_manager.py`, pinning
  `manager.MAX_AGENTS == 8` and a 64 GiB/32-core host's computed capacity to
  `8` (not a tautological reference to the constant). Ran
  `python3 .github/skills/resource-manager/tests/test_resource_manager.py -v`
  — failed as expected: `AssertionError: 8 != 4`. All 15 pre-existing tests in
  that file passed unchanged.
- **Green:** changed `MAX_AGENTS = 4` to `MAX_AGENTS = 8`. Reran the same
  command — all 16 tests passed.
- **Regression sweep:** also reran
  `test_multi_agent_contract.py` (29 passed),
  `test_skill_aware_routing.py` (9 passed),
  `test_specialist_agent_contract.py` (5 passed),
  `test_main_ownership_publisher.py` (15 passed), and
  `test_main_ownership_contract.py` (8 passed) — all green, confirming no
  consumer of the resource-manager skill depends on the old cap value.
- `git diff --check` — clean (no whitespace issues).

## Risk assessment (for reviewer-gate routing)

This diff changes one integer constant plus matching documentation prose and
adds a unit test. It does not touch authentication/authorization, untrusted
input, secrets, cryptography, new process-execution logic (the existing
`sysctl`/`memory_pressure` subprocess calls are unchanged), external network
boundaries, or dependencies. Routed to the standard **Ralph Code Reviewer**
gate only; **Ralph Security Reviewer** was not judged necessary given the
above, consistent with
`.github/skills/ralph-loop/references/worker-pr-merging.md`'s trigger list.

## Unresolved blockers

- The shared Resource Manager reports zero available slots at this iteration
  (`active_agent_count: 18`, this host's computed `capacity.max_agents: 2`
  — RAM-bound at 2 regardless of the new ceiling of 8, since this machine
  has only ~3.8 GiB available RAM — `available_slots: 0`, `can_spawn: false`).
  This blocks dispatching the required independent Ralph Code Reviewer.
  Per the Ralph Loop agent's explicit instruction, this is recorded as
  `BLOCKED`; self-review is not substituted and the gate is not claimed to
  have passed.
- The parent is not yet published or merged; remote-main verification remains
  pending until review capacity is available and a clean report is obtained
  for the exact PR base/head SHAs.
