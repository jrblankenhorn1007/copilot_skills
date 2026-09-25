# Branch Decision Index

- **Branch:** `agents/update-dependencies-docs-opencode-setup`
- **Run/tasks:** `copilot-skills-opencode-setup-20260924-2325` /
  `opencode-setup-docs`, `opencode-ralph-runtime`
- **Initial `origin/main` base:**
  `9558f99cc34cbed8dd1d24f4f15fc03f5d78b6ea`
- **Parent rebased onto:**
  `0e6576aa6b7b581ec42d27f0a5468988396754db`
- **Current fetched `origin/main`:**
  `9b333479ffacb0d7ed81a613d7df2173bf62013b`
- **Current parent implementation commit:**
  `3de73a2a8f88e45754e214a8e370ff047d3328e3`
- **Current state:** `IN_PROGRESS`; OpenCode setup, default runtime profiles,
  compatibility guidance, and contract tests are implemented. Authenticated
  runtime validation, fresh worker sign-off/handoff, independent reviews,
  and remote-main integration remain pending.
- **Coordinator records:**
  - [Coordinator PR pending](agents/coordinator/pr-pending.md)
- **Worker records:**
  - [OpenCode setup worker](../ralph-opencode-setup-docs-worker-01-20260924-2325/README.md)
- **Status/progress:**
  - [Coordinator status](../ralph/agents-update-dependencies-docs-opencode-setup/agents/coordinator/status.md)
  - [Coordinator progress](../ralph/agents-update-dependencies-docs-opencode-setup/agents/coordinator/progress.md)
- **Remote merge:** Pending; do not mark complete before fetched
  `origin/main` verifies the parent merge and the post-merge memory review is
  complete.
- **Memory review:** Pending coordinator review after parent integration.

## Decisions

### Keep the OpenCode setup guide separate from the Ralph runtime migration

- **Context:** The user requested OpenCode setup/dependency documentation and
  asked that the Ralph Loop migration happen once OpenCode works.
- **Alternatives:** Replace the Copilot CLI invocation guidance immediately,
  or document general OpenCode setup while leaving Ralph runtime instructions
  unchanged until confirmed.
- **Decision:** Add a provider-neutral install/authentication guide and link
  it from the README. Do not claim the Ralph agent works in OpenCode or
  replace its current Copilot CLI runtime before validation.
- **Rationale:** OpenCode is not installed in this environment and the
  separate setup result is not available here; premature invocation examples
  would be unverified.
- **Consequences:** The Ralph CLI migration remains a required follow-up.

### Do not invent a package dependency manifest

- **Context:** Searches for common package/dependency manifests found none in
  this documentation-focused repository.
- **Alternatives:** Add a new package file solely to list the OpenCode CLI, or
  document OpenCode as an independently installed system CLI.
- **Decision:** Add no application dependency manifest; document official
  OpenCode install options and provider configuration.
- **Rationale:** OpenCode's installation is system-level, and no existing
  package manager configuration is present to update.
- **Consequences:** No package dependency changed; the setup guide is the
  source for installation instructions.

### Use one worker until the runtime gate clears

- **Context:** General OpenCode setup documentation was independent and
  ready; the second, larger Ralph runtime migration was explicitly gated on
  OpenCode working.
- **Alternatives:** Invent a second independent assignment, duplicate the
  setup scope, or launch only the ready worker.
- **Decision:** Launch one setup documentation worker and queue the runtime
  migration for coordinator follow-up after validation.
- **Rationale:** Independent ready work was available only for the setup guide.
- **Consequences:** Effective worker count is one; overall run remains
  `IN_PROGRESS`.

### Make OpenCode the default after CLI/profile validation

- **Context:** The task requested that Ralph move to OpenCode once its setup
  works. OpenCode 1.18.32 is installed; the local CLI exposes the required
  `run` options and discovers the repository's custom profiles, but
  `opencode auth list` reports zero credentials.
- **Alternatives:** Keep Copilot CLI as the default until a provider is
  authenticated, or provide the OpenCode primary/worker/reviewer profiles and
  setup instructions now while clearly recording that a model-backed run is
  not yet verified.
- **Decision:** Make OpenCode the documented/configured Ralph default, retain
  Copilot only as compatibility guidance, and keep authenticated runtime
  validation as an explicit external prerequisite.
- **Rationale:** CLI installation, invocation options, profile discovery,
  permissions, and static contracts can be validated without using or
  collecting provider credentials. A missing credential must not be
  disguised as a successful model run.
- **Consequences:** Repository setup and migration are implemented, but a
  bounded authenticated smoke test and final integration remain pending until
  the user completes provider sign-in.

### Keep authenticated runtime validation as a separate acceptance gate

- **Context:** The CLI is installed and discovers all four repository
  profiles, but `opencode auth list` reports zero credentials.
- **Alternatives:** Treat local CLI/profile discovery as proof that a model
  can run, or leave the implemented migration explicitly unverified until an
  authenticated smoke test succeeds.
- **Decision:** Do not claim that OpenCode is working end-to-end or authorize
  integration until a bounded model-backed Ralph invocation succeeds.
- **Rationale:** Profile parsing and CLI help do not exercise a provider
  request; missing credentials prevent that request.
- **Consequences:** OpenCode is the documented default, but runtime
  validation remains blocked on provider sign-in.

## Recovered issues

- An earlier `git pull --ff-only` in the primary checkout refused because
  local `main` had eight local-only commits and was 23 commits behind
  `origin/main`. On the next iteration, the primary checkout was clean and
  already matched fetched `origin/main`; `git pull --ff-only` succeeded.
  This run did not reset or rewrite the preserved local Ralph branch.
- `origin/main` advanced while the documentation worker was active. The
  parent was fast-forwarded to `8da9310fda1b2e3042a379081dfb0675f1b22d6b`,
  and the unpublished child was rebased and retested without conflicts.
- The worker contract-test attempt initially failed because the coordinator
  had not yet indexed the worker leaf. The coordinator added the dashboard
  links; the rerun passed all 13 tests in 6.585s.
- After the prior status sync, `origin/main` advanced again. The clean
  primary integration worktree was fast-forwarded from
  `3873311c9eb041df86285a31199fd68e7c3ae6a3` to
  `13a3fab74cba841316d796775ef4ab1aac476d20`; this parent remains based on
  `0e6576aa6b7b581ec42d27f0a5468988396754db` until it can be safely rebased
  and reverified.
- `origin/main` subsequently advanced to
  `81bf5aa111c7b26468585be364ab1b8055f000bf`. The clean integration worktree
  was fast-forwarded from `13a3fab74cba841316d796775ef4ab1aac476d20`;
  the task branch remains unpublished and has not yet been rebased.
- `origin/main` then advanced to
  `9b333479ffacb0d7ed81a613d7df2173bf62013b`. The clean integration worktree
  already matched that fetched tip; the parent branch remains based on
  `0e6576aa6b7b581ec42d27f0a5468988396754db`.
- Before the latest parent rebase, the 20-test contract baseline found two
  missing OpenCode-run branch-index entries. Adding the coordinator and
  legacy setup-worker entries restored the full 20-test baseline.
- `origin/main` advanced to
  `7ee1307cb47f5a88cd6b46ee135444777ddeb665`. Rebasing the unpublished parent
  required resolving `docs/ralph-status.md`; the resolution preserved both
  upstream dashboard records and this OpenCode run.
- The first OpenCode contract-test Red produced seven failures across the
  three new tests because the agent profiles, auth/model setup instructions,
  and OpenCode-default runtime guidance were absent. The implemented profiles
  and documentation resolved those assertions; all 23 contract tests pass.
- A revision-3 task-scope publication initially waited on an unrelated
  `MERGE` reservation. After its owner signed out and the merged result was
  verified, the status publisher succeeded and released its own reservation.
- Rebase onto `b3360ae2c6df9f874c42ff332e9037c5a6b44855` conflicted in
  `docs/ralph-status.md` where the status-reporting run and OpenCode run had
  both appended dashboard records. The resolution preserved both runs and
  their branch/agent rows; the 27-test contract suite and `git diff --check`
  passed. The parent then rebased cleanly onto
  `0e6576aa6b7b581ec42d27f0a5468988396754db`.
- The revision-4 task status transaction published successfully and signed
  out; the fetched remote tip later advanced to
  `1e9a6dab03c07ea9990fe4f65039ffdc4e784f45` while the parent remains based
  on `0e6576aa6b7b581ec42d27f0a5468988396754db`.

## Unresolved blockers

- OpenCode has no configured provider credentials (`opencode auth list`
  reports 0 credentials), so authenticated model execution is not verified.
  The user must complete provider sign-in through OpenCode before the bounded
  model smoke test can be run.
- The Resource Manager reported zero available slots at
  `2026-09-25T14:32:13Z` (nine active agents; one-minute load 8.62 on six
  logical cores), so the required independent code and security reviews could
  not be dispatched.
- Worker-01's legacy status signs off the pre-rebase implementation commit
  `9f8e5e850df47700763d8d74d2250fb200804d7e` and contains no `memory_handoff`.
  The old parent integration proof was superseded; a fresh worker
  self-attestation and handoff are required.
- The parent is not yet published or merged. The authenticated GitHub CLI is
  available, but the PR, independent reviews, remote-main verification, and
  post-merge memory review remain pending.
