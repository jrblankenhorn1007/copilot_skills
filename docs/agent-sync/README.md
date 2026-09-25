# Ralph Agent Sign-In and Sign-Out Ledger

`docs/agent-sync/` is the fast, shared coordination ledger for a live Ralph
run. Agents publish status-only commits directly to remote `main` so every
other agent can see who is editing what without waiting for a pull request,
review, task branch, or status worktree. This exception applies only to
`docs/agent-sync/**`; implementation and other project changes keep the
normal isolated-worktree and integration process.

The detailed Ralph records under `docs/ralph/` and the coordinator-owned
`docs/ralph-status.md` remain the durable iteration history and aggregate
index. The synchronization ledger is the live source for current agent
ownership, prompt, model configuration, and editing/sign-out state.
The [exclusive main ownership protocol](./main-ownership.md) at
`docs/agent-sync/main-ownership.md` separately governs every status
publication and authorized merge.

## Layout

```text
docs/agent-sync/
  README.md
  main-ownership.md
  main/
    ownership.json
  runs/
    <run-id>/
      agents/
        <agent-id>/
          status.json
          prompt.md
```

Use a stable run ID and a stable, run-scoped agent ID such as `coordinator`,
`worker-01`, or `worker-02`. Each agent is the sole writer of its own
`status.json` and immutable `prompt.md`; separate paths let agents publish
concurrently without editing a shared dashboard. Do not add a mutable
run-wide index: list the agent records under the run directory instead.
The canonical status path is
`docs/agent-sync/runs/<run-id>/agents/<agent-id>/status.json`.
The one repository-wide main sign-in is
`docs/agent-sync/main/ownership.json`. A task sign-in reserves its edit
paths, not the main checkout or ref. Releasing main after a status commit
does not sign out of the task or release its edit scope.

## Sign in before editing

The coordinator assigns a bounded task, stable run/agent/task IDs, and
exclusive edit paths before dispatch. Every agent, including the coordinator,
must sign in before editing and publish revision 1 to `origin/main` **before
its first task edit**. The status record captures:

- Run, task, worker, display name, revision, current state, reason, and UTC
  sign-in/update timestamps.
- The exact task prompt dispatched to the agent in `prompt.md` and its
  `prompt_sha256`. Redact secrets and private credentials before dispatch; the
  committed prompt must be the exact safe prompt the agent received.
- Harness, agent definition, runtime/session ID, model ID, reasoning effort,
  context tier/window, and observed context usage. Record unknown or
  unavailable fields as `null`, never as an assumed model default.
- Repository identity, implementation branch, actual task worktree path,
  base ref/SHA, worktree HEAD at sign-in, and exclusive edit-scope paths.
- Sign-out fields, initially null, for the implementation SHA, summary,
  checks, and next action.

Example current-state record:

```json
{
  "schema_version": 1,
  "run_id": "example-run-20260925",
  "agent_id": "worker-01",
  "worker_id": "worker-01",
  "worker_name": "worker-01 - status contract",
  "task_id": "document-agent-sign-in",
  "status": "IN_PROGRESS",
  "revision": 1,
  "started_at_utc": "2026-09-25T05:00:00Z",
  "updated_at_utc": "2026-09-25T05:00:00Z",
  "status_reason": "Starting the assigned status contract.",
  "prompt_path": "docs/agent-sync/runs/example-run-20260925/agents/worker-01/prompt.md",
  "prompt_sha256": "<sha256 of the exact prompt.md bytes>",
  "agent_profile": {
    "harness": "VS Code Copilot",
    "agent_definition": ".github/agents/ralph-loop.agent.md",
    "runtime_agent_id": null,
    "model_id": null,
    "reasoning_effort": null,
    "context_tier": null,
    "context_window_tokens": null,
    "context_usage_tokens": null
  },
  "git": {
    "remote_name": "origin",
    "repository": "owner/repository",
    "implementation_branch": "refs/heads/ralph/example-worker-01",
    "worktree_path": "/absolute/path/to/the/task-worktree",
    "base_ref": "refs/heads/ralph/example-parent",
    "base_sha": "<full parent base SHA>",
    "worktree_head_sha_at_sign_in": "<full checked-out SHA>",
    "edit_scope": ["src/example.py", "tests/test_example.py"]
  },
  "sign_in_at_utc": "2026-09-25T05:00:00Z",
  "sign_out": {
    "at_utc": null,
    "implementation_commit_sha": null,
    "summary": null,
    "checks": [],
    "next_action": null
  }
}
```

Set `status` to `IN_PROGRESS` when the sign-in is committed. Set the branch,
worktree, base, prompt, and edit scope to their actual values; the example's
placeholders are not valid run data.

## Publish status directly to remote main

Use the standard-library Python publisher from the task repository or any of
its worktrees:

```sh
python3 .github/skills/ralph-loop/scripts/publish_agent_sync.py \
  --repository /path/to/the/repository \
  --run-id example-run-20260925 \
  --agent-id worker-01 \
  --status-file /path/to/temporary/status.json \
  --prompt-file /path/to/temporary/prompt.md
```

`--prompt-file` is required at first sign-in and omitted for subsequent
revisions. Generate temporary input files outside the task tree so status
publishing does not dirty the implementation worktree. The publisher checks
the record identity, required metadata, UTC timestamps, prompt digest, and
monotonically increasing revision. The status commit changes only this
agent's `status.json` and, on first sign-in, `prompt.md`.

The publisher first atomically signs in to main for `STATUS` in a status-only
commit changing `ownership.json`. If another owner is signed in, it waits
up to 30 seconds by default (configurable with `--wait-seconds`, 0-120) and
reports a blocker rather than stealing the reservation. It then builds a
direct status commit to `refs/heads/main` with Git plumbing and a private
temporary index. **Sign out immediately after the verified status commit**:
the publisher automatically makes a final status-only release commit before
returning. Do not insert testing, review, or unrelated work between the
status commit and release. A repeated identical status is a no-op and
requires no main reservation.

No task branch or worktree is created for status publication; the publisher
does **not** switch a branch, touch the implementation index, or change code.
Concurrent fetches use isolated temporary refs rather than changing a shared
tracking ref. On a rejected push, it fetches the latest main, rereads the
owner, and retries up to five times. An out-of-order revision, foreign owner,
failed release, or continuing race is reported rather than overwritten. The
JSON result includes the status commit, main sign-in and sign-out commit SHAs,
and the final fetched remote-main tip. Keep it as transaction evidence; a
status commit without verified main sign-out is not a successful transaction.

## Reserve main for an authorized merge

After merge authorization, reserve main before submitting the merge. Use the
same publisher from an isolated worktree, without checking out `main` unless
the merge procedure actually needs that checkout:

```sh
python3 .github/skills/ralph-loop/scripts/publish_agent_sync.py \
  --repository /path/to/the/repository \
  --repository-id owner/repository \
  --run-id example-run-20260925 \
  --agent-id worker-01 \
  --main-action acquire --operation MERGE
```

Save the returned `token` for this transaction. If a local main checkout is
needed, pass `--main-worktree /path/to/main-checkout`; the tool rejects a
dirty, detached, or unrelated checkout. Wait for the existing main owner
to sign out rather than changing its checkout or forcing its remote ref.
After the authorized merge is verified on fetched `origin/main`, release
main promptly with the actual resulting merge SHA:

```sh
python3 .github/skills/ralph-loop/scripts/publish_agent_sync.py \
  --repository /path/to/the/repository \
  --repository-id owner/repository \
  --run-id example-run-20260925 \
  --agent-id worker-01 \
  --main-action release --main-token <token-from-acquire-result> \
  --outcome MERGED --result-commit-sha <verified-remote-merge-sha>
```

For an accepted merge queue submission, release promptly with `--outcome
QUEUED` and no result SHA; the queue controls its later remote merge.
`--repository-id` must match the task's canonical `owner/repository` identity
exactly. If an action or release fails, keep the owner record and investigate
using the [recovery procedure](./main-ownership.md#merge-transaction-and-recovery);
never infer release from a timeout or another task's sign-out.

Read the current run's ledger without checking out main:

```sh
git fetch origin refs/heads/main:refs/remotes/origin/main
git ls-tree -r --name-only origin/main \
  docs/agent-sync/runs/example-run-20260925/agents
git show origin/main:docs/agent-sync/runs/example-run-20260925/agents/worker-01/status.json
```

Refresh this view before dispatch, before choosing or changing edit scope, at
coordination boundaries, and before integration. The coordinator checks
active scopes and branches for collisions before assigning work. If scopes
overlap, serialize the assignments or give the shared paths to one agent.
An abandoned-looking record is not automatically released: confirm that its
agent has stopped, then publish a status transition before reassigning those
paths.

## Keep status updates current and sign out

Before changing task scope, mark a blocker, or stopping work, refresh remote
main, increment `revision` by exactly one, update the current status/reason
and timestamp, then publish the new snapshot. Use `BLOCKED` when work cannot
proceed, but retain the record and owned paths until the coordinator confirms
that ownership is released.

When the agent stops editing, set `sign_out.at_utc`, implementation commit
SHA (when one exists), concise summary, exact check commands/results, and
next action. Use `AWAITING_MERGE` when finished work awaits normal
implementation integration; use `COMPLETE` only after the coordinator
verifies that integration. A canceled or failed assignment also signs out
with its disposition and any remaining safe next action. A subsequent
assignment or retry gets a new run/agent record; never reuse an old record to
hide history.

## Scope, privacy, and failure rules

- The no-PR/no-review/direct-main exception is strictly for one agent's
  `docs/agent-sync/**` metadata. It does not allow code, tests, or other docs
  to be committed directly to main or to bypass the parent/child and PR
  process.
- Direct status publishing requires the configured Git identity,
  authenticated `origin`, and repository policy to permit these status-only
  commits. Never weaken branch rules, use an admin bypass, or force-push. If
  the direct push is denied, report `BLOCKED`; do not silently fall back to a
  PR or claim that remote sign-in/sign-out succeeded.
- Before integration, implementation agents still synchronize/rebase the
  assigned code branch as required, rerun checks after a rebase, and verify
  each merge. A status commit is not an implementation commit or an
  integration signal.
- Never store credentials, access tokens, private keys, or secret-bearing
  command output. The prompt is committed to the repository: dispatch a
  redacted safe prompt and store exactly that prompt. Do not record private
  user data that is not needed to coordinate the task.
- Model and context data describe the session that actually ran. Use `null`
  when the host does not expose a value and explain unavailable telemetry in
  `status_reason` or an `unavailable_fields_reason`.
- Do not put secrets in commit messages, paths, agent IDs, or status values.
  Status files should remain concise and machine-readable; detailed test and
  decision history belongs in the existing per-agent Ralph records.
