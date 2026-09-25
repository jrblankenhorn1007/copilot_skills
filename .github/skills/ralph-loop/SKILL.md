---
name: ralph-loop
description: Use for Ralph-style development runs; coordinate configurable workers, capture categorized lessons, and verify remote-main integration.
---

# Ralph Loop

Use this skill to run one bounded outer software-development iteration. It
guides project discovery, worktree isolation, verification, and integration.
It does not replace the active project's plan, acceptance criteria, runner,
tests, status protocol, or decision history; read and follow those sources.

## First-run orchestration

For multi-agent work, the first top-level Ralph Loop invocation is the
orchestrator, not an implementation worker. Its first run plans and dispatches
the configured workers before taking on any worker assignment; it does not
count toward `workers=N`. The default is two workers. If fewer than two useful,
independent assignments are ready, launch only the available work and record
why; never invent or duplicate assignments to meet the default.

Configure the orchestrator's model and supported parameters for the initial
session, and configure worker defaults or per-worker overrides at dispatch.
See [multi-agent orchestration](./references/multi-agent-orchestration.md) for
the run configuration and [Copilot agent selection and model controls](./references/copilot-cli-usage.md)
for applying it in supported harnesses.

## Refresh repositories and instructions on every iteration

At the beginning of every Ralph iteration—including the orchestrator, each
worker dispatch or re-dispatch, and retries—synchronize the skills source and
active project before planning, dispatching work, or editing:

1. Identify the canonical `jrblankenhorn1007/copilot_skills` checkout and the
   active project's Git repository. Verify each checkout by its configured
   Git remote, not its directory name alone. If both are the same repository,
   update it once.
2. In each distinct repository, locate its clean, attached primary integration
   worktree (normally `main`) and verify that it tracks the intended upstream.
   From that worktree, run `git -C <integration-worktree> pull --ff-only`.
   Never pull in an iteration or feature worktree. If a checkout cannot be
   identified, is dirty or detached, tracks the wrong upstream, or cannot be
   fast-forwarded, stop and report the blocker. Preserve all changes; do not
   stash, reset, or silently continue with stale instructions.
3. After the pulls succeed, reopen the current Ralph Loop skill and (when
   used) agent definition from the refreshed `copilot_skills` checkout. Re-read
   the references needed for the current mode, applicable task skills
   (including TDD before behavior changes, Project Memory for post-merge
   review, and any other skills triggered by the task), and the active
   project's plan, prompt or runner, progress, status, decision, and local
   instruction files from its refreshed checkout. Read the files again even
   if their contents are already in the conversation or preloaded in the
   agent context. Canonical skills complement; they do not replace,
   project-specific requirements.

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
   the integration checkout is detached, or its worktree has uncommitted
   changes, preserve the current state and report the blocker.
4. Check that any project runner supports the fresh-worktree and verified
   remote-merge lifecycle below. Do not invoke a runner that assumes an
   in-place branch, pushes before integration, or skips remote verification.

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

A worker remains `AWAITING_MERGE` until the coordinator verifies integration
and completes the required post-merge memory review (including any warranted
memory follow-up). Only then may its leaf and dashboard status become
`COMPLETE`; keep both records synchronized at that transition. Keep branch
decision indexes and per-agent/PR decision records at the `docs/decisions/`
paths above.

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

## Iteration workflow

1. Perform one coherent implementation iteration per invocation. Create a
   fresh worktree and unique branch from the latest remote `main` before
   editing, following the project's location and naming conventions. Otherwise
   use:

   ```sh
   git worktree add -b <branch> <path> origin/main
   ```

   Do not reuse or remove another task's worktree or branch. Make all changes,
   tests, and commits for the iteration in the new worktree.
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
5. Complete the implementation commit and any required runner-managed status
   commit on the iteration branch before integration. Do not amend commits or
   use destructive Git operations.
6. Publish the iteration branch as needed and use the repository's remote
   merge process to integrate it into `origin/main`. An open pull request,
   pushed branch, or local merge is not completion. Fetch `origin` again and
   verify the resulting merge SHA is reachable from remote `main`. For squash
   or merge-queue flows, verify the merge result rather than requiring the
   iteration commit itself to remain an ancestor.
7. After the implementation content is merged and verified on fetched
   `origin/main`, perform a memory review using the
   [Project Memory skill](../project-memory/SKILL.md). Keep reusable lessons
   in the project's categorized memory store. If a memory change is warranted,
   make it on a fresh follow-up branch from the latest `origin/main`, integrate
   it through the same remote merge process, and verify its merge before
   completing the iteration. This is part of the same iteration, not a new
   iteration, and does not trigger another memory review. Never write directly
   to `main` or amend the merged implementation branch. If no durable lesson
   emerged, leave memory unchanged and record that outcome in the active
   progress or status record when one exists.
8. If validation, implementation merge, memory update, or remote verification
   is blocked, preserve the affected worktree and branch and report the
   blocker. Remove only this iteration's worktree and branch, and only after
   all required merges are verified and when the project's workflow permits
   cleanup.
9. Follow the active project's exact continuation, blocked, and completion
   markers, and emit them only when their conditions are met. Never report
   completion before the implementation merge and any required memory merge
   are verified on fetched remote `main`.

## Completion reporting and branch decision records

Start the final user-facing response with exactly one of these status lines:

```text
Task completed: YES
```

or

```text
Task completed: NO
```

Use `YES` only after the requested outcome, required checks, integration, and
remote verification are complete. Follow it with a concise outcome, relevant
test results, and verified merge SHA. Use `NO` when work remains blocked or
incomplete, then state the unresolved blocker and the next actionable step.
Do not imply success if required checks or remote-main verification are
missing.

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
main moves. See the
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
- [Copilot agent selection and model controls](./references/copilot-cli-usage.md).
- The [SuperCollider AI Music Agent Ralph prompt](./references/ralph-loop.md)
  is specific to `dj_maxxed_beats`; its product requirements and file names do
  not apply to other projects.
