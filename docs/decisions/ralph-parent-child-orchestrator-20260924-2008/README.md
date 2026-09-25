# Ralph Branch Decision Index

- **Run ID:** `copilot_skills-parent-child-pipeline-20260924`
- **Branch ref:** `refs/heads/ralph/parent-child-orchestrator-20260924-2008`
- **Branch slug:** `ralph-parent-child-orchestrator-20260924-2008`
- **Original `origin/main` base SHA:** `12c5a8ae22eac19023befaaf5883ab63512bee27`
- **Latest `parent_rebased_onto_origin_main_sha`:** `114e4d60567d05cd048916339ed86e324c6eeef3`
- **Parent implementation commit SHA:** `e0e5c6ec614a9d903d94222fc87d55f96833b6f3`
- **Coordinator:** `coordinator` — parent-child Ralph orchestrator.
- **Worker branches:** `ralph/parent-child-worker-agent-skill-20260924-2008` and `ralph/parent-child-worker-reference-docs-20260924-2008`.
- **Parent PR:** `NOT_OPENED`; the repository's documented integration path is a verified fast-forward to remote `main`.
- **Parent merge:** `PENDING`.

## Agent records

- [Coordinator no-PR and integration record](agents/coordinator/pr-not-opened.md)
- [Coordinator current status](../../ralph/ralph-parent-child-orchestrator-20260924-2008/agents/coordinator/status.md)
- [Coordinator progress](../../ralph/ralph-parent-child-orchestrator-20260924-2008/agents/coordinator/progress.md)
- [Worker-01 branch decision index](../ralph-parent-child-worker-agent-skill-20260924-2008/README.md)
- [Worker-02 branch decision index](../ralph-parent-child-worker-reference-docs-20260924-2008/README.md)

## Decisions

- The first Ralph Loop invocation is the high-level orchestrator, configured
  through the Ralph launcher/session `--orchestrator` option. It is not a
  native `copilot` CLI flag.
- The coordinator owns a parent branch/worktree from fetched `origin/main`;
  each worker owns a child branch/worktree from the current parent tip.
- The coordinator integrates children serially into the parent and verifies
  each result. Only the completed parent is integrated to `origin/main`.
- Child cleanup is permitted only after verified child-to-parent integration;
  parent cleanup is permitted only after verified parent-to-main integration.
- The Git pipeline test uses a temporary bare remote and two sequential
  workers to verify integration and cleanup gates without touching this
  repository's `main`.

## Integration state

- Worker-01 child-to-parent integration: `VERIFIED`.
- Worker-02 child-to-parent integration: `VERIFIED`.
- Parent-to-main integration: `PENDING`.
- Post-merge memory review and parent cleanup: `PENDING`.
