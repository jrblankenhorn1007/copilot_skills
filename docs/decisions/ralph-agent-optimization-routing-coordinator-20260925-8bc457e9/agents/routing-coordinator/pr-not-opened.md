# Routing coordinator decisions - no child PR opened

- **Run / task:** `copilot-skills-agent-routing-20260925-8bc457e9` /
  `skill-aware-ralph-routing`
- **Agent / runtime session:** `routing-coordinator` /
  `8bc457e9-1724-42bb-b3c8-cdf453f54a32`
- **Branch ref:** `refs/heads/ralph/agent-optimization-routing-coordinator-20260925-8bc457e9`
- **Exact parent base:** `4eb15e69434df810958c3d488e223e1366f00d39`
- **Implementation commits:** `56a9fa44e2446553424a254babbb8330429592e5`,
  `c0796984ff10bfbe460656663da1f3e297fc7529`
- **PR:** `NOT_OPENED`; this child is unpublished. Its rewritten tip was
  verified on the preserved parent before final remote integration.

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

### Resolution of the shared-file and integration blockers

The previous shared-file owner released its edit claim. Parent rebase
mapped final routing commit `c0796984ff10bfbe460656663da1f3e297fc7529`
and child tip `9e4936e8f31b14a756fde01cdf33a8d99532f600` to
`3cf5558464cba08807a81be2330df4ea39af2720` and
`5c1bcdbcc3ad780c94f3284cbe77bb647f1fc442`. The original and
rewritten tips have identical owned-file contents. The latter tip is an
ancestor of parent `56340cb2f89a738d560532046332c3794b5fec5c` via
verified merge `eba1d05043ed80a6c0a60eb4c2a20404f3a00959`.
Both dashboard entries are indexed and the deployed Ralph Loop profile
now routes the four specialists conditionally with 15 targeted contract
tests passing. Its role-hierarchy successor is blocked and unmerged;
parent-to-main verification and memory review remain pending.

On the final parent rebase to
`70b98bbf0ab35620f7c33b5d9789187560c699df`, routing
implementation `3cf5558464cba08807a81be2330df4ea39af2720` became
`4110fb7769d2ffca322cddf6e4b7731da75229a0`, tip
`5c1bcdbcc3ad780c94f3284cbe77bb647f1fc442` became
`24323c86425cd292af8249e6520c33a0f83c1d66`, and local parent
merge is now `691d5b4dbb18a87768294326fc924f28b1490249`.
The final tip remains a parent ancestor with identical original owned
content; its current sign-off is a coordinator `SELF_ATTESTATION`.
The separate role coordinator has resumed in a narrower, disjoint scope,
but its code branch is still unmerged.

The authorized no-PR parent fast-forward
`0b7db073e365e6c1c6e29d410c424d7c7637c9bf` and latest child
tip are ancestors of fetched `origin/main` at
`86fde358a421f64f4c979b24d0127e6797470bf9`. Main signed out
after that merge. The coordinator's post-merge memory/protocol
follow-up remains pending; retain this leaf as `AWAITING_MERGE`
until its final synchronization.
