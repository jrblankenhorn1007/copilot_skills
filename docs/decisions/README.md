# Ralph Branch Decision Records

Keep iteration decisions and troubleshooting history under
`docs/decisions/<branch-slug>/`, with one folder per Ralph branch. The slug is
the lowercase branch name with `/` replaced by `-`; each branch folder's
`README.md` records the exact branch ref, base SHA, implementation commit SHA,
agent(s), PR/integration status, and links to its agent records.

Store one record per agent and PR at
`docs/decisions/<branch-slug>/agents/<agent-id>/pr-<number>.md`. Include the
agent's stable ID and runtime session ID when available. While an expected PR
number is pending, use `agents/<agent-id>/pr-pending.md`. If the branch is
integrated without a PR, use `agents/<agent-id>/pr-not-opened.md` and state
why no PR was opened. Once a PR number is assigned, move a pending record to
the numbered filename and update the branch index before merging.

Each record captures decisions with context, alternatives, chosen approach,
rationale, and consequences. Put recovered issues in a separate section with
sanitized symptoms, resolution, and verification. Keep unresolved blockers
separate from recovered issues. Never store credentials, tokens, or
secret-bearing command output. Append new decisions rather than rewriting
history. Commit each branch's index and agent records on that branch before
integration. Use the canonical
[status-first Ralph reporting contract](../../.github/skills/ralph-loop/references/multi-agent-status.md)
for interim and final reports: lead with the overall run state and list every
assigned agent's exact current status and next action. Report only unresolved
blockers as failures.

## Branch records

- [Ralph completion and PR decision-log contract](ralph-clear-completion-branch-pr-decisions-20260924-2018/README.md)
- [Ralph docs status organization](ralph-docs-status-dashboard-coordinator-c437fcd1/README.md)
- [Ralph parent-child pipeline](ralph-parent-child-orchestrator-20260924-2008/README.md)
- [Translated Ralph prompt skills recovery](ralph-translated-ralph-skills-worker-02-refresh-9558f99-20260925-0318/README.md)
- [Ralph pre-merge code-review gate](ralph-code-review-gate-20260924-2131/README.md)
- [Ralph review skill worker](ralph-code-review-skill-worker-01-20260924-2131/README.md)
- [Ralph review-gate status worker](ralph-code-review-process-worker-02-20260924-2131/README.md)
- [Shared agent resource manager](ralph-resource-manager-shared-registry-20260925-8abd5d4e/README.md)
- [Skill-aware agent routing](ralph-agent-optimization-parent-20260925-8bc457e9/README.md)

## Ralph status and progress

See the [Ralph status dashboard](../ralph-status.md) for the overall run
status and links to each branch/agent's status and progress records under
`docs/ralph/`.
