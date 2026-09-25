# Coordinator decisions - exclusive main ownership

No PR has been opened. The repository's prior Ralph runs use an authorized,
verified fast-forward integration when policy permits; this branch remains
unpublished and unmerged until the shared dashboard owner signs out and
final acceptance checks pass. A local implementation commit or a status
commit does not establish remote-main completion.

## Decisions

- Keep task edit-scope ownership and main ownership separate. A task may
  remain `IN_PROGRESS` while its `STATUS` reservation signs out immediately
  after the verified status commit. A `MERGE` reservation is released after
  verification or promptly after queue submission.
- Use one remote `docs/agent-sync/main/ownership.json` record and atomic
  status-only fast-forward commits for acquisition and release. A rejected
  push rereads the latest owner; a foreign or stale owner cannot release or
  steal another transaction. If verification is impossible, leave ownership
  reserved and report the unresolved outcome rather than asserting success.
- Fetch the latest remote instructions into isolated worktrees. Do not pull
  or rebase another agent's shared `main` checkout merely to refresh.
- Reuse the released publisher and protocol guide from saved local commit
  `bc366c34cbe996538f677faf7e113806df8033ae`. Only those two new paths
  were imported; its other changes still belong to their original branch
  and overlapping owners.
- The first concurrent-fetch test exposed a shared remote-tracking ref
  lock race. A unique temporary fetch ref per transaction and explicit
  cleanup resolved it; three repeated concurrency checks passed.
- A `FREE` record without a verified sign-out outcome is not a handoff.
  The publisher refuses malformed releases and checks any recorded result
  against the reservation's starting main SHA and current remote history.
- The status-reporting owner signed out before changes to its Ralph
  instructions. The iteration-stall owner has not signed out of the
  aggregate dashboard; that file remains untouched until its release.
- The existing dashboard-index contract now correctly fails for this new
  coordinator leaf until the owner can add it to the shared dashboard.
  This is a coordination blocker, not a reason to weaken the assertion or
  overwrite the active owner's work.

## Pending integration and memory review

The coordinator still must synchronize the branch leaf and aggregate
dashboard, commit final records, rebase/retest on the latest fetched
`origin/main`, perform the authorized merge, fetch/verify its merge SHA,
and review durable project lessons. If merge authorization or dashboard
ownership is denied, preserve this branch and worktree.
