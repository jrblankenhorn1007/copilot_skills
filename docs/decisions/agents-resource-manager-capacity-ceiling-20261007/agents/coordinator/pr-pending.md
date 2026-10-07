# PR Pending — `hardware-bounded-eight-agent-cap`

- **Run/task:** `copilot-skills-resource-manager-capacity-ceiling-20261007` /
  `hardware-bounded-eight-agent-cap`
- **Branch:** `agents/resource-manager-capacity-ceiling-20261007`
- **Worktree:** `/Users/jrblankenhorn/copilot_skills.worktrees/resource-manager-capacity-ceiling-20261007`
- **Starting `origin/main` SHA:** `2fdbc958b76a5c31bbbbfc2d5ea8fe49812a3156`
- **Status-only sign-in commit:** `ecb2e653ad17ee5ff5e7dd82e2ce9135eaa8f1b0`
- **Latest progress status commit:** `5aa6a36f1ab4b037d806792840d70bbba338f94e`
- **Latest verified `origin/main`:** `8065bba4bd04c6567ff7ef2c15699817abb85178`
- **Implementation commit:** pending
- **Pull request:** not opened

## Integration plan

The branch preserves `MAX_AGENTS = 8` but restores the RAM/CPU-derived
effective admission bounds. The PR will require independent Code and Security
reviews bound to the exact full base/head SHAs, targeted Resource Manager
tests, and `git diff --check`. No merge is authorized until all applicable
checks and review gates pass and the dashboard owner releases the shared
scope.

## Initial TDD evidence

- The new large-host cap test failed on current main as expected because
  `MAX_AGENTS` is four.
- The existing hardware-bound capacity test failed against PR #6's
  implementation as expected because its 8-GiB, 2-core fixture was admitted
  at eight rather than one.
- The hardware-bounded implementation passes the complete Resource Manager
  suite (16 tests) and `git diff --check`.
- The focused dashboard-index contract still fails only for the pre-existing
  pipeline-live-model-evaluation coordinator leaf. This branch's blocked,
  explicitly pending dashboard leaf is accepted by the contract.

## Blockers

- `docs/ralph-status.md` remains owned by
  `copilot-skills-worktree-janitor-20261007`; its task status has no verified
  sign-out. This branch's leaf remains
  `pending_dashboard_update: true`; do not edit that dashboard.
