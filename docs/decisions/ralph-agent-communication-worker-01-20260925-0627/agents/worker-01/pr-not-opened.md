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
- **Rebased onto parent SHA:** `44a262954564a058436bd4115908605e67302d5f`
- **Implementation commit:** `d3cea422a910442d85a4a6715ea46d25c5f49cdf`
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

### Separate task-result deadline from reply checkpoint

- **Context:** Worker-02's pipeline contract defines `deadline` as the
  task-result due time and `reply_deadline` as a sender checkpoint.
- **Alternatives:** Keep only `reply_deadline`; overload it for both task
  completion and sender progress; add a separate result deadline.
- **Choice:** Include both fields in `agent-message/v1`; define `deadline` as
  the task-result due time and `reply_deadline` as the sender-checkpoint due
  time. Keep `expires_at` as the instruction-validity limit.
- **Rationale:** A delayed checkpoint must not be mistaken for a missed task
  result deadline, and neither deadline replaces expiration.
- **Consequence:** Receivers can report progress independently from task
  completion while preserving the existing stale-message rejection rule.

## Integration history

At the original worker sign-off, the observed parent tip was
`d8b3992af53a292a83ff094c5cd9837670ea968d`, later than the child's original
`base_parent_sha`. The coordinator subsequently rebased this clean child onto
`3281d44d72fa4bfa188d4ca288bee9f249b1fd4f`; at that checkpoint the child
verified that SHA was an ancestor. The original
`base_parent_sha` remains `0294550c92a5d79e1cca682a0c509b5bb6eca3fd`.

The coordinator later rebased the parent onto
`origin/main` `91a6f78fa00cde80a80bea630a763d74041a56ad`; its current parent
worktree `HEAD` is `44a262954564a058436bd4115908605e67302d5f`, which is an
ancestor of this child's rebased branch. The latest prompt's longer proposed
SHA `44a2629d72fa4bfa188d4ca288bee9f249b1fd4f` did not resolve to a Git
object; the verified parent-worktree SHA, sharing the stated `44a2629`
prefix, is recorded as `rebased_onto_parent_sha`. The current implementation
commit is `d3cea422a910442d85a4a6715ea46d25c5f49cdf`. No additional worker
rebase or child-to-parent merge is claimed here.

## Verification and signature

- Documentation-only change; TDD Red/Green/Refactor was not applicable.
- Expiry-handling audit: `PASS` (15 requirements; exact command is recorded
  in the worker progress file).
- Envelope/deadline audit: `PASS` (37 requirements; exact command is recorded
  in the worker progress file).
- `git diff --check` against the rebased parent base: `PASS`.
- `git diff --cached --check`: `PASS`.
- Required communication-contract vocabulary audit: `PASS` (25 terms; exact
  command is recorded in the worker progress file).
- Worker sign-off is `SELF_ATTESTATION`; it is
  `NOT_CRYPTOGRAPHICALLY_SIGNED`. No commit signature was verified.
- Recovered audit issue: the first literal-substring check failed on two
  newline/wording mismatches; the rule was clarified and the whitespace-
  normalized 15-statement audit passed. Details and exact commands are in
  `docs/ralph/ralph-agent-communication-worker-01-20260925-0627/agents/worker-01/progress.md`.
- Recovered command issue: one final audit invocation had a Python
  `SyntaxError` from shell escaping around the quoted `priority: "urgent"`
  literal. Rebuilt the term with `chr(34)` and reran the 37-term audit
  successfully; no contract text was changed in response to that error.
- Final rebased-base whitespace verification:
  `git diff 3281d44d72fa4bfa188d4ca288bee9f249b1fd4f...HEAD --check` —
  `PASS`.
- Coordinator's verbatim rerun found a recorded 37-term audit variant omitted
  the Markdown backticks from the two explanatory literals for `deadline`
  and `reply_deadline`. The variant was corrected and rerun against the
  unchanged skill: **PASS, 37/37**. The exact command and current rebased-base
  whitespace result are recorded in the latest worker progress entry.
- Current parent-ancestry check:
  `git merge-base --is-ancestor 44a262954564a058436bd4115908605e67302d5f HEAD`
  — `PASS`.
- Current rebased-base whitespace check:
  `git diff 44a262954564a058436bd4115908605e67302d5f...HEAD --check` —
  `PASS`.
- Fresh worker sign-off is `SELF_ATTESTATION` for implementation commit
  `d3cea422a910442d85a4a6715ea46d25c5f49cdf`; it is not cryptographically
  signed.
- No unresolved implementation blockers.
