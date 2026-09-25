# Branch Decision Index

- **Branch:** `agents/update-dependencies-docs-opencode-setup`
- **Run/tasks:** `copilot-skills-opencode-setup-20260924-2325` /
  `opencode-setup-docs`, `opencode-ralph-runtime`
- **Initial `origin/main` base:**
  `9558f99cc34cbed8dd1d24f4f15fc03f5d78b6ea`
- **Parent rebased onto:**
  `7ee1307cb47f5a88cd6b46ee135444777ddeb665`
- **Current parent implementation commit:**
  `9aca13bccabb6f03b2eca29c138b9dc23ca7dd98`
- **Current state:** `IN_PROGRESS`; OpenCode setup, default runtime profiles,
  compatibility guidance, and contract tests are implemented. Authenticated
  model validation and remote-main integration remain pending.
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

## Unresolved blockers

- OpenCode has no configured provider credentials (`opencode auth list`
  reports 0 credentials), so authenticated model execution is not verified.
  The user must complete provider sign-in through OpenCode before the bounded
  model smoke test can be run.
- The parent is not yet published or merged. The GitHub CLI is authenticated;
  use the repository's normal PR/review/integration flow after sign-in and
  independent review.
