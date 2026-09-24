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

- [TDD and Ralph Development Loop](.github/skills/tdd-ralph-loop/SKILL.md):
  coordinates test-first Red-Green-Refactor with a fresh worktree and branch
  per iteration, merged and verified on remote `main`.

## Agents

- [Ralph Loop](.github/agents/ralph-loop.agent.md): performs one focused
  development iteration in a fresh worktree and branch, then merges and
  verifies it on remote `main` using the TDD and Ralph loop skill.

## Using the agent and model controls

See [Copilot agent selection and model controls](.github/skills/tdd-ralph-loop/references/copilot-cli-usage.md)
for making Ralph selectable in VS Code/Copilot CLI and configuring supported
model reasoning-effort and context-window options.
