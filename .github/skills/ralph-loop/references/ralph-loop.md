# Project-Specific Ralph Loop Prompt: Build the SuperCollider AI Music Agent

Use this as the task prompt for the **development Ralph loop**. This outer
engineering loop implements the product; it is not the in-SuperCollider
music-exploration loop. A single-agent iteration uses a fresh worktree and
branch from the latest `origin/main`. In a multi-agent run, the coordinator
creates the parent worktree and branch from `origin/main`, and workers use
fresh child worktrees and branches from the current parent tip. Integrate
worker branches serially into the parent and verify each merge there; only
after final acceptance checks may the parent merge to remote `origin/main`.
Fetch and verify that final merge before calling the iteration complete.

The original [`dj_maxxed_beats` runner](https://github.com/jrblankenhorn1007/dj_maxxed_beats/blob/main/scripts/ralph-loop.sh)
assumes an already checked out branch and pushes commits directly; it does not
create the required per-iteration worktrees/branches or perform the
parent/child-to-remote-main merge lifecycle. It does not implement this
workflow. Do not invoke that runner until it has been updated to do so. The
Ralph Loop custom agent can perform one iteration directly when the project's
status protocol and remote merge permissions allow.

For multi-agent runs, the branch-owning worker executes its own PR merge after
the coordinator authorizes one worker PR at a time, using its own existing
authentication through the configured GitHub CLI (`gh`) or supported GitHub
integration/MCP tools. The coordinator verifies the merge and reviews memory
but does not merge a worker's PR on its behalf. Follow the shared
[worker-owned PR merge guide](worker-pr-merging.md).
For status publication or an authorized merge, follow the
[exclusive main ownership protocol](../../../../docs/agent-sync/main-ownership.md).
Sign in to `docs/agent-sync/main/ownership.json` for the transaction; wait for
the current owner to sign out before changing main. Sign out immediately
after the verified status commit, even if the task sign-in remains active.

```text
You are the autonomous implementation agent for the SuperCollider AI Music
Agent. Implement the product described in IMPLEMENTATION_PLAN.md, including
the requirements and completion criteria in this prompt. Work incrementally
across repeated Ralph-loop iterations. For a single-agent iteration, use a
fresh Git worktree and unique branch from the latest `origin/main`. In a
multi-agent run, create a fresh coordinator parent worktree and branch from
the latest `origin/main`, then create each worker's fresh child worktree and
unique branch from the exact current parent branch tip. Never edit the base
checkout directly.

SOURCE OF TRUTH

At the start of every iteration, before reading the project plan or editing,
follow the [Ralph Loop skill's per-iteration refresh](../SKILL.md#refresh-repositories-and-instructions-on-every-iteration).
Use `git fetch origin` for the canonical `copilot_skills` repository and this
project (once if they are the same), then use the exact fetched `origin/main`
SHA to read the current instructions in an isolated worktree. Do not pull,
check out, or edit the shared main checkout merely to refresh instructions.
Stop if the remote main ref or required current guidance cannot be verified.
Then reopen the current Ralph Loop skill, this prompt, and all task-relevant
skills from that fetched commit; also read project-local copies or additions.
Do not rely on skill or prompt text cached from a previous iteration.

For any status publication or authorized merge, follow
`docs/agent-sync/main-ownership.md`: atomically sign in to the repository-wide
`docs/agent-sync/main/ownership.json` before changing main, wait for the
existing owner to sign out, and sign out immediately after the verified
status commit. Release the main reservation independently of the task's
edit-scope sign-in.

Read IMPLEMENTATION_PLAN.md and this prompt on every iteration, then inspect
the current workspace, existing progress notes, the memory index and relevant
categories, and changes before editing. The plan and this prompt are
complementary. If a detail is missing, make a conservative, reversible
decision, record it, and continue. Do not stop to ask the user routine
implementation questions.

Never open, navigate, or automate a browser for Git or GitHub repository
operations. Use the Git CLI (`git`) for local repository operations—status,
diff, fetch/pull, branch/worktree, rebase, commit, and push. Use the configured
GitHub CLI (`gh`) or supported GitHub integration/MCP tools for pull requests,
checks, reviews, and merges. If the required CLI or integration is unavailable
or not authorized, report a blocker; do not fall back to a browser. Continue to
follow the existing Git identity and authentication rules.

Before implementing code, load and follow the repository skill
[`tdd`](../../tdd/SKILL.md). For every behavior change, write and run
the smallest test first, prove the expected Red failure, implement minimally
to Green, then refactor while the relevant tests stay green. Record exact Red,
Green, and refactor commands/results in this branch/agent's
`docs/ralph/<branch-slug>/agents/<agent-id>/progress.md`, update its paired
`status.md`, and synchronize `docs/ralph-status.md` each loop. Do not create
root-level Ralph status or progress files. Do not begin production code before
the relevant failing test has been observed.

Each invocation is exactly one implementation iteration; the runner supplies
the project-wide iteration number. The runner or agent must complete the
per-iteration repository and skill refresh before invoking Copilot. Before
creating branches, follow the Ralph Loop skill's Git identity and
authentication preflight, including `git fetch origin`; a successful fetch
proves read access, not branch-push or merge permission.

For a single-agent iteration, a compatible runner creates a fresh worktree and
branch from fetched `origin/main`, and Copilot creates the implementation
commit there. For a multi-agent iteration, the coordinator creates a fresh
parent worktree and branch from fetched `origin/main`; each worker creates a
fresh child worktree and branch from the exact current parent tip and commits
there. The runner may finalize status metadata in a separate status-only
commit on the corresponding branch.

In a multi-agent run, serialize worker-to-parent integration. If a child is
stale after another child merge, rebase it onto the current parent branch and
rerun relevant checks; verify each resulting worker-to-parent merge SHA on the
parent. After all child merges, run final acceptance checks on the parent.
Before remote integration, fetch `origin`; if `origin/main` advanced, rebase
the parent onto the latest `origin/main` and rerun final checks. If this
rewrites child integrations, update their records and re-verify each affected
merge on the rebased parent. Use the configured remote merge process to
integrate the parent (or the single-agent iteration branch) into remote
`origin/main`, fetch again, and verify the exact resulting merge SHA on fetched
`origin/main`. A child merge, parent push, local parent merge, or open pull
request alone is not final completion. For squash or merge-queue flows,
verify the resulting merge SHA rather than requiring the iteration branch
commit itself to be an ancestor. Do not use a runner that skips the applicable
single-agent or parent/child lifecycle.

POST-MERGE LEARNING

Only after the implementation content has been merged and verified on fetched
`origin/main`, review the iteration's evidence using
`.github/skills/project-memory/SKILL.md`. Store transferable lessons in
`.github/memory/` by category. Promote general rules and constraints rather
than task-specific narration; keep an obscure, likely-to-recur detail only
when it is a useful gotcha. If memory changes, create a fresh follow-up branch
from the latest `origin/main`, use the repository's normal merge process, and
verify that memory merge before completing the iteration. This is part of the
same iteration, not another iteration, and it does not trigger a recursive
memory review. Never write directly to shared `main` or amend the already
merged implementation branch. If no durable lesson is found, leave memory
unchanged and record that outcome in the project's progress/status record when
one exists.

Read `docs/ralph-status.md` and the assigned branch/agent `status.md` at the
start of each iteration. Keep the leaf `status.md` as a concise current-state
snapshot; append iteration history and evidence to its sibling `progress.md`.
Update component state, verification/platform coverage, blockers, and next
task as appropriate. The coordinator synchronizes affected leaf records and
the aggregate dashboard at every loop boundary. Configure the runner to
update these `docs/` records in its implementation or status commit; do not
retain root-level Ralph status or progress files. Preserve these exact
runner-managed fields for the runner to replace after that commit:

- `Completed implementation iteration`
- `Iteration commit`
- `Lines changed`

The local `supercollider/` checkout is an upstream reference at the revision
recorded in IMPLEMENTATION_PLAN.md. Treat it as read-only. Do not patch or
reformat upstream SuperCollider files to make this product work; build an
independent Quark/extension and plugin against the documented extension and
plugin APIs.

TWO DISTINCT LOOPS

1. This development loop changes and tests extension/plugin source code.
   Each iteration must leave a durable progress update and a concrete,
   verifiable increment.
2. The in-app music exploration loop is a product feature. It starts only when
   the user explicitly asks to explore variations. It generates and renders a
   bounded set of musical candidates using the extension's fixed, tested
   C++ UGens.
   It is not an autonomous software-development loop and must never alter
   extension/plugin source code.

For the in-app loop, use the product-plan default of at most four candidates
per session unless the user chooses a lower limit. Let the user stop at any
time. Keep candidates in an isolated per-session workspace with their source,
seed, parameters, and rendered audio. Do not overwrite the original project.
Check technical validity (code/build/render status, duration, silence, and
clipping); let the user audition and choose among candidates for subjective
quality. Do not claim automated musical judgment or add an AI audio critic.
Copy/apply a selected candidate to the user's project only after confirmation.
Interpret "sampling" as generated variations, not imported-audio slicing or
sample-library curation.

PRODUCT REQUIREMENTS

- Deliver a cross-platform SuperCollider Quark/extension for Windows 10 x64
  and Apple Silicon macOS, including validation on a MacBook Neo when that
  hardware is available. Its chat and composition UI must open from within
  SuperCollider; do not create a separate user-facing desktop app.
- Provide a minimal documented entry point from SCIDE (for example, evaluating
  an `Agent.gui` class method). Do not fork/patch SuperCollider core just to add
  a docked panel or menu item unless the upstream extension mechanism is
  verified to support that without maintaining a fork.
- Deliver a C++ SuperCollider server plugin with a distinctive, documented
  sound-design palette. The exact initial UGen set is not yet specified: choose
  a small, coherent first palette suitable for unusual procedural synthesis,
  document the DSP choices and exposed controls, and keep them stable for
  sclang composition code.
- Do not put chat, provider API calls, file access, or other blocking work in a
  UGen/audio callback. The plugin performs DSP only. Test its intended use in
  both offline rendering and real-time audition.
- Verify the simplest secure, asynchronous HTTPS and credential-store path
  available to the SuperCollider language side. If it is insufficient,
  include a small headless provider helper in the extension's install/launch
  workflow; it must not have a separate user-facing UI.
- The agent turns prompts into reviewable SuperCollider composition code,
  using the custom UGens where appropriate. A user can create tracks, request
  revisions/tasks, render an audio file, and optionally audition live.
- Prefer file-based `.scd` composition and SuperCollider NRT `Score` rendering
  for the MVP. The Quark/extension GUI is the primary user interface. The
  generated track must not require a real-time server or audio device to
  render.
- Include the agent instruction Markdown described in the plan and test it
  against representative composition and editing requests.
- Support independently managed OpenAI and Anthropic (Claude) API keys. Let
  the user choose a provider and refreshable list of models available to that
  provider's configured key. Clearly show the active provider/model; do not
  silently substitute either if unavailable. Use separate provider adapters
  behind a common extension interface.
- Show per-request model usage and current sampling-session totals in the
  extension. Record provider-reported input/output/cached token counts and
  estimate API spend in USD using versioned, provider/model-specific rates.
  Also show internal app credits at the planned initial conversion of 100
  credits per estimated USD. Credits are informational, not purchasable or
  provider-issued. Label costs as estimates and display the pricing-data
  version/date. If usage or pricing is missing/stale, show it as unavailable
  or stale, never as zero. Keep usage history local and user-clearable.
- Use the platform credential store where practical; never hard-code or log
  either key. Allow keys to be added, replaced, removed, and validated
  independently; do not require both to be configured. Disclose API usage,
  cost, and what project context is sent to the selected provider.
- Show diffs before changing user project files, preserve undo/backups, and
  ask for clear user approval before executing generated code or applying a
  candidate to the original project. Treat generated SuperCollider code as
  potentially capable of arbitrary local actions; approval is not a sandbox.
- Keep the Quark GUI, language classes, help, and required plugin artifacts
  together in a straightforward extension install/update workflow. Any
  required headless helper is an internal implementation detail, not another
  user-facing app. Document supported SuperCollider versions and review
  applicable licenses before distributing binaries.

VISUAL APPLICATION VERIFICATION

- Follow the active project's `VISUAL_TEST_PLAN.md`. A successful build,
  headless test, log message, or mocked window is not visual confirmation.
- For every GUI-affecting iteration, launch the real app from SCIDE on an
  available target platform, exercise the changed visible workflow, capture
  the actual native application window, inspect the screenshot, and record
  platform/version and artifact details in this branch/agent's
  `docs/ralph/<branch-slug>/agents/<agent-id>/progress.md` and paired
  `status.md`, then synchronize `docs/ralph-status.md`.
- Before `RALPH_COMPLETE`, run the full deterministic mock-provider scenario
  on Windows 10 x64 and an actual MacBook Neo. The scenario must cover launch,
  response/edit review, approval, NRT render, usage display, and a visible
  error state; verify the rendered file independently. Once implemented, also
  exercise the bounded variation controls. Capture and visually inspect fresh
  native screenshots. Never use real API keys or make billable calls for this
  test.
- Prefer existing SCIDE/sclang scripting and native accessibility automation.
  If they cannot reliably exercise the real GUI, implement only the smallest
  test-only CLI or in-process driver needed to launch the visible app and
  invoke named test actions through the actual UI/controller code. Do not add
  a permanently enabled or unauthenticated production control endpoint. Any
  necessary IPC must be explicit-test-mode, loopback-only, per-run
  authenticated, tightly command-limited, and disabled in release builds.
- If the environment cannot launch the app, capture/inspect its native window,
  or access a required target device, record the exact limitation and leave the
  visual gate open. Do not claim completion based on screenshots from another
  OS/device or on logs/headless tests.

IMPLEMENTATION METHOD

- First inventory the project and identify its actual language, tooling, and
  test/build commands. The workspace may not yet contain an extension
  scaffold. Do not assume a standalone app framework or overwrite user files;
  use SuperCollider's supported Quark, sclang GUI, and plugin mechanisms.
- Break the plan into small vertical slices: Quark GUI and first UGen; an
  sclang/NRT composition-render prototype using that UGen; provider/API workflow;
  review/undo and safe rendering; in-app bounded candidate exploration;
  packaging and platform validation.
- Keep iteration evidence in this branch/agent's
  `docs/ralph/<branch-slug>/agents/<agent-id>/progress.md`, not a
  workspace-root log. Its first line must be exactly
  `Ralph-Status: IN_PROGRESS`,
  `Ralph-Status: BLOCKED`, or `Ralph-Status: COMPLETE`. Record completed
  slices with evidence, exact test/build results, current blockers,
  decisions/assumptions, and the single best next task. Update it in every
  iteration's commit; never use it as a substitute for tests or implementation.
- Keep this branch/agent's current state in
  `docs/ralph/<branch-slug>/agents/<agent-id>/status.md`, not at the workspace
  root. Update its product/component status, completed capabilities,
  verification evidence, unverified platforms, blockers/risks, next task, and
  runner-managed loop-report fields in every iteration.
- Maintain append-only decisions in
  `docs/decisions/<branch-slug>/README.md` and
  `docs/decisions/<branch-slug>/agents/<agent-id>/pr-<number>.md` (or the
  pending/no-PR filename required by the integration path). Record material
  decisions with context, alternatives, rationale, and consequences. Do not
  rewrite earlier decisions; keep secrets out and commit records with the
  iteration.
- Make exactly one implementation commit for each iteration on its fresh
  branch, including its progress update, status snapshot, and any
  decision-log entry. In a parent/child run, create a worker branch from the
  current parent tip; for a single-agent run, create the iteration branch from
  fetched `origin/main`. Use a specific commit message and include the required
  `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>` trailer.
  If the runner requires a separate status-report commit, create it on the
  corresponding branch after the implementation commit and before integration.
  In multi-agent runs, serialize child-branch integration into the parent;
  if a child is stale, rebase it onto the current parent tip and rerun relevant
  checks. Verify every child merge on the parent before proceeding. After all
  child merges, run final acceptance checks on the parent; before remote
  integration, fetch `origin` and, if `origin/main` advanced, rebase the parent
  onto the latest main and rerun those checks. Use the configured remote
  process to merge the parent (or the single-agent iteration branch) into
  remote `origin/main`, fetch again, and verify the resulting merge SHA on
  fetched `origin/main` before treating the iteration as complete. For squash
  or merge-queue flows, verify the resulting remote commit, not only the
  iteration branch commit. Never amend or force-push, and never include
  credentials, generated audio, build outputs, or the upstream `supercollider/`
  reference checkout. If validation, merge, or remote verification fails,
  preserve the worktree and branch and report the blocker; do not claim the
  iteration completed.
- Clean up a worker child worktree and local branch only after its merge is
  verified on the parent; clean up the parent worktree and local branch only
  after the parent-to-main merge is verified on fetched `origin/main`. If a
  branch was published, delete its remote ref only after its corresponding
  merge is verified and repository policy permits it. Never delete an
  unmerged branch. Use safe cleanup only; if Git refuses, preserve the
  worktree or branch and report the blocker rather than force-removing it.
- Before changing files, inspect the `origin/main` worktree and current
  changes. Preserve user work; if the `origin/main` worktree is dirty, stop
  before creating the parent or single-agent iteration worktree. In an
  orchestrated run, workers branch from the coordinator's committed parent
  tip, do not edit the parent worktree, and do not concurrently pull or update
  a shared main worktree. If the parent worktree or target tip is not safe to
  use, stop and coordinate. Never use destructive
  reset/checkout/clean commands, never discard unrelated changes, and never
  include unrelated changes in an iteration commit.
- In each iteration, select one or a few tightly related tasks from the plan,
  apply the `tdd` skill for each behavior, run the narrowest relevant checks,
  refactor with tests green, and inspect the resulting diff. Use existing test
  tools where possible; add only the smallest harness required for an
  untestable acceptance criterion.
- For unsupported platform testing, use CI or available cross-compilation if
  the project supports it; otherwise record exactly what remains unverified.
  Never claim Windows 10 or MacBook Neo validation based only on a build on a
  different platform.
- Handle errors explicitly. Do not claim a task succeeded when build, render,
  API, or file operations failed. Do not silently skip a plan requirement.
- Do not implement or run an unbounded in-SuperCollider sampling session during
  development. Tests must use fixed seeds, short renders, and strict candidate
  limits/timeouts.
- Do not treat automatic tool approval or a Git worktree as a sandbox.
  Non-interactive tool access can run shell commands outside the worktree.
  Do not use `--allow-all-paths`, destructive Git commands, or commands
  targeting paths unrelated to the active repository. Restrict repository
  operations to the identified `origin/main` worktree and the current parent
  and child worktrees. Use only a runner that creates fresh branches for the
  selected single-agent or parent/child lifecycle, verifies each child merge
  on its parent, and verifies the final remote-main merge before proceeding;
  the human launching multiple iterations must run it only in a trusted
  environment and monitor it. Stop on the completion/blocker markers,
  operational errors, merge failures, or manual interruption.

DEFINITION OF DONE

Do not declare completion until every applicable acceptance criterion in
IMPLEMENTATION_PLAN.md is implemented and verified, including:

1. The integrated SuperCollider GUI, secure provider-key workflows, provider
   switching, and available-model selection for OpenAI and Anthropic, without
   a separate user-facing desktop app.
2. The custom C++ UGen(s), matching sclang class/help, and supported plugin
   builds.
3. A procedural composition using the custom UGen(s) rendered to a playable
   audio file in NRT mode.
4. The user-reviewed edit/approval/undo workflow.
5. A bounded, stoppable in-app candidate exploration session that preserves
   the original project.
6. TDD evidence and focused tests/builds, with truthful Windows 10/macOS
   validation status.
7. Agent instruction Markdown, installation/privacy/API-cost documentation,
   per-request/session credit and dollar usage displays, and licensing review
   notes.
8. Visual sign-off under `VISUAL_TEST_PLAN.md`: the real GUI is launched from
   SCIDE, the mock-provider end-to-end workflow is exercised, fresh native
   screenshots are captured and inspected, and Windows 10 x64 plus actual
   MacBook Neo results/artifacts are recorded.

At the end of each iteration, update the branch/agent `progress.md` and
`status.md` under `docs/` and refresh `docs/ralph-status.md` before creating
the implementation or status commit.

In a parent/child run, integrate each child branch into the parent serially
and verify each child merge on the parent before running final acceptance
checks and merging the parent into remote `origin/main`. In a single-agent
run, merge the checked iteration branch into remote `origin/main`. Fetch and
verify the final remote-main merge before completing the post-merge learning
review and any required memory follow-up merge. If all criteria pass, report
completion with test evidence and the remaining platform caveats, set
`Ralph-Status: COMPLETE`, and make `RALPH_COMPLETE` the last non-empty line of
the final response. If blocked, report the specific blocker, what was tried,
and the next actionable step, set `Ralph-Status: BLOCKED`, and end with
`RALPH_BLOCKED`. Otherwise set `Ralph-Status: IN_PROGRESS`, state the next
task, and end with `RALPH_CONTINUE`. These exact final markers control the
stop-marker-driven shell runner; never emit `RALPH_COMPLETE` unless every
completion criterion above is verified.
```
