# copilot_skills
Copilot Skills

## Skills

Community skills are mirrored from
[github/awesome-copilot](https://github.com/github/awesome-copilot); upstream
license notices are preserved in each skill directory.

- [Acquire Codebase Knowledge](.github/skills/acquire-codebase-knowledge/SKILL.md):
  creates evidence-based codebase documentation when explicitly requested.
  Adapted from
  [github/awesome-copilot](https://github.com/github/awesome-copilot/tree/main/skills/acquire-codebase-knowledge)
  under MIT; see the [skill license](.github/skills/acquire-codebase-knowledge/LICENSE).

- [Agent Architecture](.github/skills/agent-architecture/SKILL.md):
  designs or audits AI-agent architecture without implementing it.
- [Agentic Eval](.github/skills/agentic-eval/SKILL.md):
  provides patterns for evaluating and improving agent outputs.
- [Agent OWASP Compliance](.github/skills/agent-owasp-compliance/SKILL.md):
  checks agent security posture against the OWASP Agentic Security Initiative.
- [Agent Skill Stack](.github/skills/agent-skill-stack/SKILL.md):
  discovers, evaluates, and assembles a minimal compatible skill set.
- [Copilot Instructions Blueprint Generator](.github/skills/copilot-instructions-blueprint-generator/SKILL.md):
  creates project-specific Copilot instruction blueprints.
- [Docs Sync Audit](.github/skills/docs-sync-audit/SKILL.md):
  compares documentation claims with source and configuration.
- [Project Memory](.github/skills/project-memory/SKILL.md):
  captures and maintains concise, evidence-backed lessons in categorized
  repository memory; see the [memory index](.github/memory/README.md).

- [Resource Manager](.github/skills/resource-manager/SKILL.md):
  gates concurrent agents through a shared local registry sized by available
  memory, CPU capacity, and live system load.
- [Ralph Loop](.github/skills/ralph-loop/SKILL.md):
  refreshes the canonical skills and active project repositories at the start
  of every iteration and re-reads applicable guidance. It makes the first run
  an orchestrator (not a worker), dispatches two configurable worker agents by
  default when independent work allows. For orchestrated runs, configure the
  launcher/session with `--orchestrator` (not as a native Copilot CLI flag),
  start the orchestrator in a parent worktree and parent branch, and give
  workers their own child worktrees and child branches. The coordinator merges
  completed worker branches into the parent serially; only the completed
  parent merges to `origin/main`. Close each child branch/worktree only after
  its parent merge is verified; close the parent only after its remote-main
  merge is verified. The workflow verifies integration on remote `main` and
  reviews durable lessons after the parent merge. Its
  [multi-agent orchestration guide](.github/skills/ralph-loop/references/multi-agent-orchestration.md)
  covers configurable worker counts and Git synchronization; the
  [multi-agent status guide](.github/skills/ralph-loop/references/multi-agent-status.md)
  defines overall and per-worker iteration reporting. Its Git preflight checks
  configured Git identity and remote read access before work, and distinguishes
  those from branch-push and merge permissions. The
  [worker-owned PR merge guide](.github/skills/ralph-loop/references/worker-pr-merging.md)
  requires an authorized worker to merge its own PR with its existing GitHub
  CLI access.
- [Ralph PR Review](.github/skills/ralph-pr-review/SKILL.md):
  defines the independent, evidence-bounded review rubric and report format
  used by the pre-merge review gate.
- [Test-Driven Development](.github/skills/tdd/SKILL.md):
  applies test-first Red-Green-Refactor to behavior changes and bug fixes.

## Agents

- [Ralph Loop](.github/agents/ralph-loop.agent.md): refreshes repositories and
  instructions per iteration, orchestrates configurable workers through
  isolated iterations, acts as the top-level orchestrator on the first run,
  verifies remote-main integration, reviews durable lessons, and applies TDD
  to behavior changes. It registers the orchestrator and reserves worker
  slots through the Resource Manager. It distinguishes Git identity, remote
  read access, branch-push access, and merge permissions.
- [Ralph Code Reviewer](.github/agents/ralph-code-reviewer.agent.md):
  independently reviews every PR after worker sign-off and before merge
  authorization; it is read-only and does not replace required human review.
- [Ralph Security Reviewer](.github/agents/ralph-security-reviewer.agent.md):
  provides a separate, read-only security review when a diff touches
  security-sensitive behavior.

## Pre-merge PR review

Every PR receives an independent Ralph Code Reviewer pass after branch-owner
sign-off and before the applicable merge action. Launch
Ralph Security Reviewer as well when the diff touches authentication or
authorization, untrusted input, secrets or sensitive data, cryptography,
process execution, external boundaries, dependencies, or security
configuration. Reports are bound to exact base/head SHAs; a changed SHA
invalidates the report and blocks merge authorization until a fresh review.
Allow at most two completed rounds per branch/PR: an initial review and one
follow-up after the author agent acts on the first report. After the follow-up,
the author agent acts on that report alone; no third reviewer pass is launched.
A clean report is evidence, not a guarantee or replacement for CI, branch
protection, or required human approvals. The coordinator-managed no-PR
fast-forward path remains unchanged and records review as `NOT_APPLICABLE`.

## Using the agent and model controls

See [Copilot agent selection and model controls](.github/skills/ralph-loop/references/copilot-cli-usage.md)
for selecting the orchestrator model and configuring separate worker models,
reasoning-effort, and context-window options in VS Code/Copilot CLI.

## Current Ralph status

See [docs/ralph-status.md](docs/ralph-status.md) for the overall status and
the branch/agent links to current-state and progress records.
Schema-version-2 leaf reports and matching branch-index entries carry the
same branch-local wall-clock elapsed time and provider-reported token counts;
unavailable token usage is explicitly `NOT_REPORTED`, never zero or an
estimate. See the
[per-branch time and token usage contract](.github/skills/ralph-loop/references/multi-agent-status.md#per-branch-time-and-token-usage)
for field definitions, synchronization, and legacy-record handling.

## Ralph decision records

See [docs/decisions/README.md](docs/decisions/README.md) for the
branch-scoped, per-agent/per-PR decision-log format, including recovered
issues and unresolved blockers.

## Validation

Run the resource-manager registry tests and Ralph multi-agent instruction
contract checks from the repository root:

```sh
python3 .github/skills/resource-manager/tests/test_resource_manager.py
python3 .github/skills/ralph-loop/tests/test_multi_agent_contract.py
```
