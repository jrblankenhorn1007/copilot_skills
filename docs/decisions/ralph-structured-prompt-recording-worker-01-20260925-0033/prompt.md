# Structured Ralph Task Prompt

- **Run:** `ralph-prompt-generation-main-clean-20260925-0032`
- **Task:** `structured-ralph-prompt-generation`
- **Worker/iteration:** `worker-01 / structured prompt generation`, 1
- **Branch:** `ralph/structured-prompt-recording-worker-01-20260925-0033`

## Objective

Specify and test how the Ralph Loop agent converts a user's natural-language
request into a bounded, structured task prompt informed by current project
guidance, applicable skills, validated memory, and available tools.

## User-stated scope

- Update `.github/agents/ralph-loop.agent.md` to invoke the prompt-generation
  guidance and use the generated prompt for execution and worker assignments.
- Add `.github/skills/ralph-loop/references/prompt-generation.md` with
  requirements for preserving explicit user scope, separating derived
  requirements and assumptions, avoiding invented work, clarifying material
  ambiguity, and describing all required prompt fields.
- Add a focused standard-library contract test that checks the agent wiring,
  structured fields, project-context loading, scope behavior, safe persistence,
  and execution use.
- Save this sanitized task prompt at this branch's
  `docs/decisions/<branch-slug>/prompt.md`, link it from the branch
  `README.md`, and maintain the worker's `pr-not-opened.md` record.
- Run the focused prompt-generation contract test, the existing Ralph
  multi-agent contract test, and `git diff --check`.
- Use the assigned feature branch and worktree. Do not edit the coordinator's
  status snapshot, root `README.md`, `implementation_status.md`,
  `RALPH_PROGRESS.md`, `.github/skills/ralph-loop/SKILL.md`, or the existing
  multi-agent contract test. Do not publish or merge to `main`; publish only
  this feature branch if permitted.

## Derived project requirements

- The current Ralph Loop agent and skill require a fresh worktree based on the
  latest fetched `origin/main`, current project guidance, and branch-scoped
  decision records. Sources: `.github/agents/ralph-loop.agent.md` and
  `.github/skills/ralph-loop/SKILL.md`.
- Behavior changes follow Red-Green-Refactor; this task's explicit focused
  contract test is the observable check for the instruction behavior. Source:
  `.github/skills/tdd/SKILL.md`.
- A worker does not edit the coordinator-owned aggregate status snapshot and
  stays `AWAITING_MERGE` until serialized integration and the required
  post-merge memory review are verified. Sources:
  `.github/skills/ralph-loop/references/multi-agent-status.md` and the
  coordinator-provided run snapshot.
- The refreshed status protocol assigns each worker its own branch/agent
  `docs/ralph/<branch-slug>/agents/<agent-id>/status.md` and `progress.md`;
  the aggregate dashboard remains coordinator-owned. Source:
  `.github/skills/ralph-loop/references/multi-agent-status.md`.
- Relevant validated workflow memory says that remote fetch establishes read
  access only, branch-push and merge access must not be assumed, and follow-up
  integration must remain reviewable. Source: `.github/memory/workflow.md`.

## Assumptions

- This is an instruction-contract change, not a request to build a separate
  prompt-generation runtime or application feature.
- The task's prescribed no-PR worker handoff is the intended integration path;
  the coordinator will serialize integration after reviewing the sign-off.
- No material ambiguity remains in the assigned scope or acceptance criteria.

## Constraints and non-goals

- Implement only the assigned agent, new reference, focused test, this
  branch's decision records, and this worker's required status/progress leaf.
  Do not edit another worker's files or shared status.
- Preserve explicit user scope; do not add unrelated prompt features, root
  documentation, or changes to the Ralph Loop skill and existing test.
- Do not assume branch-push access from fetch. Never push or merge to `main`
  from this worker iteration.
- Keep the prompt and branch records free of credentials, tokens, secrets, and
  unrelated private context.

## Applicable skills, validated project memory, and available tools

- Apply the Ralph Loop guidance, including multi-agent status and orchestration
  references; apply TDD for the required contract test. Use Project Memory for
  the post-merge review by the coordinator.
- The relevant validated memory is the Git-access and reviewable-follow-up
  guidance in `.github/memory/workflow.md`.
- Available for this iteration: the repository worktree, Git CLI, `python3`
  with the standard library, and patch-based file editing. `git fetch origin`
  confirmed read access at the recorded base. Feature-branch push permission
  remains unverified until a normal push is attempted; no PR or main merge is
  authorized for this worker.

## Bounded work plan

1. Add the focused standard-library contract test before production guidance
   and run it to establish a Red result caused by the missing prompt contract.
2. Add the structured prompt-generation reference and wire the Ralph Loop
   agent to follow it before task selection or worker dispatch.
3. Save this scoped prompt and complete the branch decision records.
4. Run the focused test, existing Ralph contract test, and whitespace/diff
   check; inspect the final diff.
5. Commit the implementation and records with the required Copilot co-author
   trailer. Fetch again, rebase and retest if `origin/main` advanced, then
   publish only the feature branch if permitted.

## Acceptance criteria

- The agent explicitly invokes the prompt-generation guidance and uses the
  structured prompt—not the raw user message—as the source of truth for
  execution and worker assignments.
- The guidance requires objective, user-stated scope, derived project
  requirements, assumptions, constraints/non-goals, skills/memory/tools,
  bounded work plan, acceptance criteria, verification, integration end
  condition, and clarification questions.
- The guidance preserves explicit scope, labels project-derived requirements
  and assumptions separately, avoids invented work, and asks for clarification
  when ambiguity could materially change the task.
- The guidance reads current project instructions, applicable skills,
  relevant memory validated against current sources, and actually available
  tools.
- The guidance requires a secret-safe
  `docs/decisions/<branch-slug>/prompt.md` and a link from that branch's
  `README.md`.
- The focused and existing Ralph contract tests pass, and `git diff --check`
  passes.

## Verification

- Red: `python3 .github/skills/ralph-loop/tests/test_prompt_generation_contract.py`
  must fail on assertions for the absent agent link and prompt-generation
  contract, not on test setup.
- Green/refactor: rerun the same command and require all focused contract tests
  to pass.
- Regression: `python3 .github/skills/ralph-loop/tests/test_multi_agent_contract.py`
  must pass without edits to that test.
- Whitespace: `git diff --check` must exit successfully.
- After any rebase, rerun the focused and existing contract tests and
  `git diff --check`.

## Integration end condition

The worker commits and, if authorized, publishes only
`ralph/structured-prompt-recording-worker-01-20260925-0033`. No PR is opened
and this worker does not push or merge to `main`. Hand off as `AWAITING_MERGE`;
the coordinator owns serialized integration and the post-merge memory review.
Do not report the iteration `COMPLETE` until the coordinator verifies the
implementation merge on fetched `origin/main` and completes the required
memory review.

## Clarifications needed

None. The coordinator has supplied an exclusive assignment, exact paths,
checks, and integration boundary.
