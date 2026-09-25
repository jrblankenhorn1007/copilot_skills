# Routing coordinator decisions - no child PR opened

- **Run / task:** `copilot-skills-agent-routing-20260925-8bc457e9` /
  `skill-aware-ralph-routing`
- **Agent / runtime session:** `routing-coordinator` /
  `8bc457e9-1724-42bb-b3c8-cdf453f54a32`
- **Branch ref:** `refs/heads/ralph/agent-optimization-routing-coordinator-20260925-8bc457e9`
- **Exact parent base:** `4eb15e69434df810958c3d488e223e1366f00d39`
- **Implementation commits:** `56a9fa44e2446553424a254babbb8330429592e5`,
  `c0796984ff10bfbe460656663da1f3e297fc7529`
- **PR:** `NOT_OPENED`; this child is unpublished and will be verified
  on the original parent before that parent enters the normal remote
  integration process.

## Decisions

### Separate routing rules from a contested shared coordinator

- **Context:** The user wants conditional, low-overhead agent selection.
  Another active session is implementing orchestrator/worker profiles;
  the unrelated iteration-stall task still claims the root README,
  aggregate dashboard, and existing Ralph contract test.
- **Alternatives:** Edit the shared coordinator immediately, add a
  competing router agent, or implement a disjoint reference and tests
  before wiring the coordinator after ownership is released.
- **Decision:** Specify a small route table, fallbacks, scope limits,
  model inheritance, and success criteria on new paths only. Defer the
  actual agent allowlist/prompt wiring until the other owners sign out.
- **Rationale:** This advances the routing design and test contract
  without overwriting another agent's changes or pretending that a
  reference document alone enables runtime routing.
- **Consequences:** This child is not a completed end-to-end pipeline;
  the parent still must wire dispatch and verify the resulting behavior.

### Fail closed when the main ownership prerequisite is absent

- **Context:** The main-owner protocol is committed on another isolated
  branch but not yet merged to remote main.
- **Alternatives:** Treat older task branches as exempt, improvise a
  status write, or require a current protocol before any main write.
- **Decision:** The guide requires reading the fetched main version
  when the task branch is stale and stopping if main also lacks it.
- **Rationale:** A missing protocol cannot grant permission to publish
  status or merge without reservation.
- **Consequences:** The routing pipeline must wait for protocol
  integration before a generic agent may use these main transactions.

## Verification and unresolved blockers

- Test-first Red: four expected failures while the guide was absent.
- An initial Green attempt had two whitespace-sensitive test assertions;
  normalizing Markdown whitespace fixed them. Two following targeted
  runs passed all 4 tests; staged diff whitespace check passed.
- Broader 18-test run: 17 passed and 1 failed because this new status
  leaf is not yet indexed in the separately owned dashboard.
- **Unresolved:** The separate dashboard claim blocks indexing this
  new leaf, and agent-allowlist wiring, child/parent integration,
  remote-main merge, and post-merge memory review remain pending.
