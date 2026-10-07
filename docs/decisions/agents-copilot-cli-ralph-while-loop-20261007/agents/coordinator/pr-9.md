# PR #9 — Copilot CLI bounded while loop

- Run/task: `copilot-skills-cli-ralph-while-loop-20261007` /
  `document-copilot-cli-ralph-while-loop`
- Agent: `coordinator` (`copilotcli:/e33128a0-4868-4b49-9b6a-a3f28bb65997`)
- Branch: `agents/copilot-cli-ralph-while-loop-20261007`
- Original base: `2abcbe040582e68cacc7192d2388fc5eaae7a816`
- Current fetched base: `e6ed4c20c5955af91c628b34f026b6eb63c09c70`
- Implementation fix commit:
  `ac5a083230b1d40d639a47c1ee925336a5817696`
- PR head before this status refresh:
  `ac5a083230b1d40d639a47c1ee925336a5817696`
- PR: https://github.com/jrblankenhorn1007/copilot_skills/pull/9
- Opening base/head:
  `741f23521dbfc2465d5f0943de4451c0a3a42f5a` /
  `ecba436feb718cabe47cacfd7b6e6d3954bc70c0`
- Current pre-refresh PR base/head:
  `e6ed4c20c5955af91c628b34f026b6eb63c09c70` /
  `ac5a083230b1d40d639a47c1ee925336a5817696`
- Integration path: merge this PR only after independent reviews and all
  required checks/approvals pass;
  no direct-main integration is authorized.

## Decisions

- Use the documented Copilot CLI `--prompt` interface in a literal Bash
  `while` loop, with a hard iteration bound and one recognized terminal
  marker.
- Parse model output only as status text; do not execute model-produced shell
  commands. Stop on nonzero CLI status, marker validation failure, blocked or
  malformed output, and max-iteration exhaustion.
- Keep OpenCode as the default Ralph runtime and omit permission-bypass flags.

## Verification

- `python3 .github/skills/ralph-loop/tests/test_multi_agent_contract.py`:
  31 tests passed.
- `python3 .github/skills/ralph-loop/tests/test_multi_agent_contract.py GitPipelineTests.test_copilot_cli_loop_rejects_unknown_standalone_markers -v`:
  uppercase and lowercase unknown standalone markers before `RALPH_COMPLETE`
  both exit 1.
- Extracted Bash block passed `bash -n`.
- Mocked terminal-marker and CLI-error cases behaved as documented.
- `git diff --check`: clean.

## Recovered operational issues

- One initial test invocation ran from the integration checkout and did not
  exercise the edited files. The test was rerun using the absolute test path
  in this branch and passed.
- An initial mock harness used `source /dev/stdin`, which did not execute the
  piped snippet. Re-running via `bash -s` exercised the actual wrapper and
  passed all expected exit-code cases.

## Recovered capacity blocker

The `2026-10-07T16:16:14Z` snapshot showing `max_agents: 2`,
`active_agent_count: 3`, and zero free slots is no longer current. A later
Resource Manager reservation for PR #8's independent code reviewer succeeded.
PR #9 round-one reports are recorded below; refresh capacity before its
follow-up review reservation and verify the exact PR base/head before dispatch.

## Round-one reviews and fix

- Code and Security reports completed for base/head
  `e6ed4c20c5955af91c628b34f026b6eb63c09c70` /
  `cfb290c89a7ce9674e18236042675d681f39a61b`.
- Code review: `FINDINGS`, R1 (medium, high confidence) at
  `.github/skills/ralph-loop/references/copilot-cli-usage.md:142`. The marker
  counter ignored an unknown standalone `RALPH_...` line, so
  `RALPH_FUTURE` followed by `RALPH_COMPLETE` returned success.
- Security review: `CLEAN`; no findings for the same exact pair.
- The author chose `FIX_MANUALLY`. Commit
  `ac5a083230b1d40d639a47c1ee925336a5817696` rejects unknown standalone
  marker-shaped lines and adds a mocked regression against the actual loop.
  Red was reproduced before the production-doc change; the targeted test and
  full 31-test suite passed afterward.
- Round 1 is complete; one finding remains unresolved until the permitted
  follow-up Code and Security reviews verify the updated exact PR head.
