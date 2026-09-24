# Workflow

## Keep post-merge follow-ups reviewable

- **Rule:** Deliver work discovered after a change has merged as a new,
  reviewable change based on the current main branch; do not write directly to
  main or amend an already integrated branch.
- **Why:** The merged branch is no longer an integration path, and follow-up
  work still needs the repository's normal checks and merge verification.
- **Gotcha:** A lesson found during post-merge review cannot be added to a
  change that has already merged.
