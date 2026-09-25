# Coordinator decision record — no PR opened

- **Run/task:** `copilot-skills-status-report-time-token-20260925` /
  `branch-status-resource-usage`
- **Agent:** `coordinator`
- **Runtime session ID:** `copilotcli:/b3f44ce6-c093-476d-ab74-b633b1be1939`
- **Branch:** `ralph/status-report-time-token-20260925-0335`
- **Worktree:** `/Users/jrblankenhorn/copilot_skills.worktrees/ralph-status-report-time-token-coordinator-20260925-0335`
- **Base `origin/main`:** `8da9310fda1b2e3042a379081dfb0675f1b22d6b`
- **Implementation commit SHA:** Pending
- **PR:** Not opened. The repository's documented integration path is a
  coordinator-reviewed, verified fast-forward without a PR.

## Decisions

### Keep status schema, instructions, and tests in one worker scope

- **Context:** Per-branch time and token reporting changes the same contract
  across the Ralph skill, agent instructions, status schema/examples, and
  contract test.
- **Alternatives:** Split the files across workers or assign the complete
  contract to one worker.
- **Decision:** Assign the coupled documentation contract to one worker and
  keep the aggregate dashboard with the coordinator.
- **Rationale:** File ownership stays disjoint while the field names,
  definitions, and examples can be changed together.
- **Consequences:** Requested worker count is two, effective worker count is
  one; no overlapping or speculative second task is created.

### Report measurements without inventing unavailable telemetry

- **Context:** Existing records do not consistently capture provider token
  counters.
- **Alternatives:** Estimate token usage, report unknown values as zero, or
  mark provider telemetry explicitly unavailable.
- **Decision:** Report elapsed time with its wall-clock basis and use
  `NOT_REPORTED` plus null token counts when provider usage is unavailable.
- **Rationale:** This distinguishes unknown usage from zero and avoids
  presenting estimates as measured spend.
- **Consequences:** Historical records remain identifiable as legacy when
  token telemetry was never captured; new reports use the documented
  resource-usage fields.

### Follow the no-PR fast-forward integration path

- **Context:** Existing coordinator records identify verified fast-forward
  integration to `origin/main` as the normal path for this repository.
- **Alternatives:** Open a pull request or use the established
  coordinator-reviewed fast-forward path.
- **Decision:** Do not open a PR; integrate only after checks and records are
  reviewed, then fetch and verify the result on `origin/main`.
- **Rationale:** This follows the repository's documented process and does
  not bypass branch protection.
- **Consequences:** If the normal fast-forward is denied, preserve the branch
  and worktree and report the blocker.

### Treat the request as documentation-only

- **Context:** The requested outcome is a status-reporting documentation
  contract, not application behavior.
- **Alternatives:** Fabricate a Red behavior test or validate the existing
  documentation contract and diff integrity.
- **Decision:** Do not create a TDD Red phase; run the existing Ralph
  documentation contract suite and `git diff --check`.
- **Rationale:** A made-up behavior test would not verify this documentation
  change.
- **Consequences:** Record exact documentation-check results in progress
  records.

## Verification and recovered issues

Pending.

## Unresolved blockers

None.
