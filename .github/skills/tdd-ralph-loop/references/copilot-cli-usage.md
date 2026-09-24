# Copilot agent selection and model controls

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

## Ralph Loop defaults

The Ralph Loop agent frontmatter sets `reasoning-effort: max`. The selected
model must support that level; otherwise, the harness may report it as
unsupported and leave its effort unchanged.

Copilot CLI reads repository defaults from `.github/copilot/settings.json`.
This repository pins `contextTier` to `default`, including for Ralph Loop
subagent invocations. The repository-wide setting applies to Copilot CLI
sessions in this repository; custom-agent frontmatter does not expose a
context-tier field. In VS Code, use the model picker to select the context
tier for the active session if needed.

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
