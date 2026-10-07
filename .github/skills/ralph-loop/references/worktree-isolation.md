# Ralph Worktree Isolation and Session Identity

Every Ralph parent, child, and retry must have one explicit Git worktree
owner. A branch name in a prompt is not a workspace switch: only the host's
workspace/session binding determines where that agent's editor and shell
operate.

## Allocate collision-resistant identities

The coordinator creates each parent and child worktree before launching its
agent. Generate a unique `run-id` for the run and a new unique `dispatch-id`
for every worker launch or retry. Include both identifiers and the stable
`worker-id` in each child branch and worktree name. Include the run and
dispatch identifiers in the parent branch and worktree name as well. For
example:

```text
branch:   ralph/<task-slug>-<run-id>-<worker-id>-<dispatch-id>
worktree: <worktree-root>/ralph-<task-slug>-<run-id>-<worker-id>-<dispatch-id>
```

Never derive a path or branch from worker-id alone. A retry gets a fresh
`dispatch-id`, path, and branch; do not reopen or reuse the prior attempt.

Before creating a worktree, check that its absolute path is unused, that the
local branch ref is absent (`git show-ref --verify`), that the remote branch
ref is absent (`git ls-remote --heads origin`), and that neither path nor
branch appears in `git worktree list --porcelain`. If any identity already
exists, generate a new `dispatch-id` and check again. Never take over a
pre-existing worktree or branch, and never use `--force`,
`--ignore-other-worktrees`, or an equivalent override to bypass a collision.
Record the exact path, branch, and base SHA in the coordinator's assignment
before launch.

## Bind and verify the actual agent session

Launch each worker with the host-supported mechanism that binds its session
and editing tools to the assigned absolute child-worktree path. Do not treat a
path written in the prompt, a `git -C` command, or a test run from another
directory as proof that the agent's editing context changed.

Before reading or editing project files, each agent verifies from its actual
session:

```sh
pwd -P
git rev-parse --show-toplevel
git branch --show-current
git rev-parse HEAD
git status --porcelain
git worktree list --porcelain
```

The canonical `pwd -P` and Git root must both equal the assigned worktree
path; the current branch and `HEAD` must equal the assigned branch and exact
base SHA; the working tree must be clean; and the worktree registry must map
that path to that branch and base. The coordinator independently checks this
identity before authorizing edits or accepting a worker's sign-off. All
editor/apply-patch operations must use the verified worktree, not merely shell
commands that point there.

If the host cannot bind a session to its assigned worktree, or any identity
check differs, stop before editing. Do not switch branches, change directory
and continue with a mismatched editor, edit the parent/default checkout, or
reuse another agent's worktree. Report the expected and observed path, Git
root, branch, base SHA, clean-state result, and registry mapping; mark the
attempt `BLOCKED` without making changes. When the host cannot bind distinct
worker worktrees, do not dispatch in parallel. The coordinator may proceed
sequentially in its own verified worktree only if the project's workflow
permits it; otherwise report the limitation.

## Record identity evidence

Each agent records a `worktree_identity` object in its status leaf with:

```yaml
worktree_identity:
  state: VERIFIED
  expected_path: "<assigned absolute path>"
  observed_pwd: "<canonical pwd -P>"
  observed_git_root: "<git rev-parse --show-toplevel>"
  expected_branch: "<assigned branch>"
  observed_branch: "<git branch --show-current>"
  expected_base_sha: "<assigned full SHA>"
  observed_head_sha: "<git rev-parse HEAD>"
  working_tree_clean: true
  registry_match: true
```

If preflight fails, use `state: BLOCKED`, preserve both expected and observed
values, set the checks to false as appropriate, and record that no edits were
made. Keep this evidence with the worker's `status.md` and `progress.md`; the
coordinator synchronizes the summary in `docs/ralph-status.md`.
