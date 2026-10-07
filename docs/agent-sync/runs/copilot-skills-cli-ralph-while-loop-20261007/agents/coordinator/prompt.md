Update the Copilot CLI compatibility guide in copilot_skills to show a
literal, valid Bash `while` loop that runs bounded Ralph iterations via
Copilot CLI's documented non-interactive `--prompt` invocation. The example
must cap iteration count; require exactly one standalone RALPH_CONTINUE,
RALPH_COMPLETE, or RALPH_BLOCKED final marker; stop on CLI errors, blocked or
unknown/missing markers, and max-iteration exhaustion; and only exit success
on RALPH_COMPLETE. Explain that each --prompt invocation is a fresh one-shot
CLI run and relies on committed project/worktree/status state rather than
previous conversation context. Cite the official Copilot CLI programmatic-use
documentation. Add a contract test that enforces the literal while syntax,
CLI invocation, bounded/error/marker behavior, and citation. Do not change the
repository's OpenCode default, touch product behavior, weaken CLI permissions,
or use --allow-all. Keep implementation/test edits restricted to
.github/skills/ralph-loop/references/copilot-cli-usage.md and
.github/skills/ralph-loop/tests/test_multi_agent_contract.py, with this run's
own Ralph status/progress and decision records.
