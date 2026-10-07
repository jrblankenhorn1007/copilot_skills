# Task: Make the Eight-Agent Limit Hardware-Bounded

## Context

The current Resource Manager change sets `MAX_AGENTS` to eight and also sets
`base_agents = MAX_AGENTS`, allowing an eight-agent total even when the
reported RAM and CPU estimates are lower. Independent security review found a
medium-confidence availability risk on small hosts. Current `origin/main` is
`2fdbc958b76a5c31bbbbfc2d5ea8fe49812a3156`.

## Goal

Keep eight as the hard configured ceiling while ensuring the effective base
admission limit does not exceed the host-derived RAM and CPU estimates. Live
degraded-pressure and critical-pressure safeguards must continue to reduce or
deny admission.

## Acceptance criteria

- `MAX_AGENTS` remains eight, and large hosts may reach an effective total of
  eight agents.
- Normal small-host capacity is bounded by both estimates: the 8-GiB,
  six-core fixture admits two total agents; the 8-GiB, two-core fixture
  admits one; a 32-GiB, sixteen-core fixture can admit eight.
- Degraded and critical live-pressure behavior remains covered and correct.
- Update the Resource Manager guidance so it distinguishes the configured
  ceiling from the hardware-bounded effective capacity.
- Follow Red-Green-Refactor: first change/add the narrowest capacity test and
  demonstrate the unsafe implementation fails it, then implement and verify.
- Keep edits to the Resource Manager source, its tests, its skill guidance,
  and this branch's decision/status records. Do not modify PR #6 or PR #8
  worktrees or their published branch histories.
- The Janitor still owns `docs/ralph-status.md`. Preserve that scope, mark
  this branch's dashboard entry pending, and do not edit the dashboard until
  a verified owner release.
- Open a fresh PR from this branch. Require independent Code and Security
  reviews on the exact full base/head SHAs and verify all applicable checks
  before any merge.
- Use only the configured GitHub CLI/authentication, make no direct main
  edits, and include the repository's required Copilot co-author trailer in
  commits.

## Relevant skills

- Ralph Loop: `.github/skills/ralph-loop/SKILL.md` — isolated branch, status,
  decision, review, and merge workflow.
- TDD: `.github/skills/tdd/SKILL.md` — this is a behavior change and requires
  a verified failing test before production edits.
- Resource Manager: `.github/skills/resource-manager/SKILL.md` — admission
  and registration policy.
- Project Memory: `.github/skills/project-memory/SKILL.md` — required review
  after verified implementation integration.
