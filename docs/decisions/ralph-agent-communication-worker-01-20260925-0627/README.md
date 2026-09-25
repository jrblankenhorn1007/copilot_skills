# Agent Communication Worker Branch Decisions

- **Run:** `copilot-skills-agent-communication-20260925-0627`
- **Task:** `agent-communication-skill`
- **Worker:** `worker-01 / agent communication skill`
- **Exact branch:** `ralph/agent-communication-worker-01-fallback-20260925-1647`
- **Current worktree:** `/Users/jrblankenhorn/copilot_skills.worktrees/ralph-agent-communication-worker-01-fallback-20260925-1647`
- **Parent branch:** `ralph/agent-communication-parent-20260925-0627`
- **Initial base parent SHA:** `15d0597d1bf693f9ebea3c348ad73d160e896fee`
- **Rebased onto parent SHA:** `3257768c7e43824d38a46f89e751add006d0790e`
- **Parent's initial main base:** `20293c720b18a1a21ff150f566823493b7a2717d`
- **Current parent rebase base (`origin/main`):** `c1ac03a4d3378789450b7ac59a655fcbff974241`
- **Current parent HEAD:** `3257768c7e43824d38a46f89e751add006d0790e`
- **Current parent implementation commit:** `db6d18e1c49fe3a0af962b0b3c6add156b4ca460`
- **Current fetched origin/main:** `d8af3e8d87cd32aaab128bb6edabd6e8402da5e4`
- **Current implementation commit:** `d93041a2d19108929e44e03b2b977429e56ed6fa`
- **Current worker-series head:** `d93041a2d19108929e44e03b2b977429e56ed6fa`
- **Status:** `AWAITING_MERGE`; the new fixed/shared message-limit guidance
  passes the focused and full contract suite but has not yet been integrated
  into the parent. Earlier worker-series and metadata branch proofs remain
  historical and unchanged. No worker PR is opened.

## Agent records

- [Worker-01 — no PR opened](agents/worker-01/pr-not-opened.md)

## Fixed/shared message-limit fallback — 2026-09-25T18:02:51Z

- **Context:** The coordinator's TDD Red asserts that a fixed/shared host
  message cap must fail the route, prevent new-session/session-spawn bypasses,
  and use a durable channel or report blocked.
- **Alternatives:** Retry from another session or spawned relay; treat the cap
  as a temporary per-session quota; use an already available coordination
  channel or report the route blocked.
- **Choice:** Mark a host-reported fixed/shared cap as `failed`; do not retry
  from a new session or spawn relay sessions to bypass it; do not claim a
  universal numeric quota; prefer an already available authorized durable
  coordination channel, otherwise report blocked.
- **Rationale:** The current `.github/memory/tooling.md` records that the
  observed cap is fixed/shared across sessions and that retrying after delay
  or from another session did not reset it. The skill applies this evidence
  without reproducing the memory entry's full chronology.
- **Consequence:** The sender avoids multiplying failed delivery attempts and
  must not claim delivery or processing when no durable route is available.
