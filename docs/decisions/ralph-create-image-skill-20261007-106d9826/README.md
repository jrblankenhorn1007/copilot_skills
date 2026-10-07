# Ralph Branch Decisions

- **Branch:** `refs/heads/ralph/create-image-skill-20261007-106d9826`
- **Run/task:** `copilot-skills-create-image-20261007-106d9826` /
  `create-image-skill-live-model`
- **Agent:** `coordinator`; runtime
  `copilotcli:/106d9826-722e-465f-9fe9-1f6dfd20bf32`
- **Initial base `origin/main`:** `e5678b13b9e21db2fbe6ab1c85dcea1411a0a062`
- **Latest base incorporated before implementation commit:**
  `a8cf0eae5d26cac0d7adee645449809bc24ec94a`
- **Implementation commit:** pending
- **PR/integration:** `NOT_OPENED`; documented coordinator-managed no-PR
  fast-forward; remote merge verification pending
- **Agent record:** [coordinator/pr-not-opened.md](agents/coordinator/pr-not-opened.md)

## Decisions

1. Keep the skill as guidance over Runecore's existing asset-pipeline CLI;
   do not add a second provider integration.
2. Put the real-model test behind an explicit opt-in because it contacts a
   billable external service. Keep request and generated output temporary,
   and suppress provider diagnostics in test failures.
3. Treat the skill and its live test as one integrated coordinator assignment.
   The default worker count is 2, but this request has no useful independent
   path split and the Resource Manager reported no available host slots.
4. Use the documented no-PR fast-forward process. No branch protection or
   GitHub rulesets were found; the merge still requires the main ownership
   lease and exact remote verification.

## Path coordination

The root `README.md` and `docs/ralph-status.md` currently have active peer
owners. Coordination requests were queued; those paths remain unchanged until
the owners release or explicitly coordinate them. The task will update its
scope in the agent-sync record before editing either path.
