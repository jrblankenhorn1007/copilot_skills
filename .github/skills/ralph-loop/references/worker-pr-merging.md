# Worker-owned PR merging

Every PR-backed Ralph iteration has one merge actor: the agent that owns the
iteration branch. In a multi-agent run, the coordinator reviews the worker's
sign-off, checks, and integration readiness, then authorizes one worker PR at
a time. The worker that owns the branch executes its own PR merge after that
coordinator authorization.

## Merge procedure

1. Confirm the coordinator authorized this exact PR and that required reviews,
   checks, and branch-update requirements are satisfied. Do not merge another
   worker's PR or treat an open PR as authorization.
2. Use the worker session's already-authenticated GitHub CLI and the
   repository's configured merge method. For example, when merge commits are
   the configured method, use `gh pr merge <number> --merge`. If the repository
   requires a merge queue, use its normal queue-enabled merge process instead
   (for example, `gh pr merge <number> --auto --merge` when configured).
   `gh auth status` can confirm the CLI is signed in; it does not prove that
   the worker has permission to merge this PR.
3. Wait for GitHub to report the PR as merged. Fetch `origin`, identify the
   resulting merge SHA, and verify that the exact SHA is reachable from
   `origin/main` (for example, with
   `git merge-base --is-ancestor <merge-sha> origin/main`). For squash or
   merge-queue flows, verify the resulting remote merge SHA rather than
   requiring the original implementation commit to remain an ancestor.
4. Record the worker who submitted or queued the merge action as
   `merge_actor_worker_id` in the leaf status, and append the exact merge
   command, resulting SHA, remote verification method, and timestamp to the
   worker's progress evidence. The coordinator independently verifies the
   merge, refreshes the aggregate dashboard, and completes the post-merge
   memory review before marking the iteration `COMPLETE`.

The coordinator serializes authorization; it does not merge a worker PR on
the worker's behalf. The coordinator does not use its own credentials to
merge a worker PR, and workers must not share or request credentials. Never
use `--admin`, push directly to `main`, or override managed host or repository
policy to force a merge.

If the worker's merge permission is denied, a required check or review is
missing, or the host does not expose the normal merge tool, preserve the
branch and PR and report a sanitized blocker. Do not retry with another
identity, ask for a token, or silently transfer merge ownership to the
coordinator. Resume only when the normal authorization, permission, and
repository requirements are satisfied.
