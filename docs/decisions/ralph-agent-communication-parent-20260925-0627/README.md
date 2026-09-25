# Agent Communication Iteration Decisions

- **Run ID:** `copilot-skills-agent-communication-20260925-0627`
- **Branch:** `ralph/agent-communication-parent-20260925-0627`
- **Parent worktree:** `/Users/jrblankenhorn/copilot_skills.worktrees/ralph-agent-communication-parent-20260925-0627`
- **Base `origin/main` SHA:** `20293c720b18a1a21ff150f566823493b7a2717d`
- **Implementation commit:** `15638054cffca7eb054cff80430ff2998d97a3df`
- **Agents:** `coordinator`, `worker-01`, `worker-02`
- **Integration:** Pending; use coordinator-reviewed, verified fast-forward
  without a PR, as documented by the repository.
- **Memory review:** Pending

## Agent records

- [Coordinator / benchmark and integration](agents/coordinator/pr-not-opened.md)

## Decisions

### Use the documented no-PR fast-forward path

- **Context:** The active Ralph Loop guidance specifies a
  coordinator-managed, verified fast-forward without a PR for this repository.
- **Alternatives:** Open a PR outside the normal path, or push to `main`
  without the required exclusive-main reservation.
- **Choice:** Do not open a PR. Rebase and retest the parent against the
  latest fetched `origin/main`, then perform a coordinator-reviewed
  fast-forward under the `MERGE` reservation and verify the resulting remote
  SHA.
- **Rationale:** This follows the repository's documented integration path
  without bypassing the main ownership and verification gates.
- **Consequence:** Worker leaves remain `AWAITING_MERGE` until remote-main
  integration and post-merge memory review are complete.

### Use a typed, asynchronous, session-addressed envelope

- **Context:** VS Code session documentation describes separate conversations;
  the available host message bridge routes by session URI and returns
  asynchronously.
- **Alternatives:** Use a shared file mailbox; ask the coordinator to relay
  every message; share full transcripts.
- **Choice:** Define a small `agent-message/v1` envelope addressed to one
  verified session, with correlation/acknowledgment and artifact references.
  Treat full transcript sharing and file polling as fallback-only.
- **Rationale:** Direct routing avoids serial coordinator relays while bounded
  envelopes reduce context and latency.
- **Consequence:** The interface must distinguish transport acceptance from
  recipient acknowledgment and task completion.

### Do not claim hard interruption without a host cancellation primitive

- **Context:** The session bridge available in this host queues messages for
  busy sessions; the Copilot SDK's documented `immediate` mode is steering,
  not a guaranteed hard cancel.
- **Alternatives:** Call every urgent message an interrupt; require short
  polling intervals; expose an explicit optional host interrupt operation.
- **Choice:** Specify cooperative `interrupt` messages plus an optional
  `requestInterrupt` capability. Return `UNSUPPORTED` or `QUEUED` when
  preemption is unavailable and use the session Stop control for a hard stop.
- **Rationale:** A skill cannot create host-level preemption and must not
  promise it.
- **Consequence:** A true interrupt SLA requires implementation by the
  session host; the skill can improve routing, acknowledgments, and
  checkpoint responsiveness immediately.

### Keep the explicitly requested Copilot host for this run

- **Context:** Refreshed main now documents OpenCode as the default Ralph
  runtime, while the user specifically requested communication between
  sessions in Copilot's Agents window. This session exposes the Copilot-
  compatible session tools used in the benchmark.
- **Alternatives:** Switch to OpenCode, or describe the communication contract
  as universally available.
- **Choice:** Continue in this Copilot-compatible host and keep the skill
  capability-gated. Do not claim VS Code or every agent host has a general
  cross-session messaging API.
- **Rationale:** This preserves the user's explicitly selected target; the
  current environment also has no connected OpenCode providers.
- **Consequence:** Results apply to observed Copilot host capabilities only;
  other hosts must provide and verify their own adapter.

### Treat fixed or shared message-limit errors as route failures

- **Context:** Existing tooling memory records repeated, identical messaging
  cap failures across independent sessions and warns that new sessions do
  not bypass the shared limit.
- **Alternatives:** Retry after a delay, start another session, or keep
  relaying through the same capped tool.
- **Choice:** The skill will treat a reported message limit as a failed route,
  stop retries from new sessions, and direct the sender to an already
  available durable coordination channel.
- **Rationale:** Repeated attempts consume time and capacity without improving
  delivery confidence.
- **Consequence:** A test-first contract assertion is currently Red; worker-01
  will add the bounded fallback guidance before integration.

### Rebase onto the refreshed main before child integration

- **Context:** `origin/main` advanced by twelve commits while the benchmark
  and worker assignments were in progress; the updated main also added an
  independent PR review gate.
- **Alternatives:** Integrate the original parent tip and leave current main
  changes out; abandon the new run; rebase and retest.
- **Choice:** Rebase the clean, unpublished parent onto the refreshed
  `origin/main` and preserve both main's active code-review run and this
  run's dashboard entries.
- **Rationale:** The parent-child workflow requires the latest main before
  final integration; no-PR fast-forward runs are explicitly exempt from the
  new PR-only review gate.
- **Consequence:** Both workers must rebase from their original parent base
  onto the current parent tip and rerun scoped checks before integration.

### Reconcile later status-only main advances before dispatch

- **Context:** After the parent rebase onto
  `16b98ea828d1c25efeeb07f0bacbd19add71804c`, main advanced to
  `5d87b5289aeac271696df3ce2c3201e0b631c3c3`; the intervening changes were
  limited to ownership/status metadata.
- **Alternatives:** Ignore the new main tip, merge stale worker leaves, or
  rebase the unpublished parent and verify the replay.
- **Choice:** Rebase the clean parent onto the latest fetched `origin/main`,
  retain every active dashboard entry, and rerun the targeted Red check.
- **Rationale:** Status-only commits are still part of the exact remote base;
  current worker attestations must refer to the refreshed parent.
- **Consequence:** All 45 commits mapped one-to-one in `git range-diff`;
  previous worker sign-offs are superseded and must be refreshed.
