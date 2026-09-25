# OpenCode setup

OpenCode is the default runtime for Ralph Loop in this repository. The CLI is
installed separately from the repository: there is no application dependency
manifest to update. Repository agent profiles live under `.opencode/agents/`;
Copilot CLI profiles under `.github/agents/` are compatibility-only.

## Install the CLI

Use the official installer:

```sh
curl -fsSL https://opencode.ai/install | bash
```

Or install with Homebrew:

```sh
brew install anomalyco/tap/opencode
```

For other platforms and package managers, use the official
[OpenCode installation guide](https://opencode.ai/docs/). Open a new terminal
if the installer changed `PATH`, then verify the CLI:

```sh
opencode --version
opencode agent list
```

Run these commands from the repository root so OpenCode discovers the
project's `.opencode/agents/` profiles. The `agent list` output should include
`ralph-loop`, `ralph-loop-worker`, `ralph-code-reviewer`, and
`ralph-security-reviewer`.

## Authenticate with a provider

OpenCode needs an account or API credential from a supported model provider.
Use its interactive login flow:

```sh
opencode auth login
```

Alternatively, start the TUI with `opencode` and use `/connect`. Choose a
provider and follow its sign-in instructions. `opencode auth list` shows
which providers are configured; it does not set up a provider by itself. See
the [OpenCode providers guide](https://opencode.ai/docs/providers/) for
provider-specific requirements.

Provider credentials are managed by OpenCode in the user's private local
configuration, not in this repository. Never paste keys into prompts, commit
credentials, or manually edit the credential store.

## Select a model and verify it

List the models available from configured providers:

```sh
opencode models
```

Use an exact `provider/model-id` from that list for a small smoke test:

```sh
opencode run --model provider/model-id \
  "Reply with exactly: OpenCode is ready."
```

Then verify the repository's primary Ralph profile:

```sh
opencode run --agent ralph-loop --model provider/model-id \
  "Read the Ralph Loop skill and summarize its preflight steps. Do not edit files."
```

Replace `provider/model-id` with the model ID returned by `opencode models`.
Do not use `--auto`: it auto-approves permissions that should remain visible
for review.

## Run Ralph Loop workers

The top-level session uses the primary `ralph-loop` profile. For each
implementation worker, first create its dedicated child worktree and branch,
then start a separate OpenCode session rooted at that child directory:

```sh
opencode run --dir <child-worktree> --agent ralph-loop-worker \
  --model provider/model-id "<bounded worker assignment>"
```

Replace both placeholders before running the command. OpenCode subagents do
not create Git worktrees; the coordinator owns worktree creation and serial
integration. Use the named read-only reviewer profiles for independent PR
reviews. See the [multi-agent orchestration guide](./multi-agent-orchestration.md)
for the required branch, worktree, verification, and merge lifecycle.

## Troubleshooting

- `opencode: command not found`: open a new terminal, verify the installer
  completed, and make sure the install location is on `PATH`.
- `opencode auth list` shows no providers: run `opencode auth login` or use
  `/connect` in the TUI, then retry the command.
- The requested model is unavailable: run `opencode models` and copy an exact
  `provider/model-id` from the result.
- A Ralph profile is not listed: run `opencode agent list` from the
  repository root and confirm the profile exists under `.opencode/agents/`.
- A tool asks for permission: review the requested action and approve only
  what is needed; do not bypass the prompt with `--auto`.
