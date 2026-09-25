# Agent Communication Pipeline Decisions

- **Run ID:** `copilot-skills-agent-communication-20260925-0627`
- **Task ID:** `agent-session-pipeline-contract`
- **Branch:** `ralph/agent-communication-worker-02-20260925-0627`
- **Parent branch/worktree:** `ralph/agent-communication-parent-20260925-0627` /
  `/Users/jrblankenhorn/copilot_skills.worktrees/ralph-agent-communication-parent-20260925-0627`
- **Assigned `base_parent_sha`:**
  `0294550c92a5d79e1cca682a0c509b5bb6eca3fd`
- **Implementation commit:**
  `610910bcbfe87be3b681368a94e812dd6a35b4bb`
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
