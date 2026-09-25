# Exclusive main ownership

The task sign-in under `docs/agent-sync/runs/` records who owns an edit scope.
It does **not** reserve the shared `main` checkout or `refs/heads/main`. Main
ownership is a separate, short-lived transaction. A task may remain
`IN_PROGRESS` or `BLOCKED` after its main transaction ends.

## When main may be used

- Do ordinary development, tests, research, and branch rebases in isolated
  worktrees. Refresh instructions with a read-only `git fetch origin` and the
  exact fetched `origin/main` commit; do not pull or edit the shared main
  checkout merely to refresh a task.
- Reserve main only to publish status or to perform an authorized merge.
  The status publisher can create status-only commits without checking out
  main at all. It still changes the remote main ref and therefore needs the
  same reservation. A PR or merge queue does not authorize an unrelated
  agent to edit the local main checkout.
- An attached, idle main checkout is an integration-only worktree. Never use
  it as a general-purpose task workspace. Do not detach, stash, reset, or
  clean another agent's main checkout to acquire it.

## Reservation record and acquisition

Maintain one repository-wide current-state record at
`docs/agent-sync/main/ownership.json`, separate from each agent's task
`status.json`. Its sign-in identifies the repository/ref, run ID, stable
agent ID, runtime session ID when known, operation (`STATUS` or `MERGE`),
actual checkout path if used, starting remote-main SHA, UTC sign-in time,
and a monotonic revision. A free record retains the previous owner, UTC
sign-out time, and the resulting status or merge commit SHA for audit.
Unknown telemetry is `null`, not a guessed identity.

The owner acquires this record with an atomic, status-only fast-forward
commit based on the latest fetched remote main. On a rejected push, fetch
and reread the owner before retrying: never treat a stale observation of
`FREE` as permission. If another owner is signed in, **wait for its verified
remote sign-out**. While waiting, agents may continue independent work in
their own worktrees, but must not use main or publish another status
transaction. The publisher waits up to 30 seconds by default; its bounded
`--wait-seconds` option permits 0-120 seconds per attempt. Report `BLOCKED`
if the wait cannot finish; never silently steal an old reservation,
force-push, or override branch policy.

Only the recorded owner may write or release main. Recheck the owner and
expected revision immediately before every main mutation. A task-level
sign-in, a clean local checkout, or a successful fetch is not a main
reservation. If local main is dirty or its history diverges, preserve it
and coordinate with its owner rather than pulling, rebasing, resetting, or
committing someone else's work.

## Status transaction: release immediately

1. Prepare and validate the status payload outside the main checkout. Read
   the latest remote ownership record, then sign in for `STATUS`.
2. Commit/push only the intended status paths, and verify the resulting
   commit on fetched `origin/main`. The fast publisher must check that its
   caller still owns main after any concurrent-push retry.
3. **Immediately after that status commit**, sign out of main with a
   status-only release commit that records the result. Perform no tests,
   implementation, review, or unrelated status work between the status
   commit and release. Automate this release in the publisher rather than
   depending on an agent to remember it.

Reacquire for the next status update, even when the same task is still
running. Signing out of main does not sign out of the task edit scope; the
agent's task `status.json` remains accurate until that agent finishes or
releases its assigned files. Failed publication or failed release must be
reported explicitly: an unverified release leaves main reserved and all
other agents waiting.

Use `publish_agent_sync.py --main-action acquire --operation MERGE` and its
`--main-action release` counterpart for authorized merges; see the
[publisher guide](./README.md#reserve-main-for-an-authorized-merge) for the
required repository, run/agent IDs, returned token, and merge-result SHA.
For status updates the same publisher acquires and releases automatically.
It rechecks main ownership on every concurrent-push retry and avoids two
extra commits for an identical, already-published status.

## Merge transaction and recovery

The authorized branch owner/coordinator acquires `MERGE` before any
operation that changes main. Keep the reservation only for the merge
transaction, verify its remote result, and release main promptly. If a
merge queue accepts work but applies it later, release any local checkout
after submission; the queue owns remote ordering. This reservation does
not transfer merge permission or allow an unauthorized direct main push.

On interruption or an ambiguous push result, fetch and reconcile the
authoritative remote record and target commit before retrying. If the owner
cannot release cleanly, keep the record occupied, identify the owner and
last verified SHA, and escalate for a documented recovery decision. Never
infer sign-out from a timeout, an absent process, or a local commit.
