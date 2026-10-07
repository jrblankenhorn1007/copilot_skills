# Pipeline Live-Model Evaluation Decisions

- **Run ID:** `pipeline-live-model-evaluation-20261007-35327e2e`
- **Task ID:** `all-skill-agent-live-model-tests`
- **Branch:** `ralph/pipeline-live-model-evaluation-20261007-35327e2e`
- **Initial base:** `fb82e0d85ef80b26537c3fede01bcaefa422652d`
- **Initial implementation commit:** `d5cf0f6576d7c9b9f98216093167db48f728479e`
- **Latest implementation commit before authorized integration:** `17dad8789e6c01a84d6dfeebd3a3657c079087a5`
- **Latest rebase base:** `c23b6e8ffb285ef57f4d99b45425a31ad031ee91`
- **Agent:** `coordinator-01`; runtime `copilotcli:/35327e2c-33cc-430e-90bd-c4f9a1e20471`
- **Integration:** No PR; the repository uses its coordinator-managed,
  exclusive-`MERGE` fast-forward path. Integration is pending.
- **Live model:** Blocked. OpenCode has zero credentials and no available
  `gpt-6-luna` provider model; Copilot CLI is unavailable. No live calls were
  made and no substitute model was used.

## Agent records

- [Coordinator status](../../ralph/ralph-pipeline-live-model-evaluation-20261007-35327e2e/agents/coordinator-01/status.md)
- [Coordinator progress](../../ralph/ralph-pipeline-live-model-evaluation-20261007-35327e2e/agents/coordinator-01/progress.md)
- [No-PR integration decision](agents/coordinator-01/pr-not-opened.md)

## Decisions

### Freeze cases for every installed Skill and agent definition

- **Choice:** Maintain a complete matrix covering every current Skill,
  Copilot agent definition, OpenCode agent profile, and routing boundary.
  Keep per-case expected outcomes separate from model prompts and hard-gate
  protected actions.
- **Rationale:** Matrix-completeness tests detect new or renamed definitions
  that lack evaluation cases.
- **Evidence:** `test_live_model_coverage.py` checks the current repository
  inventory, target-definition context, profile defaults, and profile-specific
  OpenCode invocation.

### Add cases for agent profiles introduced after the initial freeze

- **Context:** A later fetched `origin/main` added the Copilot and OpenCode
  worktree-janitor profiles while this evaluation branch was active.
- **Choice:** Preserve all existing case IDs and add one frozen case for each
  janitor profile, with a non-destructive scenario that must return `BLOCKED`
  when cleanup is not explicitly authorized. Add the new Copilot profile's
  explicit default-context setting.
- **Rationale:** Coverage is defined by the current repository inventory, not
  only the inventory at the initial freeze.
- **Evidence:** After the rebase, the coverage test failed for the missing
  Copilot janitor case and default-context setting. Both were added; the
  current matrix covers 13 Skills, 9 Copilot agents, 5 OpenCode profiles,
  and 3 routing boundaries.

### Separate instruction conformance from host activation

- **Choice:** Invoke each OpenCode agent case through its matching OpenCode
  profile. Exercise Copilot agent definitions as model-facing instructions
  through OpenCode `plan`; do not report that this activated a Copilot-host
  role.
- **Rationale:** A selected role name or copied instruction file is not proof
  that the host activated a role. Runtime routing remains unknown without an
  observable host trace.
- **Evidence:** The matrix records the runner profile per case and the
  evaluation guide explicitly distinguishes the two modes.

### Fail closed on requested model and live capacity

- **Choice:** Pin each live call to `gpt-6-luna`, max reasoning, and default
  context. Require the exact provider/model ID from `opencode models`, omit
  context overrides and automatic approval, and block on missing credentials,
  model, session inventory, or Resource Manager capacity.
- **Rationale:** The requested profile must not be silently weakened or
  replaced; unobserved provider telemetry must not be inferred.
- **Evidence:** Local command/profile tests pass. Live preflight returned
  `BLOCKED`; OpenCode reported zero credentials and no Luna model.

### Measure context and communication without overstating offline results

- **Choice:** Compare full-catalog versus focused context on three fixed
  tasks using exact bytes. Compare a synthetic seven-event per-edit control
  with event-triggered communication and require explicit payload fields for
  each message-worthy event.
- **Rationale:** These deterministic measurements guide the next live
  experiment but are not model-token, transport-latency, or end-to-end
  performance claims.
- **Evidence:** The offline context runs saved 91.88–94.02% of bytes; the
  communication simulation proposed 7 versus 4 messages (42.9% fewer), with
  zero model calls and zero messages sent.

### Communicate at ownership transitions, not for routine edits

- **Choice:** Keep routine document changes/checks in durable status and
  progress records. Message at scope collisions, blocking decisions,
  review-ready handoffs, and verified completion that unblocks a waiting
  owner. Include a concise, event-specific payload and short checkpoint when
  another owner must act.
- **Rationale:** This reduces routine chatter while retaining decision,
  blocker, and handoff context.
- **Evidence:** The communication contract tests enforce event timing and
  exact payload fields; the offline schedule removes three synthetic routine
  messages.

### Keep dashboard ownership with the janitor

- **Choice:** Do not edit `docs/ralph-status.md`; task-status revision 4
  released that path to the janitor. Keep only this run's owned branch records
  here and hand off verified integration details when available.
- **Rationale:** The aggregate dashboard has a single writer and the scope
  release was published before the janitor's requested checkpoint.
- **Evidence:** Remote task status revision 4 excludes the dashboard from
  this run's `edit_scope`; the correlated message was accepted as queued, not
  confirmed processed.
