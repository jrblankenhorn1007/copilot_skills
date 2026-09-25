# Structured Ralph task prompt — iteration 2

## Objective

Add Ralph Loop instructions that transform a user's natural-language request
into a bounded, structured task prompt informed by refreshed project
instructions, applicable skills, relevant validated memory, and the tools
actually available. The generated prompt, not a verbatim raw user message,
must govern execution and worker assignments.

## User-stated scope

- Preserve explicit user intent and scope; distinguish user-stated
  requirements from project-derived requirements and assumptions.
- Do not invent work. Surface material ambiguity for clarification before
  dispatch or implementation.
- The structured prompt must state the objective, user scope, derived
  requirements, assumptions, constraints/non-goals, skills and validated
  memory, available tools, bounded work plan, acceptance criteria,
  verification, integration end condition, and any needed clarifications.
- Save a secret-safe version at
  `docs/decisions/<branch-slug>/prompt.md` and link it from that branch's
  `README.md`.
- Reapply only the unmerged iteration-1 prompt-generation implementation on
  the fresh iteration-2 branch:
  `.github/agents/ralph-loop.agent.md`,
  `.github/skills/ralph-loop/references/prompt-generation.md`, and
  `.github/skills/ralph-loop/tests/test_prompt_generation_contract.py`.
- Add this branch's decision/prompt/PR records and worker-owned status and
  progress records. Keep the iteration-1 branch unchanged.
- Run the focused contract test, existing Ralph contract suite, and
  `git diff --check`; commit with the required Copilot co-author trailer.
- Publish this feature branch and open its PR through the normal available
  process. Wait for the coordinator to authorize this exact PR before any
  merge; do not merge during this handoff.

## Derived project requirements

- The refreshed Ralph agent and skill define per-iteration source refresh and
  the integration lifecycle. Preserve their current branch, status, and
  worker-owned PR requirements.
- `.github/skills/ralph-loop/references/multi-agent-status.md` makes the
  coordinator the sole writer of `docs/ralph-status.md`; this worker writes
  only its own `docs/ralph/<branch-slug>/agents/worker-01/{status,progress}.md`
  leaf records.
- `.github/skills/ralph-loop/references/worker-pr-merging.md` requires the
  branch owner to wait for coordinator authorization of the exact PR, then
  perform and verify the merge using its own existing authentication.
- `.github/skills/tdd/SKILL.md` requires a focused failing contract test
  before behavior changes, followed by passing targeted verification.
- The repository's current Ralph contract suite is
  `.github/skills/ralph-loop/tests/test_multi_agent_contract.py`; do not edit
  it because it belongs to another worker.
- Branch decision records must include the sanitized prompt, a branch index,
  and a separate worker/PR record. Current leaf status and append-only
  evidence belong only under this branch's `docs/ralph/` leaf paths.
- Git fetch establishes read access only. Do not infer branch publication or
  PR merge permission from it.

## Assumptions

- The assigned source paths and branch-local record paths are the complete
  scope for this worker iteration.
- No material scope ambiguity is known. Actual GitHub PR creation capability
  must be verified before claiming the PR is open.

## Constraints and non-goals

- Work only on branch
  `ralph/structured-prompt-recording-worker-01-retry-20260925-0124` in its
  fresh assigned worktree.
- Do not change `.github/skills/ralph-loop/SKILL.md`,
  `.github/skills/ralph-loop/tests/test_multi_agent_contract.py`,
  `docs/ralph-status.md`, `implementation_status.md`, `RALPH_PROGRESS.md`,
  another worker's files, or the prior published iteration-1 branch.
- Do not merge this branch before explicit coordinator authorization of its
  exact PR. Do not push directly to `main` or use another worker's credentials.
- Keep the implementation minimal; do not add unrelated features, cleanup, or
  refactors.
- Persist no secrets, credentials, tokens, or unrelated private context.

## Applicable skills, validated memory, and available tools

- Skills and guidance applied: Ralph Loop, TDD, Project Memory, multi-agent
  orchestration, multi-agent status, and worker-owned PR merging.
- Validated workflow memory: preserve already-published iteration history;
  separate fetch, publish, and merge authorization; do not infer write access
  from a successful fetch. Confirmed against current Ralph and PR-merging
  guidance.
- Available for this iteration: Git 2.50.1, Python 3.9.6 and its standard
  library, patch editing, and GitHub MCP read/list operations. The `gh` CLI is
  unavailable, and no writable PR-creation MCP action is exposed. The
  repository's current no-browser rule prohibits using a browser for Git or
  GitHub repository operations. Use `gh` or a supported writable GitHub
  integration for PR operations; if neither is available, preserve the branch
  and report the blocker without changing authentication or falling back to a
  browser.

## Bounded work plan

1. Add the focused standard-library prompt-generation contract test first and
   run it to confirm a genuine Red caused by the missing behavior.
2. Reapply the prompt-generation reference and agent wiring while preserving
   current status, artifact, and PR instructions.
3. Add the secret-safe prompt and this branch's decision, worker status, and
   progress records; record iteration-1 provenance and retry rationale.
4. Run the focused contract test, current Ralph contract suite, and
   `git diff --check`; inspect the complete diff against current
   `origin/main`.
5. Commit with the required Copilot co-author trailer. Fetch before
   publication; rebase and rerun targeted checks if `origin/main` has moved.
6. Publish only this feature branch. Open the worker-owned PR only through
   `gh` or a supported writable GitHub integration; never use a browser for
   GitHub operations. If no supported write action is available, preserve the
   branch and report the PR-creation blocker.
7. Do not merge until the coordinator authorizes this exact PR.

## Acceptance criteria

- The focused contract test proves the agent invokes prompt-generation
  guidance; the guidance specifies the required structured fields,
  user-intent and scope preservation, current instructions/skills/memory/tool
  loading, secret-safe persistence, exact branch-doc artifact path, and using
  the generated prompt for execution and worker assignments.
- The focused test passes after implementation, the current Ralph contract
  suite passes, and `git diff --check` passes.
- The full diff is scoped to the assigned implementation and branch-local
  records, and the records link the structured prompt and identify the retry
  provenance.
- The feature branch is published and its PR is opened and recorded, if a
  normal authenticated `gh` or writable GitHub integration is available.
  Otherwise the branch is preserved and the inability to open a PR is
  reported as a blocker; browser-based GitHub operations are not permitted.
- The worker hands off as `AWAITING_MERGE`; no merge occurs until explicit
  coordinator authorization of the exact PR.

## Verification

- Red: `python3 .github/skills/ralph-loop/tests/test_prompt_generation_contract.py`
  must fail because the guidance and agent wiring are missing.
- Green: run the same focused test; expect all seven tests to pass.
- Regression: `python3 .github/skills/ralph-loop/tests/test_multi_agent_contract.py`
  must pass.
- Hygiene: `git diff --check` must pass.
- Review: inspect `git diff origin/main...HEAD`, full branch-local record
  contents, and `git status`; fetch before publication and record any rebase
  and retest evidence.
- PR: through `gh` or a supported writable integration, verify the host
  reports the exact branch's PR open, record number and URL, and leave merge
  pending. Do not use a browser or claim an unavailable check passed.

## Integration end condition

The branch owner publishes this feature branch and opens its worker-owned PR
through `gh` or a supported writable GitHub integration; never use a browser
for GitHub repository operations. The iteration is `AWAITING_MERGE`, not
complete, while the PR awaits
coordinator authorization. The worker must not merge until the coordinator
authorizes this exact PR. After authorization, the branch owner performs the
merge with its own existing authentication, waits for the host's merged state,
fetches `origin`, and verifies the merge SHA on `origin/main`. The coordinator
then performs the required post-merge memory review and updates the aggregate
dashboard. An open PR, published branch, or local commit alone is not
completion.

## Clarifications needed

None for the implementation scope. PR-creation capability must be verified
through `gh` or a supported writable GitHub integration. If neither is
available, report the blocker; browser-based GitHub operations and credential
changes are not permitted.
