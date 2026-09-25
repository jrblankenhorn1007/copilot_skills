# Ralph branch decisions

- **Run:** `copilot-skills-premerge-code-review-20260924`
- **Exact branch:** `ralph/code-review-gate-20260924-2131`
- **Base `origin/main` SHA:** `485b4a64c871f581f9295e46c867b188b0e3ccee`
- **Implementation commit:** pending
- **Integration:** `NOT_OPENED` — current project documentation runs use coordinator-managed verified fast-forward integration.
- **Agents:** coordinator, worker-01, worker-02

## Agent records

- [Coordinator PR decision record](agents/coordinator/pr-not-opened.md)
- [Worker-01 cancellation record](../ralph-code-review-skill-worker-01-20260924-2131/README.md)
- [Worker-02 PR decision record](../ralph-code-review-process-worker-02-20260924-2131/README.md)

Worker decision records remain in their branch-scoped folders and are linked
here when a sign-off or terminal disposition is recorded.

## Decisions

1. Use an independent read-only `Ralph Code Reviewer` for every PR and a
   `Ralph Security Reviewer` when the diff changes security-sensitive paths.
   This provides separate author/reviewer context while avoiding redundant
   full reviews for low-risk changes.
2. Bind each review to the exact PR base and head SHAs and repeat review when
   either changes. Stop automated review/author exchanges after ten rounds;
   the author then records the chosen disposition. Existing merge
   authorization, branch protection, CI, and human approval requirements
   remain in force.
3. Build a project-local review skill from verified code-review guidance and
   evaluation patterns; do not install or copy third-party skills.

## Research references

- [Google code-review standard](https://google.github.io/eng-practices/review/reviewer/standard.html)
- [Google review checklist](https://google.github.io/eng-practices/review/reviewer/looking-for.html)
- [GitHub Copilot code review](https://docs.github.com/en/copilot/concepts/agents/code-review)
- [VS Code custom agents](https://code.visualstudio.com/docs/agent-customization/custom-agents)
- [VS Code agent tools](https://code.visualstudio.com/docs/agents/run/tools)
- [VS Code subagents](https://code.visualstudio.com/docs/agents/run/subagents)
- [Project Agentic Eval skill](../../../.github/skills/agentic-eval/SKILL.md)
- [GitHub Awesome Copilot audit-integrity example](https://github.com/github/awesome-copilot/tree/main/skills/audit-integrity)
- [Bug Hunter skill example](https://github.com/codexstar69/bug-hunter)
