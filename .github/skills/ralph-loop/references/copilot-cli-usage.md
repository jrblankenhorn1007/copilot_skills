# Copilot CLI compatibility: Ralph Loop agent selection and model controls

Compatibility only: this guide describes the optional Copilot CLI runtime.
OpenCode is the default Ralph Loop runtime; see
[OpenCode setup](./opencode-setup.md) and the
[multi-agent orchestration guide](./multi-agent-orchestration.md) for the
supported default workflow.

This reference explains how to select the Ralph Loop agent and adjust the
available model reasoning and context options. Availability depends on the
selected Copilot harness, model, plan, organization policy, and CLI version.

## Select the Ralph Loop agent

The project agent is
[`.github/agents/ralph-loop.agent.md`](../../../agents/ralph-loop.agent.md). Its
frontmatter sets `user-invocable: true`, so it can appear in the agent picker.

- In VS Code, choose the intended **Session Target**, then select **Ralph
  Loop** from the **Agent** dropdown. Workspace agents are discovered from the
  workspace's `.github/agents/` folder.
- In interactive Copilot CLI, enter `/agent` and choose **Ralph Loop**.
- For a programmatic CLI invocation, use the agent file's basename without
  `.agent.md`:

  ```sh
  copilot --agent ralph-loop --model gpt-6-luna \
    --prompt "Implement one scoped task from the project plan"
  ```

If the workspace is not this repository, its `.github/agents/` file is not a
workspace-level agent for that session. For Copilot CLI/Agent Host sessions,
make the agent available across workspaces by placing the file at
`~/.copilot/agents/ralph-loop.agent.md`. Check for an existing same-name
personal agent before copying. Restart the CLI/Agent Host or start a new
session so it discovers the user-level file.

See the [Copilot CLI custom-agent guide](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli)
and [VS Code custom-agent guide](https://code.visualstudio.com/docs/agent-customization/custom-agents)
for supported locations and picker behavior.

## Configure orchestrator and worker profiles

The first Ralph Loop session is the orchestrator. The workspace agent does not
pin a reasoning-effort value, so configure the orchestrator's model and effort
in that initial session. Configure each worker's model and effort separately
when the worker session is launched. For example, an orchestrator and its
workers can use different CLI profiles:

```sh
copilot --agent ralph-loop --model gpt-6-astra --reasoning-effort high \
  --prompt "Coordinate the requested Ralph Loop task"

copilot --agent ralph-loop --model gpt-6-luna --reasoning-effort medium \
  --prompt "Implement the worker's bounded assignment"
```

These commands illustrate separate session settings; the orchestration host
must pass each worker profile when it creates that worker. In VS Code, choose
the orchestrator model in the active session's model picker and set worker
models through the host's per-worker session controls. Use only effort values
supported by the selected model.

`--orchestrator`, when used by a Ralph launcher, is a launcher-level/session
configuration option, not a native Copilot CLI flag; the official GitHub
Copilot CLI documentation does not document it. Do not append it to `copilot`
unless an external wrapper explicitly implements that option. Use the
documented Copilot agent and prompt options shown above; keep orchestration
role selection in the Ralph launcher or session host.

Copilot CLI reads repository defaults from `.github/copilot/settings.json`.
This repository configures `contextTier` separately for the top-level session
and `subagents.agents.Ralph Loop`, so the orchestrator and Ralph Loop workers
can use different context tiers. The agent frontmatter itself does not expose
a context-tier field. In VS Code, use the model picker for the active session;
use per-worker context controls only when the host supports them. If a host
cannot set a requested worker-specific context tier, report that limitation
and retain the configured default.

## Run a multi-agent Ralph task

In VS Code, select the [Ralph Loop](../../../agents/ralph-loop.agent.md)
agent. Its first top-level invocation acts as the orchestrator; include a
worker count in the task prompt:

```text
Implement the requested feature from the project plan. workers=3
```

The orchestrator treats `workers=N` as the requested number of concurrent
worker agents (default two), writes a split plan, and delegates independent
workstreams to **Ralph Loop** subagents. The orchestrator itself is not
counted. The host must enable the `agent/runSubagent` tool; if it is
unavailable, the orchestrator must report that limitation rather than claim
it launched the requested workers. Verify the run by checking the child-agent
calls and the per-worker entries in the project status snapshot.

The count is a prompt-level setting, not a standard agent-frontmatter field or
a universal Copilot worker-pool option. Copilot CLI's `/fleet` command can
parallelize decomposed work, but its documented interface does not guarantee
an exact user-selected worker count. Do not use `/fleet` alone when the task
requires exactly `N` verifiable Ralph Loop workers; use a host that permits
explicit subagent invocations or report the limit. See the
[VS Code subagent guide](https://code.visualstudio.com/docs/agents/run/subagents)
and the [Copilot CLI `/fleet` guide](https://github.blog/ai-and-ml/github-copilot/run-multiple-agents-at-once-with-fleet-in-copilot-cli/).

## Choose model, reasoning effort, and context

Model selection is separate from agent selection. In an interactive CLI, use
`/model` to choose a model and any reasoning-effort or context-window options
that model exposes. In VS Code, use the model picker for the selected
harness. These options are model-specific; not every model exposes every
level or context size.

Copilot CLI also exposes its validated user settings as parameters. Use
`/settings` to browse available keys and values, or use the inline forms:

```text
/settings
/settings show <key>
/settings <key> <value>
/settings reset <key>
```

Search the settings list for reasoning or context controls and use only the
keys and values shown by the installed CLI. The CLI validates these values and
writes supported user settings to `~/.copilot/settings.json`; repository
settings are stored in `.github/copilot/settings.json`. Names and choices can
vary by CLI version. The `/context` command reports current context usage and
capacity; it does not change the context window.

Custom-agent frontmatter supports the `reasoning-effort` field but not a
context-tier field. The Copilot CLI also supports `--reasoning-effort` (or
`--effort`) for programmatic sessions. Use only model-specific values accepted
by the selected model and harness.

Larger context windows and higher reasoning levels can consume more AI
credits. See GitHub's notes on
[configurable reasoning and larger context windows](https://github.blog/changelog/2026-06-04-larger-context-windows-and-configurable-reasoning-levels-for-github-copilot/),
the [Copilot CLI settings guide](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/change-settings),
and the [CLI programmatic reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-programmatic-reference).
