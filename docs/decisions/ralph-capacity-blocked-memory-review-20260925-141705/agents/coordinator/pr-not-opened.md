# Coordinator integration record

- **Run / task:** `copilot-skills-memory-update-agent-20260925-0223` /
  `capacity-blocked-review-resume-guidance`
- **Branch:** `ralph/capacity-blocked-memory-review-20260925-141705`
- **Worktree:** `/Users/jrblankenhorn/copilot_skills.worktrees/ralph-capacity-blocked-memory-review-20260925-141705`
- **Base `origin/main`:**
  `88051ce785a38965e26b5744b6c8fc53e37fcc41`
- **Implementation commit:**
  `045ea5295d976fadde833f129daba74488a2bfa9`
- **PR:** `NOT_OPENED`; the repository's normal path is coordinator-managed
  fast-forward integration with a verified `origin/main` result.

## Integration requirements

1. Recheck that main is free before acquiring a `MERGE` reservation.
2. Refresh `origin/main`, rebase this unpublished branch if needed, and rerun
   the Ralph, Project Memory Update, and main-ownership contract suites.
3. Acquire the authorized `MERGE` reservation, integrate only after rechecking
   ownership, fetch, and verify the exact resulting merge on `origin/main`.
4. Release the main reservation promptly after verification.
5. Keep the original memory review `PENDING`. Refresh the full Resource
   Manager inventory and invoke the dedicated updater exactly once only after
   an atomic capacity reservation succeeds.

No PR, push, or merge is claimed by this record.
