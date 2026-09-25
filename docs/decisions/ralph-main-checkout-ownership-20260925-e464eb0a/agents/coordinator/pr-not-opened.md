# Coordinator decisions - exclusive main ownership

No PR was opened. The repository's authorized no-PR fast-forward was
verified on fetched `origin/main` at
`f9cab16e19f22586192c93da76f7aedceced63ce` after all 41 Ralph
tests passed; the main reservation was released at
`ebb4cce4b8889b3693ffd218c7a7cf41f5610c3c`. A local implementation
commit or a status commit alone would not establish remote-main completion.

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
  instructions. The iteration-stall owner subsequently signed out and
  released the aggregate dashboard in remote status revision 2. This run
  then published its own scoped task sign-in and indexed its leaf without
  dropping any existing dashboard entries.
- The dashboard-index contract correctly failed while this leaf was
  unindexed. No assertion was weakened: after synchronization, its focused
  check and the complete 41-test Ralph contract both passed.
- The intervening Resource Manager implementation on remote main was
  preserved during rebase. Its direct main integration did not change the
  main-ownership revision, demonstrating why all future merge actors must
  use the reservation protocol rather than assuming a free record enforces
  itself.
- While this run's `MERGE` reservation was acquired, Resource Manager
  status-only commits had completed upstream. The dashboard rebase conflict
  was resolved by retaining its verified `COMPLETE` status and memory
  outcome alongside this run's new `AWAITING_MERGE` entry; rerun the
  complete contract before publishing.

## Post-merge memory review

The coordinator reviewed the memory index and workflow category after
verifying the merge. No new entry is needed: the ownership protocol and
tests already capture this iteration's reusable constraints.
