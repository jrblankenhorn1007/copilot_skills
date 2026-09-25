# Agent Communication Iteration Decisions

- **Run ID:** `copilot-skills-agent-communication-20260925-0627`
- **Branch:** `ralph/agent-communication-parent-20260925-0627`
- **Parent worktree:** `/Users/jrblankenhorn/copilot_skills.worktrees/ralph-agent-communication-parent-20260925-0627`
- **Base `origin/main` SHA:** `20293c720b18a1a21ff150f566823493b7a2717d`
- **Implementation commit:** `ce5d5c742ae5a9085c6db11695fa7570dad0ba5a`
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
