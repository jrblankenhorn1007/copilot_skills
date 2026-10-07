# Progress

## 2026-10-07T05:21:49Z — iteration 1 started

- **Acceptance:** Add frozen model-facing cases for every installed Skill,
  Copilot agent definition, and OpenCode agent profile; pin any live call to
  GPT-6 Luna, max reasoning, and default context; compare focused versus
  catalog context; and run local checks. The user later added the
  document-owner communication timing/content experiment and authorized
  structural changes.
- **Branch/worktree:** `ralph/pipeline-live-model-evaluation-20261007-35327e2e`
  in `/Users/jrblankenhorn/copilot_skills.worktrees/ralph-pipeline-live-model-evaluation-20261007-35327e2e`,
  initially based on `fb82e0d85ef80b26537c3fede01bcaefa422652d`.
- **Task scope:** The published task status was updated through revision 4;
  `docs/ralph-status.md` was released to the janitor and is not edited here.
  The correlated scope-release message was accepted as queued; no processing
  acknowledgement was observed at the later deadline check.
- **Capacity:** The refreshed Resource Manager inventory reported zero free
  slots. No child agents were dispatched; the work proceeded serially.

## 2026-10-07T18:33:33Z — offline suite and communication experiment

- **TDD Red/Green — profile coverage:** Added a test requiring every
  OpenCode-role case to select its named profile. The initial run failed only
  for `ralph-loop-worker`, whose runner was `plan`. Updated the frozen case to
  invoke `ralph-loop-worker`; the coverage and runner tests then passed.
- **TDD Red/Green — communication payloads:** Expanding the blocking-event
  case first exposed a missing `reply deadline` expectation and then missing
  `blocking_dependency` payload fields. The test now requires exact
  fields for scope collisions, blocking dependencies, review-ready handoffs,
  and verified completion; the fixture was corrected and the two focused
  communication tests pass.
- **Coverage:** The final matrix contains 13 Skills, 8 Copilot agent
  definitions, 4 OpenCode agent profiles, and 3 routing boundaries. All
  target instruction files are present in the corresponding case context.
  OpenCode-role cases request the matching profile; Copilot definitions are
  exercised as model-facing instructions through OpenCode `plan`, not as
  activated Copilot-host agents.
- **Local validation:** All 82 pre-existing contract tests and all 32 new
  deterministic tests passed (114 total). JSON, Python syntax, and
  `git diff --check` validations passed.
- **Focused-context experiment:** Offline byte reductions were 94.02% for
  Agent Architecture (223,075 versus 13,329 bytes), 91.88% for Agent Skill
  Stack (223,070 versus 18,121 bytes), and 92.61% for Docs Sync Audit
  (223,068 versus 16,492 bytes). No model calls or token estimates were
  reported.
- **Document-owner experiment:** The synthetic per-edit control proposed
  seven messages (three routine); the event-triggered candidate proposed
  four (zero routine), saving three messages or 42.9%. No messages were sent.
  Transport, recipient-processing, and end-to-end latency remain
  `NOT_MEASURED`; the control is not an observed host baseline.
- **Live blocker:** `opencode auth list` showed zero credentials;
  `run_live_model_cases.py --preflight` found no unique `gpt-6-luna` provider
  model; the `copilot` CLI is unavailable. No live call was attempted and no
  model was substituted, as required by the prompt.
- **Current implementation commit before final rebase:** `d5cf0f6576d7c9b9f98216093167db48f728479e`.
  At the latest fetch recorded here, `origin/main` was
  `c23b6e8ffb285ef57f4d99b45425a31ad031ee91`. Rebase and authorized
  integration remain pending; rerun the local suite after rebasing.

## 2026-10-07T18:39:29Z — refresh coverage for newly added janitor roles

- **Rebase:** Rebased implementation commit
  `d5cf0f6576d7c9b9f98216093167db48f728479e` onto fetched
  `origin/main` `c23b6e8ffb285ef57f4d99b45425a31ad031ee91`, producing
  `c1c3f7206192227def7e47b4d01141f08e08a0ea`. No conflicts occurred.
- **Late matrix additions:** The refreshed main added
  `.github/agents/ralph-worktree-janitor.agent.md` and
  `.opencode/agents/ralph-worktree-janitor.md` after the initial case freeze.
  Kept the original case IDs and added
  `agent-ralph-worktree-janitor` and
  `opencode-agent-ralph-worktree-janitor`; added an explicit default-context
  entry for the Copilot profile.
- **TDD Red/Green:** The post-rebase coverage test first failed because the
  new Copilot role lacked both a case and an explicit default-context entry.
  Added both janitor cases with a non-destructive blocked-cleanup scenario,
  then reran coverage (9 tests) and runner tests (21 tests); both passed.
- **Current matrix:** 13 Skills, 9 Copilot agent definitions, 5 OpenCode
  agent profiles, and 3 routing boundaries. Every case includes its target
  instruction file; every OpenCode profile case requests that same profile.
- **Updated offline context experiment:** Agent Architecture saved 216,594
  bytes (94.20%; 229,923 versus 13,329); Agent Skill Stack saved 211,797
  bytes (92.12%; 229,918 versus 18,121); Docs Sync Audit saved 213,424
  bytes (92.83%; 229,916 versus 16,492). These are bytes, not token or
  latency measurements.
- **Dashboard contract:** The full suite exposed the expected unindexed-leaf
  gate because this task released `docs/ralph-status.md` to the janitor.
  Did not edit the dashboard. Marked this coordinator leaf `BLOCKED` with
  `pending_dashboard_update: true` and the exact shared path/owner run ID;
  the focused 30-test multi-agent contract suite then passed.
- **Still pending:** Rerun the complete local suite after the late case
  additions, refresh the remote owner/base before further integration, and
  use the no-PR `MERGE` transaction only after the current owner releases it.
  No live calls were made; Luna preflight remains blocked.

## 2026-10-07T18:41:30Z — full suite green after dashboard-scope record

- **Full local suite:** All 84 pre-existing tests and 32 new evaluation and
  communication tests passed (116 total). The test counts were 8 main
  ownership contract, 15 publisher, 30 Ralph multi-agent, 9 routing, 6
  specialist, 1 memory, 15 resource-manager, 21 runner, 9 coverage, and 2
  document-owner communication tests.
- **Dashboard contract recovery:** A prior full-suite run failed only because
  this blocked coordinator leaf was not indexed while `docs/ralph-status.md`
  remained released to the janitor. Recorded the exact pending path and owner
  run ID without editing the dashboard; the focused Ralph multi-agent suite
  passed (30 tests), followed by the full suite.
- **Static checks:** `git diff --check`, JSON parsing for both JSON files,
  and `py_compile` for all four Python files passed.
- **Current role coverage:** The frozen matrix now contains 13 Skills, 9
  Copilot agents, 5 OpenCode profiles, and 3 routing boundaries, including
  the newly added worktree-janitor definitions. The evaluation still
  distinguishes OpenCode profile invocation from Copilot instruction
  conformance.
- **Latest offline context results:** 94.20% fewer bytes for Agent
  Architecture, 92.12% for Agent Skill Stack, and 92.83% for Docs Sync
  Audit; all token counts remain null and model calls remain zero.
- **Latest communication result:** The synthetic comparison remains 7
  control versus 4 candidate messages (42.9% fewer); no messages were sent,
  and no transport or task latency is claimed.
- **Current code commit:** `17dad8789e6c01a84d6dfeebd3a3657c079087a5`,
  based on `c23b6e8ffb285ef57f4d99b45425a31ad031ee91`. At the
  `18:41:30Z` fetch, remote main ownership was `FREE` at revision 278 and
  no covered role files had changed since the rebase. Recheck before writing.
- **Next:** Publish the task status as `AWAITING_MERGE`, rebase and rerun
  checks on the resulting status-sign-in tip, then acquire `MERGE`, integrate
  the reservation commit, push non-force, and verify the remote result.
  Preserve the janitor's dashboard scope. Live execution remains blocked
  until the requested model and capacity are available.
