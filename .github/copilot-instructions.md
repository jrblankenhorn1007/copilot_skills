# Shared agent resource policy

Before doing task work, each agent must register itself with the shared local
registry described in the
[Resource Manager skill](skills/resource-manager/SKILL.md). This includes the
top-level orchestrator and every worker or nested subagent.

Before launching a child, refresh the host's active-agent inventory and
atomically reserve a registry slot. The orchestrator counts toward the limit.
If there is no slot, the registry or resource metrics are unavailable, or the
active-agent inventory is unknown, do not spawn; queue or serialize the work
instead. A child activates the reservation before other work. Heartbeat active
registrations and release them when work ends or pauses.
