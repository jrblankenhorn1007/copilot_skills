# Agent Communication Pipeline Decisions

- **Run ID:** `copilot-skills-agent-communication-20260925-0627`
- **Task ID:** `agent-session-pipeline-contract`
- **Branch:** `ralph/agent-communication-worker-02-20260925-0627`
- **Parent branch/worktree:** `ralph/agent-communication-parent-20260925-0627` /
  `/Users/jrblankenhorn/copilot_skills.worktrees/ralph-agent-communication-parent-20260925-0627`
- **Assigned `base_parent_sha`:**
  `0294550c92a5d79e1cca682a0c509b5bb6eca3fd`
- **Rebased onto parent:** `808bc8819c898d27db9a22dcc670b96c953780b4`
- **Implementation commit:**
  `d1ec345fd930a83c5e5b879a09dd1c298fcffea4`
- **Integration:** Pending coordinator action; no PR is part of the worker's
  assigned path.

## Agent records

- [Worker-02 — no PR](agents/worker-02/pr-not-opened.md)

## Decisions

### Keep the transport capability-gated and asynchronous

- **Context:** The available host bridge exposes `list_sessions`,
  `send_message`, and `get_session_context`; its send operation is
  asynchronous and queues messages for busy sessions. Ordinary VS Code
  session documentation does not promise a cross-session messaging API.
- **Alternatives:** Promise automatic session messaging or hard cancellation;
  treat transport acceptance as receipt; serialize all communication through
  a shared mailbox.
- **Choice:** Specify discovery, one-session addressing, delivery versus
  recipient receipt/completion states, optional interruption outcomes, and a
  coordinator-relay fallback. Align the typed envelope with the sibling
  Agent Communication skill.
- **Consequence:** Hosts without the advertised capability must not claim
  direct delivery or preemption; the durable worker progress/status protocol
  remains authoritative.

### Keep communication evidence in the existing progress log

- **Context:** The project has one coordinator-owned aggregate dashboard and
  branch/agent progress leaves.
- **Alternatives:** Add another benchmark dashboard or copy full message
  transcripts into the status snapshot.
- **Choice:** Record compact timing, outcome, and check evidence in
  `progress.md`; retain only the normal status summary and leaf links in the
  aggregate dashboard.
- **Consequence:** Measurement remains auditable without duplicating or
  exposing private message content.

### Reject expired instructions even when marked urgent

- **Context:** A live experiment delivered an urgent interrupt after its
  `expires_at`, and the test agent still acted on it.
- **Alternatives:** Treat urgent priority as an expiry override; rely on the
  host to retract queued messages; or permit stale actions while merely
  reporting that they were late.
- **Choice:** Require recipients to check expiry before acting, acknowledge an
  expired request in a correlated `kind: "ack"` stating `expired`, perform no
  requested action or side effect, and escalate safety-critical requests to
  the coordinator/authorized owner for fresh instructions. State that urgent
  priority does not imply preemption or override expiry.
- **Consequence:** A late queued instruction cannot be revived by priority;
  critical work must be revalidated through a current, unexpired request.

### Require processing confirmation before claiming work started

- **Context:** The coordinator's updated test requires a distinct
  acknowledgment lifecycle and an explicit task `deadline`.
- **Alternatives:** Treat transport acceptance as recipient processing; use
  one undifferentiated acknowledgment for send, receipt, and completion; fold
  the task deadline into the expiration cutoff.
- **Choice:** Specify `accepted`/`queued`/`failed` as transport states, a
  correlated recipient processing acknowledgement, and a separate correlated
  completion result. Add `deadline` for the task-result due time while keeping
  `reply_deadline` as the sender checkpoint and `expires_at` as the validity
  cutoff.
- **Consequence:** Transport acceptance without a processing acknowledgement
  remains unconfirmed, and a task deadline cannot revive an expired request.

### Use the shared deadline meaning and one README skill entry

- **Context:** The integrated Agent Communication skill now includes the
  shared `deadline` field, so describing it as a Ralph-only addition would be
  stale. The refreshed README also contains the dedicated Agent Communication
  entry alongside Ralph PR Review.
- **Choice:** Describe `deadline` as the shared task/result due time and
  `reply_deadline` as the sender checkpoint. Keep one dedicated Agent
  Communication README bullet and preserve Ralph PR Review.
- **Consequence:** The pipeline example remains aligned with the integrated
  skill without duplicate skill index entries.
