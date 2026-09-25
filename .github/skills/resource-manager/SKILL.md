---
name: resource-manager
description: Register agents and gate concurrent agent spawning through a shared, hardware-aware local registry.
---

# Resource Manager

Use this skill whenever an agent starts work or may start another agent,
including orchestrators and nested subagents. The orchestrator counts toward
the same limit as every worker and subagent. A requested worker count is an
upper bound; it never overrides the live resource limit.

## Shared registry

The CLI stores live registrations in
`~/.copilot/agent-resource-manager/registry.json` and serializes updates with
`registry.lock`. All local agent worktrees on the same host use that one
directory, so reservations are visible across sessions and are not committed
to a project. The directory and registry files are private to the current
user. Do not put the registry in a worktree, repository, per-session folder,
or temporary directory.

If agents use different home directories, set
`COPILOT_AGENT_RESOURCE_MANAGER_DIR` to the same shared, host-local directory
for every session. Do not use a network filesystem or continue when the shared
path or atomic lock is unavailable. The manager supports macOS and Linux and
fails closed when it cannot read resource metrics or update the registry.
When working in a project without this skill installed, invoke the script from
the canonical `copilot_skills` checkout; do not create a separate per-project
registry or run divergent copies of the manager.

## Dynamic capacity

The manager computes a total-agent limit from physical memory, logical CPU
cores, currently available memory, and one-minute system load:

- Reserve 4 GiB for the OS and editor, budget 2 GiB per agent, and cap the
  memory-derived limit at four agents.
- Budget one agent per two logical CPU cores, also capped at four.
- The base limit is the lower of the memory and CPU limits.
- Reduce the limit by one (minimum one) when available memory is below 3 GiB
  or one-minute load reaches 85% of logical CPU count.
- Allow no new registration or reservation when available memory is at or
  below 1.5 GiB or one-minute load reaches logical CPU count.

For example, an 8 GiB, six-core Mac has a base limit of two total agents, not
two workers plus an orchestrator. Live pressure can reduce that to one or zero.
The active count is the union of registered agents, pending reservations, and
currently observed live sessions not already represented by a registration.
This includes nested agents. Existing agents are never terminated when
pressure rises; the manager only refuses additional registrations or
reservations.

On macOS the manager reads `sysctl hw.memsize`, `memory_pressure`, and the
one-minute load average. On Linux it reads `MemTotal`/`MemAvailable` from
`/proc/meminfo` and the one-minute load average. The load average is a
conservative host-load proxy, not a per-process CPU measurement.

## Start, reserve, and release

1. Query the host's live session list and active subagent list when available.
   Include every in-progress agent, including this orchestrator and nested
   agents; do not infer that an empty registry means no agents are running.
2. Register this agent before doing task work. Use its runtime session ID as
   both `agent-id` and `runtime-id`, and pass the observed live IDs:

   ```sh
   python3 .github/skills/resource-manager/scripts/resource_manager.py status \
     --observed-session "<orchestrator-session-id>" \
     --observed-session "<other-live-session-id>"

   python3 .github/skills/resource-manager/scripts/resource_manager.py register \
     --agent-id "<orchestrator-session-id>" \
     --runtime-id "<orchestrator-session-id>" \
     --role orchestrator \
     --observed-session "<orchestrator-session-id>" \
     --observed-session "<other-live-session-id>"
   ```

   For a worker, use `--role worker`; for other agents use `agent` or
   `subagent`. If this agent was already visible in the live-session snapshot,
   registering it records the existing agent without counting it twice. An
   already-running agent may register while the machine is over capacity, but
   it must not spawn more agents until a slot is available.

3. Before every spawn, refresh the live-session inventory and reserve the
   child's slot. The reservation is atomic with the capacity check and counts
   immediately:

   ```sh
   python3 .github/skills/resource-manager/scripts/resource_manager.py reserve \
     --agent-id "<run-id>/worker-01" \
     --parent-id "<orchestrator-session-id>" \
     --role worker \
     --observed-session "<orchestrator-session-id>" \
     --observed-session "<other-live-session-id>"
   ```

   Pass the returned `reservation_id` and `agent_id` to the child. It must
   activate that reservation before other work:

   ```sh
   python3 .github/skills/resource-manager/scripts/resource_manager.py activate \
     --agent-id "<run-id>/worker-01" \
     --reservation-id "<reservation-id>" \
     --runtime-id "<worker-session-id>"
   ```

   If reservation fails, do not spawn. Queue or serialize the remaining work;
   do not lower the cap, omit the orchestrator, or launch an unregistered
   child. Any registered agent may reserve a child only when its task and
   orchestration rules authorize delegation.

4. Run `status` to inspect the hardware snapshot, capacity, registered agents,
   reservations, observed-but-unregistered sessions, and free slots. A stale
   live-session inventory makes `can_spawn` false; refresh it before trying
   again.
5. Heartbeat a live registration after meaningful work and before or after
   long-running tool operations:

   ```sh
   python3 .github/skills/resource-manager/scripts/resource_manager.py heartbeat \
     --agent-id "<registered-agent-id>"
   ```

   Release the agent's registration when it completes, is cancelled, or
   pauses for user input. If spawning fails, cancel the reservation using its
   reservation ID:

   ```sh
   python3 .github/skills/resource-manager/scripts/resource_manager.py release \
     --agent-id "<run-id>/worker-01" \
     --reservation-id "<reservation-id>"
   ```

Active leases expire after 30 minutes without a heartbeat; unclaimed
reservations expire after five minutes. Treat expiry as crash recovery, not a
normal release path. If the host cannot provide a complete live-agent
inventory, the shared directory is inaccessible, or resource metrics are
unknown, do not spawn agents. Report the constraint and proceed serially where
possible.

The registry is local admission control, not permission to delegate. Follow
the active agent definition, user request, and project workflow for which
agents may be launched and what work they may perform.
