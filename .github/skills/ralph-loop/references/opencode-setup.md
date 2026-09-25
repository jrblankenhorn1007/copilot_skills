# OpenCode setup

This guide covers general OpenCode installation and provider authentication.
It does not migrate this repository's Ralph Loop from its current Copilot CLI
runtime. Ralph-specific OpenCode invocation and integration remain pending
validation; this guide does not configure repository-level OpenCode agents or
claim that `.github/agents` is an OpenCode agent location.

## Install OpenCode

Use the official install script:

```sh
curl -fsSL https://opencode.ai/install | bash
```

Or install with Homebrew:

```sh
brew install anomalyco/tap/opencode
```

See the [OpenCode installation guide](https://opencode.ai/docs/) for current
installation options. Once installed, start OpenCode from a terminal with:

```sh
opencode
```

## Connect a model provider

OpenCode needs credentials for an LLM provider. In the OpenCode TUI, run
`/connect`, choose a provider, and complete its authentication flow. For an
API-key provider, use a key issued by that provider; do not put API keys in
this repository.

OpenCode stores provider credentials in
`~/.local/share/opencode/auth.json`. Keep that file private and do not commit
it. See the [OpenCode providers guide](https://opencode.ai/docs/providers/)
for provider-specific details.

## Ralph Loop integration

Installing and connecting OpenCode is independent of the Ralph Loop runtime.
Continue using the existing Copilot CLI instructions for Ralph Loop until
OpenCode integration has been separately confirmed to work.
