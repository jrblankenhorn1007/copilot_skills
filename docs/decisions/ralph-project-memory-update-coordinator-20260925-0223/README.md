# Branch decisions

- Exact branch: `ralph/project-memory-update-coordinator-20260925-0223`
- Base `origin/main`: `114e4d60567d05cd048916339ed86e324c6eeef3`
- Coordinator agent: `coordinator`; runtime session: `copilotcli:/dfeb3cd8-a5e9-4dec-b4e5-e2cf00dcb998`
- Implementation commit: `f5adf9e95e227b8eae3eed8e9bc91ac0d1113e5e`
- Integration state: parent `82d34a3` is rebased onto fetched `origin/main`
  `96fca381f96a743a08eb2e758d1eae8eb2fd483a`; final remote integration and
  post-merge memory review remain pending.

## Agent/PR records

- [Coordinator no-PR integration record](agents/coordinator/pr-not-opened.md)

## Decisions

### Separate memory-updater implementation from Ralph handoff integration

- **Context:** The user reports that Ralph has a Project Memory skill but does not produce visible memory updates, and asks for a dedicated agent that receives implementation knowledge from every agent and subagent.
- **Alternatives:** Keep the coordinator as the sole memory editor; let each worker edit shared memory; or introduce a dedicated updater with an explicit evidence handoff.
- **Decision:** Dispatch two disjoint workers: one defines/tests the dedicated updater agent, and the other integrates structured coordinator/worker reports and the post-integration invocation into Ralph guidance.
- **Rationale:** Shared categorized memory needs one evidence-checking owner, while a structured report from every implementation agent preserves knowledge without allowing parallel edits to shared memory.
- **Consequences:** The updater must run only after implementation merges are verified on `origin/main`; it owns any fresh memory-follow-up branch and reports no-update when evidence does not support a durable lesson.

### Use the active project's documented memory store

- **Context:** The Project Memory skill specifies a project-local memory store; in this repository it is `.github/memory/`.
- **Decision:** The updater targets the active project's documented memory store and uses `.github/memory/README.md` and category files when the active project is `copilot_skills`.
- **Consequence:** A run in another repository does not write into this skills repository merely because the updater is defined here.

### Serialize refreshes of the shared integration worktree

- **Context:** Both workers use the same clean primary integration worktree.
- **Decision:** The coordinator performs the required `pull --ff-only` and fetch before dispatch; workers verify the refreshed `origin/main` and request a new coordinator-serialized refresh if it changes.
- **Rationale:** Concurrent pulls or fetches of the same worktree and shared Git refs can race and make the base ambiguous.
- **Consequence:** Each worker still creates its isolated branch from the verified latest `origin/main` and records its own base SHA.

### Preserve and reverify child integration across parent rebases

- **Context:** Repeated upstream advances rewrote the parent commits that recorded worker-01's child integration.
- **Decision:** Map every rebased parent patch with `git range-diff`, compare stable patch IDs for the worker implementation and integration, and verify the current integration commit is an ancestor of the rebased parent before updating worker status.
- **Evidence:** The final rebase preserved all 23 parent patches; worker implementation patch ID `1571aec2fe973545242da3e2d925c6027d49d9ef` and integration patch ID `457e943bdfd9be5cb94a63cf3ff32d72e34ce887` are unchanged, and the current integration is an ancestor of parent `82d34a3`.
