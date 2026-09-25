---
name: ralph-loop
description: Use for Ralph-style development runs and project-specific Ralph prompt generation or translation; coordinate configurable workers, capture categorized lessons, and verify remote-main integration.
---

# Ralph Loop

Use this skill to run one bounded outer software-development iteration. It
guides project discovery, worktree isolation, verification, and integration.
It does not replace the active project's plan, acceptance criteria, runner,
tests, status protocol, or decision history; read and follow those sources.

## OpenCode runtime and first-run orchestration

OpenCode is the default Ralph Loop runtime. Start the repository's primary
profile from the project root with a provider/model returned by
`opencode models`:

```sh
opencode run --agent ralph-loop --model provider/model-id \
  "Coordinate one bounded Ralph Loop task"
```

The profile is defined in `.opencode/agents/ralph-loop.md`; it follows this
skill as the source of truth. Its first top-level invocation is the
coordinator, not an implementation worker. Validate `workers=N` as a
positive integer, defaulting to two. The coordinator plans and dispatches
ready workers before taking on any worker assignment; it does not count
toward `workers=N`, but it does count toward the live total-agent limit.
Before task work, register the coordinator with the Resource Manager, reserve
each child slot before dispatch, and have each worker activate its reservation
before work. The effective worker count is bounded by ready assignments and
the Resource Manager's available slots. If capacity is full or cannot be
measured, dispatch no workers and queue or serialize the work; never bypass
the limit. If fewer than two useful, independent assignments are ready,
launch only the available work and record why.

Create a fresh child worktree and branch for each implementation worker, then
start a separate OpenCode session rooted at that worktree:

```sh
opencode run --dir <child-worktree> --agent ralph-loop-worker \
  --model provider/model-id "<bounded worker assignment>"
```

Replace the placeholders before running the command. OpenCode's Task
subagents inherit the current session's worktree; they do not create Git
worktrees. Do not use them for implementation assignments that require
child-worktree isolation. Use the Task tool only for the named, read-only
PR reviewers. Do not add `--auto` to a Ralph session.

Pass an explicit `--model provider/model-id` to each session; use `--variant`
only when the selected provider/model supports it. Apply worker-specific
model settings at launch rather than claiming an unsupported context or
reasoning option was applied.

Install and authenticate OpenCode before starting model-backed work; follow
the [OpenCode setup guide](./references/opencode-setup.md). The
[multi-agent orchestration guide](./references/multi-agent-orchestration.md)
defines worker sessions, model settings, worktree isolation, and integration.
Follow the [Resource Manager skill](../resource-manager/SKILL.md) for the
shared local registry and dynamic hardware-based capacity policy.
The Copilot CLI profile and
[Copilot CLI compatibility guide](./references/copilot-cli-usage.md) remain
available for users who explicitly choose that legacy runtime, but are not
the default workflow.

The currently deployed Ralph Loop profile is both the top-level coordinator
and the general implementation-worker profile. Route only relevant, bounded
Git, documentation, agent-design, or OWASP ASI assignments to the optional
specialists following the
[conditional specialist routing guide](./references/skill-aware-routing.md).
Specialists consume shared host capacity but do not inflate `workers=N`;
preserve the general worker fallback and the existing independent PR review
gates. The separately proposed Orchestrator and Worker profiles are not yet
on `origin/main`; do not delegate to them as if they were deployed.

## Parent and child worktrees

After the per-iteration refresh and Git identity/authentication preflight,
fetch `origin` and create a dedicated parent worktree and unique parent branch
from the exact fetched `origin/main` SHA. Run the top-level Orchestrator
session with the user's prompt in that parent worktree, not in the
integration checkout.

Each worker receives a fresh, unique child worktree and branch based on the
parent branch and exact parent base SHA supplied by the coordinator. Workers
do not create child branches from `origin/main` or merge directly to it. Keep
worker path ownership disjoint. The coordinator integrates one completed
child branch at a time into the parent and verifies each integration before
proceeding to the next worker. Only after all child work has been integrated
and the parent passes its acceptance checks may the coordinator publish and
merge the completed parent branch to `origin/main`. Fetch `origin` and verify
the resulting parent merge SHA there; a child commit or child-to-parent merge
is not remote-main completion.

Never delete an unmerged branch. After a child's merge into the parent is
verified, the coordinator may remove its worktree with
`git worktree remove <child-worktree>` and delete its local branch with
`git branch -d <child-branch>`. Delete a published child ref only after that
verification and if repository policy permits. Keep the parent worktree and
branch until the completed parent merge has been fetched and verified on
`origin/main`; only then may the coordinator remove the parent worktree and
use `git branch -d` for its branch. Delete a published parent ref only after
that verification and if repository policy permits. Do not use force-delete
operations.

## Refresh repositories and instructions on every iteration

At the beginning of every Ralph iteration—including the orchestrator, each
worker dispatch or re-dispatch, and retries—synchronize the skills source and
active project before planning, dispatching work, or editing:

1. Identify the canonical `jrblankenhorn1007/copilot_skills` checkout and the
   active project's Git repository. Verify each checkout by its configured
   Git remote, not its directory name alone. If both are the same repository,
   fetch it once.
2. In each distinct repository, run `git fetch origin`, verify its remote
   `main` ref, and record the exact fetched `origin/main` SHA. Locate the
   attached primary integration worktree with `git worktree list --porcelain`
   for later merge use, but do not pull, check out, or edit shared main to
   refresh instructions. A dirty, diverged, or detached integration checkout
   is not a task workspace: preserve it and continue read-only/isolated
   work, but do not use it for a checkout-based merge. Stop if the remote
   main ref or required current instructions cannot be verified. Never
   stash, reset, or clean another agent's checkout.
3. Reopen the current Ralph Loop skill and (when used) agent definition from
   the fetched `copilot_skills` commit, using `git show` or an isolated
   worktree at that SHA. Re-read the references needed for the current mode,
   applicable task skills (including TDD before behavior changes, Project
   Memory for post-merge review, and any other skills triggered by the task),
   and the active project's plan, prompt or runner, progress, status,
   decision, and local instruction files from its fetched commit. Read the
   files again even if their contents are already in the conversation or
   preloaded in the agent context. Canonical skills complement; they do not
   replace project-specific requirements.

## Required setup

1. After completing the per-iteration refresh above, read the active project's
   implementation plan, Ralph prompt or runner,
   progress log, current status snapshot, decision log, and applicable local
   instructions. Read the project's memory index and relevant categories when
   available using the [Project Memory skill](../project-memory/SKILL.md), and
   validate those lessons against current sources. Treat the active project's
   artifacts as the source of truth for scope, filenames, runner behavior, and
   completion markers.
2. Confirm the requested work advances a clear acceptance criterion. If there
   is no active task or the requested scope is unclear, ask for direction
   rather than inventing a project goal.
3. Fetch the configured remote and identify its latest `main` ref and the
   worktree where that branch is checked out. If remote `main` is unavailable,
   report the blocker. Preserve a detached, dirty, or diverged integration
   checkout; its owner must resolve it before a checkout-based merge, but
   independent work starts from the fetched remote SHA in a fresh worktree.
4. Check that any project runner supports the fresh-worktree and verified
   remote-merge lifecycle below. Do not invoke a runner that assumes an
   in-place branch, pushes before integration, or skips remote verification.

## Generating or translating a project-specific Ralph prompt

When asked to create or translate a project-specific Ralph prompt, inspect
the user's task, the active project's current project plan and current Ralph
prompt or runner, applicable project instructions, the canonical skill catalog
(`copilot_skills/.github/skills/`), and the project-local
`.github/skills` catalog when it exists. Read candidate skill descriptions
and triggers; select a skill only when those descriptions or triggers match
the task or a required Ralph workflow step. Base the selection on current
evidence, not a skill's name alone. Do not guess a stack. Do not reuse a
static list for every project, and do not list every available skill. Do not
invent project criteria when a plan or current prompt is absent.

Verify that a project-local skill path exists before linking it. When the same
skill appears in both catalogs, list each skill only once: link the active
project's copy when it is the controlling version; otherwise link the
canonical source. If both links are needed to explain distinct guidance, put
them in the same entry rather than duplicating the skill.

The generated prompt itself must contain an explicit `## Relevant skills`
section as prompt content, not only as generator metadata. List each selected
skill's name, canonical or project-local path or link, and the condition or
reason it applies; replace any template placeholders with verified values.
Always include Ralph Loop for the development workflow, include TDD for
behavior changes, and include Project Memory for the required post-merge
review. Domain-specific skills may be included only when their descriptions
or triggers match the actual task. Do not duplicate a skill. Do not list an
unavailable local skill.

## Active-project Ralph documentation and status

Resolve these paths from the active project's repository root, not from the
canonical skills checkout. Keep generated Ralph run, status, progress, and
decision records inside that repository's `docs/` folder; do not create or
update root-level Ralph status or progress files. Use this layout:

```text
docs/
  ralph-status.md
  ralph/<branch-slug>/agents/<agent-id>/
    status.md
    progress.md
  decisions/<branch-slug>/
    README.md
    agents/<agent-id>/pr-<number>.md
```

Normalize the exact Git branch name to lowercase and replace `/` with `-` to
form `<branch-slug>`. Use the stable run-scoped `<agent-id>` assigned by the
coordinator (for example, `worker-01`), not the display name or runtime
agent/session ID.

The coordinator exclusively owns `docs/ralph-status.md`. It must surface every
branch/agent folder under `docs/ralph/`, linking that folder's `status.md` and
`progress.md` and showing its current summary. Each worker owns the leaf
`status.md` and `progress.md` in its assigned branch/agent folder: keep
`status.md` current and append dated loop evidence to `progress.md`. At every
loop or worker-state transition, the worker reports the updated leaf records
and the coordinator refreshes the affected dashboard entry in the same
coordination cycle. Keep the leaf status, progress summary, and dashboard
entry consistent on the run/worker state, iteration, branch, checks,
blockers, next action, and merge/memory-review state; retain dashboard entries
for unaffected branch/agent folders. Workers never edit the aggregate
dashboard.

Schema-version-2 current reports include a branch-local `resource_usage`
object in each worker's `status.md`; the coordinator mirrors that exact object
into the matching `branch_agent_index` record in the same status-sync cycle.
`time_spent_seconds` is elapsed wall-clock time from `started_at_utc` to the
report's `updated_at_utc`, not active coding time. Record provider-reported
token counters only; use the documented `REPORTED`, `PARTIAL`, or
`NOT_REPORTED` status and null unavailable counts, never estimates or
monetary cost estimates. See the
[per-branch time and token usage contract](./references/multi-agent-status.md#per-branch-time-and-token-usage)
for fields, cached-input handling, and legacy-record rules.

For every PR-backed iteration, the branch owner is the merge actor. In a
multi-agent run, the coordinator authorizes one worker PR at a time after
reviewing its sign-off and checks; the worker performs the remote merge of its
own PR after coordinator authorization, using its own existing authentication
through the configured GitHub CLI (`gh`) or supported GitHub integration/MCP
tools. Do not rely on coordinator credentials. The coordinator verifies the
remote merge and performs the post-merge memory review, but does not merge a
worker's PR on its behalf. Follow the
[worker-owned PR merge guide](references/worker-pr-merging.md).

After a worker's child-to-parent merge is verified on the current parent
branch, that worker may become `COMPLETE`; the overall run remains
`IN_PROGRESS` until final parent-to-main verification and the coordinator's
post-merge memory review (including any warranted memory follow-up). For a
single-branch iteration, the worker remains `AWAITING_MERGE` until its final
remote-main merge and required post-merge memory review are complete. Keep
each leaf and dashboard status synchronized at the applicable transition,
and keep branch decision indexes and per-agent/PR decision records at the
`docs/decisions/` paths above.

## Independent pre-merge PR review

For every PR-backed iteration, after branch-owner sign-off and before any
merge action, launch an independent **Ralph Code Reviewer**. Also
launch a **Ralph Security Reviewer** when the diff touches authentication or
authorization, untrusted input, secrets or sensitive data, cryptography,
process execution, external boundaries, dependencies, or security
configuration. Reviewers follow
[`.github/skills/ralph-pr-review/SKILL.md`](../ralph-pr-review/SKILL.md), are
separate from the author, and are read-only: they report findings but do not
edit the branch, apply fixes, or merge.
Complete review before coordinator authorization for a worker-owned child PR
and before the coordinator merges its own parent PR.

Bind every completed review pass to the exact full base and head commit SHAs.
Before authorizing a merge, compare both SHAs with the PR's current base and
head. If either differs, the report is stale and blocks authorization until a
fresh review is complete. A clean agent report is evidence, not a guarantee
of correctness and not a substitute for required CI, branch protection, or
human approvals.

Review for design, intended functionality and edge cases, complexity,
correctness, and appropriate tests. Ground findings in the changed code and
available project context; distinguish actionable defects from suggestions.
Personal preference, cosmetic style, and nits are nonblocking unless they
violate an applicable written project standard. Use structured,
evidence-bounded findings and an adversarial challenge to check that each
finding is real and relevant. Do not use unverified numeric scoring or grant
reviewers broad autonomous fixing.

Allow at most **2 completed review rounds per branch/PR**: one initial review
and, when needed, one follow-up review after the author agent acts on the first
report. A round is one complete pass on an exact base/head pair; the first
completed reviewer report counts as round 1, and any required code and
security reports for that pair belong to the same pass. A clean initial
report may proceed through the normal merge gates without an unnecessary
follow-up. After round 2, the author agent acts on the follow-up report alone,
records its final action and non-empty rationale, and does not dispatch a
third reviewer pass. The available actions are `FIX_MANUALLY`,
`ACCEPT_FINDINGS_AND_REQUEST_MERGE`, `ESCALATE_FOR_HUMAN_REVIEW`, and `CLOSE`.
Accepting findings requests normal merge consideration; it does not waive CI,
branch protection, or required human approvals. A later base or head change
still makes the report stale. If the author agent changes the head after the
follow-up, do not merge on that stale report; obtain any required human review
through the normal process, not a third agent review on the same branch/PR.

For the repository's coordinator-managed fast-forward path with no PR, do not
launch reviewers or change the integration process; record
`review.status: NOT_APPLICABLE`. See the
[multi-agent orchestration](./references/multi-agent-orchestration.md),
[status schema](./references/multi-agent-status.md), and
[worker-owned PR merge guide](./references/worker-pr-merging.md) for the
review gate and status fields.

Before editing an assigned scope, use the
[agent-sync ledger](../../../docs/agent-sync/README.md) to publish the task
sign-in on remote main. The task record owns edit paths, not the main checkout
or ref. If direct status publication is rejected with a verified GH013 message
that explicitly requires GitHub API/UI merging, use the ledger's
[protected-main status-PR recovery](../../../docs/agent-sync/README.md#protected-main-status-pr-recovery);
do not retry a forbidden direct write or treat an unmerged PR as published
sign-in. Keep the task unedited until the first status record is visible on
fetched `origin/main`. Other authentication, lease, or permission failures
remain blockers unless the repository documents an authorized recovery.

For direct status commits and authorized merges, follow the separate
[exclusive main ownership protocol](../../../docs/agent-sync/main-ownership.md):
atomically sign in to `docs/agent-sync/main/ownership.json` for `STATUS` or
`MERGE`; wait for the existing owner to sign out instead of using main. If a
verified GH013 denial explicitly requires API/UI merging, use the matching
protected-main recovery in the ledger and ownership protocol; do not retry a
forbidden direct write or bypass an active owner. The status publisher must
sign out immediately after verifying its status commit, without signing out
of the task or releasing its edit scope. For a direct/no-PR merge, release
promptly after remote verification or queue submission. Never report success
if a required main release cannot be verified.

## Git identity and authentication

Before creating an iteration branch or editing files, verify the configured
commit identity and remote read access:

```sh
git var GIT_AUTHOR_IDENT
git var GIT_COMMITTER_IDENT
git fetch origin
```

If either identity is missing or incorrect, stop before editing and report
that the intended Git `user.name` and `user.email` must be configured. Do not
invent an identity, override the author, or change shared Git configuration.
Use only authentication already configured for the session, such as the
platform credential helper, an SSH agent, or the host's GitHub integration.
Never ask the user to paste credentials, expose or inspect credential values,
embed a token in a remote URL or command, or write credentials to a file. Do
not run sign-in/setup commands or change remotes or credential configuration
without the user's explicit approval.

A successful fetch proves read access only; it does not establish permission
to publish a branch or merge it. Test write access by publishing the actual
iteration branch through the repository's normal process, and test merge
permission through its required PR, review, or merge-queue process. A dry-run
or local commit is not proof of either permission. If publishing or merging
fails because of authentication or repository policy, preserve the worktree
and branch, report the operation and sanitized error, and stop. Do not guess
credentials, repeatedly retry, force-push, or bypass branch protection by
writing directly to `main`.

## Git and GitHub repository operations

Never open, navigate, or automate a browser for Git or GitHub repository
operations. Use the Git CLI (`git`) for local repository operations—status,
diff, fetch/pull, branch/worktree, rebase, commit, and push. Use the configured
GitHub CLI (`gh`) or supported GitHub integration/MCP tools for pull requests,
checks, reviews, and merges. If the required CLI or integration is unavailable
or not authorized, report a blocker; do not fall back to a browser. Continue to
follow the existing Git identity and authentication rules.

## Iteration workflow

1. Perform one coherent implementation iteration per invocation. The
   coordinator creates the parent worktree and branch from the exact fetched
   `origin/main` SHA; each worker creates a fresh child worktree and branch
   from its assigned parent base. Follow project conventions for unique
   worktree paths and branch names. Do not reuse or remove another task's
   worktree or branch. Make all changes, tests, and commits only in the
   assigned worktree.
2. For behavior changes, follow the project's TDD requirements and the
   [TDD skill](../tdd/SKILL.md): write and run the narrowest relevant failing
   test first, implement to Green, then refactor with targeted checks passing.
   A documentation-only change does not require fabricated behavior tests;
   use the repository's available documentation and diff checks instead.
3. Run the narrowest relevant checks and inspect the resulting diff. Record
   exact Red, Green, and refactor commands and results, plus unverified
   platforms or environment gaps, in this branch/agent's
   `docs/ralph/<branch-slug>/agents/<agent-id>/progress.md`. For a
   documentation-only change, do not fabricate a TDD Red phase.
4. Keep this branch/agent's `status.md` and `progress.md` current for each
   loop, and coordinate the aggregate-dashboard update described above. Keep
   append-only decision history in `docs/decisions/<branch-slug>/`; preserve
   runner-owned fields and do not create Ralph run records outside `docs/`.
5. Complete each worker's implementation commit and any required
   runner-managed status and decision-record commits before integration. Do
   not amend commits or use destructive Git operations. The coordinator
   integrates one completed child branch at a time into the parent; workers
   never merge child branches directly to `origin/main`. If a child-to-parent
   PR is part of the repository's normal process, the coordinator authorizes
   it and the branch-owning worker performs its own PR merge with its existing
   authentication. The coordinator does not merge a worker PR on the worker's
   behalf. Verify each worker-to-parent merge before proceeding.
6. Only the completed parent branch goes through the repository's normal
   remote merge process to `origin/main`. Use a PR or merge queue when
   required; never bypass branch protection with a direct push. An open PR,
   pushed parent branch, or child-to-parent merge is not final completion.
   Wait for the parent merge to complete, fetch `origin`, and verify the
   resulting merge SHA on remote `main`. For squash or merge-queue flows,
   verify the parent merge result rather than requiring the parent
   implementation commit itself to remain an ancestor.
   Reserve main for the authorized merge transaction; if the reservation's
   status-only commit invalidates strict branch checks, release it and
   report the repository-policy blocker instead of bypassing those checks.
7. Only after the final parent-to-main merge is verified on fetched
   `origin/main`, invoke the dedicated
   [Project Memory Update agent](../../agents/project-memory-update.agent.md)
   exactly once with the coordinator report, its own `memory_handoff`, every
   worker's `memory_handoff`, and their source paths. The updater independently
   verifies the implementation merge and reviews the active project's
   categorized memory. Do not invoke it after a child merge or before final
   verification; if a required handoff is missing, report a blocker rather
   than filling gaps. Workers never edit shared memory. If the updater finds a
   durable, evidence-backed lesson, it creates a fresh follow-up branch from
   the latest `origin/main`, uses the same remote merge process, and verifies
   that merge before completing the overall run. A memory-only follow-up
   belongs to the same parent iteration and does not trigger another review.
   Never write directly to shared `main` or amend an already merged branch.
   If no durable lesson emerged, leave memory unchanged and record the
   updater's `NO_UPDATE` outcome in the active progress or status record.
8. If child-to-parent integration, the parent-to-main merge, a memory update,
   or remote verification is blocked, preserve the affected worktree and
   branch and report the blocker. Remove a child worktree and branch only
   after its parent merge is verified; remove the parent worktree and branch
   only after its remote-main merge is fetched and verified. Follow the
   repository's PR/remote-ref cleanup policy; never delete an unmerged branch
   or force-remove a worktree.

### Capacity-blocked post-merge memory review

Capacity denial is pending work, not task completion. Keep the run `BLOCKED`
and `memory_review_status: PENDING`; preserve all handoffs and record the
specific capacity blocker and next action. Do not substitute coordinator
self-review or report `NO_UPDATE` before the updater completes its review.
Continue safe non-agent work, but do not busy-poll or dispatch without a
reservation. If no safe work remains, use `ask_user` to ask the user for a
capacity remedy and wait with the run still blocked.

On every user resume, refresh the complete live-session inventory and current
Resource Manager status. If capacity remains unavailable, preserve the same
pending gate and next action. Otherwise atomically reserve a slot before
invoking the updater exactly once with all required handoffs. Do not call
`task_complete` or emit `RALPH_COMPLETE` while the memory review is pending;
the run becomes complete only after the updater reports a valid outcome and
any required memory merge is verified on fetched `origin/main`.

9. Follow the active project's exact continuation, blocked, and completion
   markers, and emit them only when their conditions are met. Never report
   completion before the parent merge and any required memory merge are
   verified on fetched remote `main`.

## Status-first run reporting and branch decision records

Lead every interim and final Ralph run report with the explicit overall run
state. List every assigned agent with its exact current status and next
action; include queued workers and agents awaiting integration, not only
currently active workers.

Use `IN_PROGRESS` while authorized work, review, checks, coordinator tasks, or
integration can still proceed. Use `BLOCKED` only when the run cannot advance
without external intervention; an individually blocked agent does not block
the run when other work can continue. Use `COMPLETE` only after all assigned
acceptance criteria and checks pass, all required worker-to-parent and
parent-to-main merges are verified, and the post-merge memory review and any
warranted follow-up merge are complete. A child merge or published branch
alone does not make the run complete. Do not substitute a binary
task-completion verdict for the run state and agent roster. Follow the
[status-first multi-agent reporting contract](./references/multi-agent-status.md)
for report structure and state meanings.

Report only unresolved blockers as failures. If a command, test, authentication
step, rebase, or merge attempt fails but the issue is resolved within the
iteration, record its sanitized symptoms, resolution, and successful
verification in the branch decision record instead of presenting it as an
unresolved failure in the final response. Do not omit or soften a blocker that
still prevents completion.

Create a version-controlled decision record for every iteration branch under
`docs/decisions/<branch-slug>/`. Normalize the exact branch name to lowercase
and replace `/` with `-` for `<branch-slug>`; record the exact branch ref in
the folder's `README.md`. Under that folder, keep a separate log for each
agent and pull request at
`agents/<agent-id>/pr-<number>.md`. If the repository's normal integration
expects a PR but its number is not assigned yet, use
`agents/<agent-id>/pr-pending.md`. If the normal integration does not open a
PR, use `agents/<agent-id>/pr-not-opened.md` and record why. When a PR number
is assigned, move a pending record to the numbered PR file and update the
branch index before merging.

For each agent/PR record, capture the branch, base and implementation commit
SHAs, agent and runtime ID when available, PR number/URL or why none was
opened, and decisions with context, alternatives, rationale, and consequences.
Log recovered failures with a sanitized diagnostic, resolution, and passing
verification; keep unresolved blockers clearly separate. Never record
credentials, tokens, or raw secret-bearing command output. Update the branch
index with links to every agent/PR record. The agent responsible for a branch
maintains its records and commits them with that branch before integration;
the coordinator checks the records alongside the branch's tests and diff.

## Worker status and sign-off

When the first top-level run delegates work, the coordinator owns
`docs/ralph-status.md` and records every worker's individual iteration,
sign-off, and remote merge verification there. The dashboard indexes every
branch/agent leaf folder; workers update only their assigned `status.md` and
`progress.md` and send the coordinator the exact changes and evidence needed
to refresh its entry. Workers use fresh worktrees and branches, refresh from
`origin/main` before starting and before integration, and rebase/retest if
main moves. A child worker records the exact parent base SHA;
the parent records its fetched `origin/main` base and remote merge evidence.
If the parent changes while child work is in flight, coordinate a rebase or a
fresh child branch from the updated parent and rerun checks before integration.
The coordinator serializes refreshes of any shared integration worktree and
re-syncs the parent with `origin/main` before its final integration. See the
[multi-agent orchestration](./references/multi-agent-orchestration.md) and
[multi-agent status](./references/multi-agent-status.md) references for the
split-plan, worker configuration, synchronization, and attestation contract.

Keep this outer development loop distinct from any in-product generation or
sampling loop. When the product has such a loop, follow its project-specific
requirements for user initiation, bounds, stoppability, isolation, and
confirmation before applying results.

## References

- [Test-Driven Development](../tdd/SKILL.md) for behavior-changing code work.
- [Multi-agent orchestration](./references/multi-agent-orchestration.md) for
  splitting a project into independent worker assignments.
- [Multi-agent status snapshots](./references/multi-agent-status.md) when a
  Ralph run delegates work to multiple agents.
- [OpenCode setup](./references/opencode-setup.md) for installation,
  authentication, model selection, and Ralph profiles.
- [Copilot CLI compatibility](./references/copilot-cli-usage.md) for the
  optional legacy runtime.
- The [SuperCollider AI Music Agent Ralph prompt](./references/ralph-loop.md)
  is specific to `dj_maxxed_beats`; its product requirements and file names do
  not apply to other projects.
