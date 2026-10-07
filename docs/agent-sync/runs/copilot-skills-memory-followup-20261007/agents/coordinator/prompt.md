# Memory Follow-up PR Integration

Run/task: `copilot-skills-memory-followup-20261007` / `memory-follow-up-pr`

Preserve the published branch `agents/memory-worktree-janitor-gate-20261007` and its commit `f677e4144cb013d65939f3c605dc1cd30b53e2d5`. It contains a Project Memory Update that was independently reviewed after the Janitor implementation merge `85c8a4796e21f0d1e1a88fb01804a55d3c71d893` was verified on `origin/main`. That branch is based on an older main SHA and did not open a PR.

Repository policy limits direct-main/no-PR integration to `docs/agent-sync/**` metadata. Replay only the already-reviewed lesson onto a fresh branch based on the latest fetched `origin/main`; do not modify or rewrite the published memory branch. Use the normal PR path for `.github/memory/workflow.md`, run the relevant memory and Janitor contract tests plus `git diff --check`, and obtain an independent Code review bound to the exact PR base/head. Do not invoke the Project Memory Update agent again for this memory-only follow-up. Merge only after the normal PR gates pass, then fetch and verify the resulting memory merge SHA on `origin/main`.

Keep edits limited to `.github/memory/workflow.md` and this task's sign-in/status metadata. Do not edit `docs/ralph-status.md` until its current task-scope owner has published a verified release. Preserve the original memory branch/worktree and all other sessions.
