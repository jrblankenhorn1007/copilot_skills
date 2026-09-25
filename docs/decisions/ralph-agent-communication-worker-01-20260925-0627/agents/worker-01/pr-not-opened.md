# Worker-01 Branch Decision Record

- **Run/task/agent/iteration:** `copilot-skills-agent-communication-20260925-0627` /
  `agent-communication-skill` / `worker-01` / 1
- **Runtime agent ID:** `4b590f58-600f-4d99-92b7-29db9c14b7a4`
- **Branch:** `ralph/agent-communication-worker-01-20260925-0627`
- **Worktree:** `/Users/jrblankenhorn/copilot_skills.worktrees/ralph-agent-communication-worker-01-20260925-0627`
- **Parent branch/worktree:** `ralph/agent-communication-parent-20260925-0627` /
  `/Users/jrblankenhorn/copilot_skills.worktrees/ralph-agent-communication-parent-20260925-0627`
- **Run `origin/main` base:** `20293c720b18a1a21ff150f566823493b7a2717d`
- **Base parent SHA:** `0294550c92a5d79e1cca682a0c509b5bb6eca3fd`
- **Implementation commit:** `fc3a416cf1543f771c84d066080f8d603b8030be`
- **Pull request:** `NOT_OPENED`; this child is handed to the coordinator for
  serial parent integration under the assigned no-PR path.

## Decisions

### Route only to a verified session

- **Context:** A message must reach the intended task owner without flooding
  unrelated sessions or relying on a guessed title or workspace.
- **Alternatives:** Broadcast to active agents; route by display name; ask the
  coordinator to relay every message.
- **Choice:** Find one candidate with `list_sessions`, verify its assignment
  with available session metadata/context, then address its exact session
  identifier. Use a coordinator fallback relay if no unique target or tool is
  available.
- **Rationale:** Exact routing avoids accidental disclosure and unnecessary
  relay latency while preserving a safe fallback.
- **Consequence:** The sender must not claim a message was delivered when the
  route cannot be verified.

### Keep delivery, processing, completion, and interruption distinct

- **Context:** Host acceptance or queueing does not prove recipient
  processing, and queued messages do not stop a busy turn.
- **Alternatives:** Treat “Message sent” as an acknowledgment; retry when no
  reply appears; call every urgent message a hard interrupt.
- **Choice:** Define separate `accepted`, `queued`, `received`, `expired`, and
  `failed` states; require recipient processing and result acknowledgments
  for their respective claims; treat `interrupt` as cooperative unless a
  verified host cancellation primitive confirms a hard stop.
- **Rationale:** Status must reflect evidence the host or recipient actually
  provides.
- **Consequence:** Keep senders productive with short checkpoints and relay
  or re-plan instead of blocking for a delayed reply.

### Use the specified no-PR integration path

- **Context:** The parent dashboard assigned this worker
  `pr-not-opened.md`; worker branches are integrated serially into the parent.
- **Alternatives:** Open a child PR or merge directly into `origin/main`.
- **Choice:** Open no worker PR and leave child-to-parent integration to the
  coordinator. Do not publish, merge, or clean up this branch.
- **Rationale:** This preserves path ownership and the run's parent/child
  integration protocol.
- **Consequence:** The worker remains `AWAITING_MERGE` until the coordinator
  verifies integration.

### Reject expired instructions regardless of priority

- **Context:** A live experiment observed an urgent cooperative interrupt
  arrive after `expires_at`; the test agent still acted on the stale message.
- **Alternatives:** Treat urgency as permission to act after expiry; leave
  expiry advisory; reject stale work but omit an acknowledgment.
- **Choice:** At receipt, dequeue, and immediately before acting, reject any
  message whose `expires_at` is reached; send a correlated `expired`
  acknowledgment even when `ack_required` is false; perform no requested
  action or side effect; and escalate safety-critical content through a
  current, verified coordinator/operator channel.
- **Rationale:** Queueing can deliver a message after its validity window, and
  priority does not provide cancellation or preemption.
- **Consequence:** The receiver rejects stale urgent interrupts as well as
  ordinary requests. The escalation reports risk without authorizing the
  expired instruction.

## Integration note

At worker sign-off, the parent branch tip observed was
`d8b3992af53a292a83ff094c5cd9837670ea968d`, later than the child's
`base_parent_sha`. This child has not been rebased
(`rebased_onto_parent_sha: null`). The coordinator's current status calls for
rebasing children onto the current parent tip before serial integration and
rerunning their scoped checks. No child-to-parent merge is claimed here.

## Verification and signature

- Documentation-only change; TDD Red/Green/Refactor was not applicable.
- Expiry-handling audit: `PASS` (15 requirements; exact command is recorded
  in the worker progress file).
- `git diff --check` against the supplied child base: `PASS`.
- `git diff --cached --check`: `PASS`.
- Required communication-contract vocabulary audit: `PASS` (25 terms; exact
  command is recorded in the worker progress file).
- Worker sign-off is `SELF_ATTESTATION`; it is
  `NOT_CRYPTOGRAPHICALLY_SIGNED`. No commit signature was verified.
- Recovered audit issue: the first literal-substring check failed on two
  newline/wording mismatches; the rule was clarified and the whitespace-
  normalized 15-statement audit passed. Details and exact commands are in
  `docs/ralph/ralph-agent-communication-worker-01-20260925-0627/agents/worker-01/progress.md`.
- No unresolved implementation blockers.
