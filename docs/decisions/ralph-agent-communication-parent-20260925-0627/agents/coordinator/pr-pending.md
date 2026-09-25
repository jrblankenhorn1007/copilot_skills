# Coordinator Branch Decision Record

- **Run/task/agent/iteration:** `copilot-skills-agent-communication-20260925-0627` /
  `communication-baseline` / `coordinator` / 1
- **Branch:** `ralph/agent-communication-parent-20260925-0627`
- **Base `origin/main` SHA:** `20293c720b18a1a21ff150f566823493b7a2717d`
- **Parent worktree:** `/Users/jrblankenhorn/copilot_skills.worktrees/ralph-agent-communication-parent-20260925-0627`
- **Implementation commit:** Pending
- **PR:** Pending; determine the repository's normal integration route before
  final integration.

## Decisions

- Use a typed, asynchronous, session-addressed message envelope; distinguish
  accepted, queued, received, and completed states.
- Keep hard cancellation separate from cooperative interrupt messages. The
  currently available `send_message` bridge queues for a busy target and
  cannot promise immediate preemption.
- Use `1..100 = 5050` as the deterministic known-answer task and measure
  single-agent and communicating-session runs before deciding whether the
  protocol improves end-to-end time.

## Recovered issues

- `origin/main` advanced after the initial refresh. The clean integration
  worktree was fast-forwarded and the parent was created from the newer
  fetched SHA `20293c720b18a1a21ff150f566823493b7a2717d`.
- The new contract test's expected Red is due to the missing skill and
  pipeline behavior; test discovery and execution succeeded.

## Unresolved blockers

- None.
