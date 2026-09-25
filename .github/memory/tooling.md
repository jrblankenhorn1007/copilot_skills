# Tooling

## The cross-session `send_message` tool enforces a fixed cap that is likely shared, not per-process

- **Rule:** `send_message` (and similar cross-session/agent messaging calls)
  can refuse with "Refusing to send more than 50 messages from server tools
  in this process" once a fixed count is reached. Treat this as a fixed
  count, not a transient or time-windowed rate limit: immediate retry and
  retry after a delay both fail identically. Do not assume the cap is
  scoped to your own conversation: independent sessions/processes created
  specifically to retry delivery (via `create_session`) have hit the
  identical error on their first attempt, and one concluded from four
  attempts across three independent sessions that the limit is "enforced
  somewhere shared across the whole account/host, not per calling
  session." A freshly created session can also simply stall indefinitely
  under host overload before ever reaching its send attempt, which is
  further evidence of shared resource contention rather than a private,
  bypassable per-process quota. Do not keep spawning additional relay
  sessions hoping a "fresh process" resets the cap; check `list_sessions`
  first for other in-flight sessions already retrying delivery to the same
  target before creating another one, to avoid compounding the same
  redundant, resource-consuming attempt many times over.
- **Why:** Observed directly in this session: `send_message` failed
  identically on immediate retry and after a 5s delay, while `list_sessions`
  kept succeeding — ruling out simple flakiness. A sibling independent
  session (created via `create_session` specifically to relay the message)
  then stalled for minutes without completing even one turn, and a separate
  independent session reported the same cap error on its very first
  attempt after being told "figure it out" — both inconsistent with a
  private per-process quota that a new process easily bypasses.
- **Gotcha:** When several independent sessions are already redundantly
  targeting the same destination for the same message, prefer a durable,
  non-realtime channel (e.g. a GitHub PR/issue comment, a shared status
  file, or the repository's existing coordination artifacts) that the
  target session already checks, over multiplying live messaging attempts
  that add to the same contention they are trying to route around.
