# Ralph Worktree Isolation and Session Identity

Every Ralph parent, child, and retry has an explicit worktree owner. A path or
branch in a prompt is not a workspace switch: the host determines where the
agent's editor and shell operate.

## Allocate collision-resistant identities

The coordinator creates each parent and child worktree before launching its
agent. Use a unique `run-id` and a new `dispatch-id` for every worker launch
or retry. Include those values and the stable worker ID in each child branch
and worktree path:

```text
branch:   ralph/<task-slug>-<run-id>-<worker-id>-<dispatch-id>
worktree: <worktree-root>/ralph-<task-slug>-<run-id>-<worker-id>-<dispatch-id>
```

Never derive a path or branch from worker ID alone. A retry gets a new
dispatch ID, path, and branch; do not reopen the previous attempt. Before
creating a worktree, verify that its absolute path is unused, its local branch
ref is absent with `git show-ref --verify`, its remote branch ref is absent
with `git ls-remote --heads origin`, and neither path nor branch appears in
`git worktree list --porcelain`. On any collision or inconclusive check,
choose a new dispatch ID and repeat the checks. Never take over an existing
worktree or branch, or bypass a collision with a force/ignore option. Record
the exact path, branch, and base SHA in the assignment.

## Bind and verify the actual agent session

Launch each worker with the host-supported mechanism that binds its session
and editing tools to the assigned absolute worktree path. Do not treat a path
in the prompt, `git -C`, or a test run from another directory as proof of
session binding.

Before reading project files or editing, run the read-only verifier from the
actual session, with the exact values supplied in the assignment:

```sh
python3 .github/skills/ralph-loop/scripts/verify_worktree_identity.py \
  --expected-path "$RALPH_EXPECTED_WORKTREE" \
  --expected-branch "$RALPH_EXPECTED_BRANCH" \
  --expected-base-sha "$RALPH_EXPECTED_BASE_SHA"
```

The verifier compares the canonical process working directory and
`git rev-parse --show-toplevel` with the expected path; compares
`git branch --show-current` and `git rev-parse HEAD` with the expected branch
and exact base SHA; requires `git status --porcelain` to be empty; and requires
exactly one `git worktree list --porcelain` entry for that path whose branch
ref and HEAD equal the assignment. It exits zero only when all six checks
pass and prints a JSON report. Any mismatch, malformed assignment, registry
mismatch, or Git command failure returns nonzero with `state: BLOCKED`.
The registry equality result is reported as
`registry_matches_expected_identity`.

Stop before editing. Do not read project files or continue from another
checkout after a nonzero result. Preserve the output, report the expected and
observed identity, and mark the attempt blocked with no edits made. Do not
switch branches, change directory and continue with a mismatched editor, edit
a parent/default checkout, or reuse another agent's worktree. If the host
cannot bind workers to distinct paths, do not dispatch them in parallel.

The coordinator independently verifies the worker's exact worktree and
assignment before authorizing edits or accepting a sign-off. Every editor or
patch operation must target the verified worktree.

## Record identity evidence

Record the verifier's point-in-time pre-edit result in the agent status leaf:

```yaml
worktree_identity:
  state: VERIFIED
  verification_phase: PRE_EDIT
  verified_at_utc: "<UTC timestamp>"
  expected_path: "<assigned absolute path>"
  observed_pwd: "<canonical process working directory>"
  observed_git_root: "<git rev-parse --show-toplevel>"
  expected_branch: "<assigned branch>"
  observed_branch: "<git branch --show-current>"
  expected_base_sha: "<assigned full base SHA>"
  observed_head_sha: "<git rev-parse HEAD before editing>"
  working_tree_clean: true
  registry_match: true
```

Use `state: VERIFIED` only when the pre-edit verifier exited zero and every
recorded value came from that same check. Preserve the pre-edit
`observed_head_sha` as evidence; do not replace it later with a post-edit HEAD
while retaining the old base or verification time. A later HEAD belongs in a
separate current branch/commit field. If a pre-edit check fails or cannot complete, use
`state: NOT_VERIFIED`, preserve the expected and observed values, record
`no_edits_made: true`, and explain the blocker. Do not label incomplete or
mismatched evidence `VERIFIED`.
