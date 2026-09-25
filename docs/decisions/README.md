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
integration. The final user-facing response reports completion status first
and reports only unresolved blockers as failures.

## Branch records

- [Ralph completion and PR decision-log contract](ralph-clear-completion-branch-pr-decisions-20260924-2018/README.md)

## Ralph status and progress

See the [Ralph status dashboard](../ralph-status.md) for the overall run
status and links to each branch/agent's status and progress records under
`docs/ralph/`.
