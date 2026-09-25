# Conditional specialist routing for Ralph Loop

Select an agent for a bounded task, not an agent for every installed Skill.
The user-facing Ralph Loop entrypoint delegates the complete request to
the internal Ralph Orchestrator; the entrypoint does not dispatch specialists.
The Ralph Orchestrator owns the split plan, exclusive edit scope, worker
count, dashboard, specialist routing, and final verification. This guide complements the
[multi-agent orchestration](multi-agent-orchestration.md),
[Resource Manager](../../resource-manager/SKILL.md), and the
main-ownership protocol at `docs/agent-sync/main-ownership.md`.
If the latter is not yet present on an older task branch, read the current
fetched main version before any main transaction; do not treat its absence
as permission to bypass the ownership rules. If fetched main lacks the
protocol too, stop and report that prerequisite instead of improvising a
status or merge write.

## Decide at the task boundary

Default to the general Ralph Loop Worker. Look at the user's requested outcome and
the relevant Skill's trigger before routing an independent, bounded
assignment. Do not run all specialists for every request or duplicate
investigations across roles.

| Requested work | Agent | Load a Skill only when relevant |
|---|---|---|
| Implementation, tests, integration, or a mixed task with no separable specialist scope | Ralph Loop Worker (`ralph-worker`) | `tdd` for behavior changes; `project-memory` for the coordinator's post-merge review |
| Code review of a changed branch or PR | `ralph-code-reviewer` | Existing read-only reviewer; not a second implementation worker |
| Diff-level security review or an explicit search for exploitable vulnerabilities | `ralph-security-reviewer` | Existing security reviewer; not an OWASP ASI posture audit |
| Fetch/rebase/worktree conflict triage, task status publication, or an authorized Git merge | `ralph-git-specialist` | `ralph-loop` only when acting in a Ralph iteration |
| Documentation drift, explicitly requested docs updates, codebase onboarding docs, or Copilot instructions | `ralph-docs-specialist` | `docs-sync-audit` for drift; `acquire-codebase-knowledge` only for explicit repository mapping; `copilot-instructions-blueprint-generator` only for an explicit instructions blueprint |
| Agent architecture, minimal multi-step Skill stack, or evaluation-gate design | `ralph-agent-design-specialist` | `agent-architecture` for architecture-only work; `agent-skill-stack` for a multi-step Skill workflow; `agentic-eval` for evaluation design |
| Explicit OWASP ASI Top 10 compliance or controls mapping | `ralph-asi-specialist` | `agent-owasp-compliance`; keep this read-only and separate from diff-level security review |

The ASI agent reports evidence and unknowns rather than certification.
Architecture and review agents return findings or a plan, not code. An
implementation worker makes behavior changes with TDD after the user has
requested implementation; do not let a read-only analysis role silently
write a fix. Prefer one agent for a task whose paths and verification are
inseparable; split only for an independent deliverable with disjoint
ownership.

## Dispatch and fallback

1. Confirm the named custom agent exists in `.github/agents/` for this
   workspace and is allowed by the Ralph Orchestrator's `agents:`
   frontmatter. Agent definitions alone do not change the pipeline: the
   Orchestrator must explicitly route to the selected specialist and permit
   that agent through its subagent allowlist. Keep Ralph Loop Worker and
   the existing read-only reviewers in that allowlist; do not add a
   competing coordinator or let the entrypoint dispatch specialists.
2. Allocate a small, exclusive edit scope and concrete expected output
   before invoking `agent/runSubagent`. Supply just the task prompt, exact
   branch/base, relevant paths, applicable Skill trigger, safety limits, and
   acceptance checks. Avoid pasting the whole repository or unrelated
   Skills into every prompt. One agent owns each shared file, even when
   specialists run alongside implementation workers.
3. Count only launched implementation workers in `workers=N`; specialists
   are not counted as implementation workers. Every launched specialist
   counts toward the Resource Manager's host limit alongside the router,
   Orchestrator, workers, and reviewers. Refresh the live-agent inventory
   and reserve a host slot before each `agent/runSubagent` call. Pass the
   exact `agent_id` and `reservation_id`; an execution-capable specialist
   activates its reservation before task work, heartbeats while active,
   and releases it when done. Read-only specialists cannot run the registry
   CLI. The Orchestrator must account for their live sessions through a
   current reservation or the complete observed-session inventory, and
   keep that accounting valid throughout the task. If their capacity
   cannot be verified, do not dispatch; do not grant `execute` solely for
   registry bookkeeping. Cancel an unclaimed reservation after a rejected
   launch.
   When capacity is full, queue or block the specialist; a general worker
   fallback also requires an available slot. Do not invent worker slots or
   claim a specialist ran just because its definition was discoverable.
   Report actual invocations and checks in the status records.
4. If a specialist, its Skill, or the `agent/runSubagent` capability is
   unavailable, use the general Ralph Loop Worker with the same relevant
   Skill and validation rules when that worker is authorized and capable.
   Otherwise report the blocker; do not skip mandatory security review or
   imply a missing review occurred. A fallback does not grant new tools or
   edit rights. Inherit the session model by default, and avoid pinning a
   model or raising reasoning/context settings without measured task-specific
   benefit.
5. Check the output against the task's acceptance criteria. Invoke a
   second specialist only for a distinct needed capability or concrete
   finding, not speculative parallel passes over the same files. Measure
   end-to-end latency, tokens/credits where observable, handoff count, and
   verified accuracy before claiming optimization; there is no measured
   speed or cost improvement merely from adding profiles.

Example: a bug fix with associated docs can stay with one general worker;
use the docs specialist only if a separable docs audit or update is
explicitly requested and it owns different paths. A requested OWASP ASI
audit uses the ASI specialist, not the diff-level security reviewer.

## Preserve edit and main ownership

The task ledger reserves an exclusive edit scope before any agent edits;
if another agent owns a path, wait for its recorded sign-out or scope
release. Each child works in its own branch/worktree and hands verified
commits to the parent. A specialist cannot mutate another worker's branch.

The authoritative main reservation is
`docs/agent-sync/main/ownership.json` on fetched `origin/main`. `main` is
checked out only for a status write or an authorized merge that needs that
checkout; routine refreshes use isolated worktrees and `git fetch origin`.
For each `STATUS` transaction, reserve main, write status-only paths, and
sign out immediately after the status commit. For `MERGE`, wait for the
current owner to release main; the branch owner performs an authorized PR
merge, verifies its actual remote result, then releases the reservation.
Releasing main does not sign out the separate task. No specialist may
force-push, steal a reservation, bypass branch policy, or claim completion
from a local commit or an open PR.
