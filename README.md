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

- [Ralph Loop](.github/skills/ralph-loop/SKILL.md):
  refreshes the canonical skills and active project repositories at the start
  of every iteration and re-reads applicable guidance. It makes the first run
  an orchestrator (not a worker), dispatches two configurable worker agents by
  default when independent work allows, verifies integration on remote `main`,
  and reviews durable lessons after each merge. Its
  [multi-agent orchestration guide](.github/skills/ralph-loop/references/multi-agent-orchestration.md)
  covers configurable worker counts and Git synchronization; the
  [multi-agent status guide](.github/skills/ralph-loop/references/multi-agent-status.md)
  defines overall and per-worker iteration reporting. Its Git preflight checks
  configured Git identity and remote read access before work, and distinguishes
  those from branch-push and merge permissions.
- [Test-Driven Development](.github/skills/tdd/SKILL.md):
  applies test-first Red-Green-Refactor to behavior changes and bug fixes.

## Agents

- [Ralph Loop](.github/agents/ralph-loop.agent.md): refreshes repositories and
  instructions per iteration, orchestrates configurable workers through
  isolated iterations, acts as the top-level orchestrator on the first run,
  verifies remote-main integration, reviews durable lessons, and applies TDD
  to behavior changes. It distinguishes Git identity, remote read access,
  branch-push access, and merge permissions.

## Using the agent and model controls

See [Copilot agent selection and model controls](.github/skills/ralph-loop/references/copilot-cli-usage.md)
for selecting the orchestrator model and configuring separate worker models,
reasoning-effort, and context-window options in VS Code/Copilot CLI.

## Current Ralph status

See [implementation_status.md](implementation_status.md) for the overall
status, worker iterations, sign-offs, and remote-merge evidence for this
multi-agent run.

## Ralph decision records

See [docs/decisions/README.md](docs/decisions/README.md) for the
branch-scoped, per-agent/per-PR decision-log format, including recovered
issues and unresolved blockers.

## Validation

Run the Ralph multi-agent instruction contract checks from the repository
root:

```sh
python3 .github/skills/ralph-loop/tests/test_multi_agent_contract.py
```
