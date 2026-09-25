# Agent Communication Baseline

## Goal and known answer

Measure whether session messaging preserves correctness and improves handoff
time on a deterministic task with a known result:

```text
sum(1..100) = 100 * 101 / 2 = 5050
sum(1..50) = 1275
sum(51..100) = 3775
1275 + 3775 = 5050
```

This is a protocol smoke benchmark, not evidence that multi-agent work is
faster for every workload. All measurements below were made on 2026-09-25 in
Copilot's Agent Host using session/chat messaging tools. The independent
single-agent session start and model-inference timestamps are not exposed, so
some timings are upper bounds or intervals rather than precise latency
percentiles.

## Measured results

| Variant | Delivery/ack observation | Task result | Interpretation |
| --- | --- | --- | --- |
| Single-agent baseline | The one-turn computation was visible by 07:05:14Z; its exact start time was not captured. | `5050` (formula and independent pairing check). | Correct baseline; timing precision is insufficient for a speedup claim. |
| Communicating baseline: busy target / queued message | `send_message` returned **Message queued**. The recipient processed `bench-20260925-01` at 07:01:49Z. The actual send was after 06:57:37Z and before 06:59:49Z, so observed enqueue-to-processing latency was between 120 and 252 seconds. | `5050`; the reply missed its 07:00:00Z reply deadline by 109 seconds but arrived before expiry. | Delivery is asynchronous for the sender, but recipient processing waits for its current turn. |
| Urgent interrupt probe | `send_message` again returned **Message queued**. The `urgent` interrupt was processed at 07:02:22Z, 153 seconds after its 06:59:49Z timestamp and 93 seconds after expiry. | The target retained `3775` and acknowledged a cooperative stop. No external action was involved. | Priority did not preempt the busy turn. The target acted on an expired message; the skill must instead reject/ack expired instructions without acting. This is not a hard interrupt. |
| Ready-target optimization | The receiver finished its small preparation task and reported `READY B=3775`. `send_message` returned **Message sent** (not queued) for `bench-20260925-optimized-01` at 07:05:14Z; the correct acknowledgment was visible by 07:07:02Z (at most 108 seconds). | `5050`, with message ID acknowledged. | Dispatch to a ready recipient avoided the busy-queue delay. The remaining response time is model-turn latency, not sender-side blocking. |
| Direct peer-to-peer handoff | Chat A sent `bench-20260925-peer-result-01` directly to chat B; the sender observed **Message sent** and did not wait for the reply. The peer acknowledgment/result was visible by 07:13:09Z; the exact send timestamp was not exposed. | `5050`, with the peer message ID and correlation acknowledged. | The host routed chat-to-chat without a coordinator relay. This experiment used two chat targets in one Agent Host session, not two independent worktrees or remote sessions. |
| Independent-session dispatch probe | Created a separate Agent Host session and sent a bounded `agent-message/v1` request to its session URI. `send_message` returned **Message sent**. By 07:31:25Z, `get_session_context` still exposed no conversation or processing acknowledgment; no retry was issued. | No result was observable; excluded from correctness and latency comparisons. | The sender-side acceptance result does not prove delivery or processing. Keep the request unconfirmed, do not resend automatically, and surface the missing acknowledgment. |

The ready-target run is a single sample and differs from the busy-target
variant in recipient state; it demonstrates the effect of avoiding an
in-progress turn, not a statistically controlled speedup. The arithmetic is
too small to justify two agents on its own: task parallelism pays off only
when independent work outweighs session startup, messaging, and integration
costs.

## Optimization loop and stopping point

1. **Baseline:** A single session computed `5050` correctly. A message to a
   busy session was queued; its response missed the requested reply deadline.
   An urgent interrupt was also queued and arrived after its expiry.
2. **Refinement:** The receiver was given a bounded preparatory task and sent
   a `READY` checkpoint before the dependent message. The host reported
   `Message sent` rather than `Message queued`; the same known result and
   message acknowledgment were obtained.
3. **Diminishing returns:** Direct peer routing removes the coordinator relay,
   but prompt/schema changes cannot make this host's queued message preempt an
   active turn. The useful skill-level optimization is to send concise
   addressed messages asynchronously, schedule dependent work at explicit
   ready/checkpoint boundaries, and avoid blocking the sender for a reply.
   Three bounded variants preserved the known answer. A separate-session
   dispatch was accepted by the transport but had no visible processing
   acknowledgment during observation, so it was not counted as a successful
   result and was not retried. Further prompt-only tuning cannot provide a
   hard interrupt guarantee or turn transport acceptance into proof of
   processing. A host adapter exposing steering/cancellation is required for
   hard interruption and must be benchmarked separately.

## Metric contract for future runs

Record each message's `sent_at`, transport result (`accepted`, `queued`, or
`failed`), delivery latency, recipient `received_at`, recipient
acknowledgment time, and task completion time separately. Also record
correctness against the known result and whether
the recipient was idle, at a checkpoint, or in an active turn. Do not call a
transport acceptance an acknowledgment or a queued prompt an interruption.
Use at least five repetitions for a latency comparison, report median and
range, and stop a refinement when it does not improve completion time without
reducing correctness, safety, or auditability. Do not report a speedup from
the single samples above.

## Platform sources

- [VS Code Agents window](https://code.visualstudio.com/docs/agents/run/agents-window)
- [Manage agent sessions in VS Code](https://code.visualstudio.com/docs/agents/run/sessions/manage-sessions)
- [GitHub Copilot custom agents and sub-agent orchestration](https://docs.github.com/en/copilot/how-tos/copilot-sdk/features/custom-agents)
- [Copilot SDK steering and queueing](https://github.com/github/copilot-sdk/blob/main/docs/features/steering-and-queueing.md)
