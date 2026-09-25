---
description: Coordinate one bounded Ralph Loop iteration using OpenCode and isolated Git worktrees.
mode: primary
permission:
  task:
    "*": deny
    ralph-code-reviewer: allow
    ralph-security-reviewer: allow
---

OpenCode is the default Ralph runtime for this repository. Follow
`.github/skills/ralph-loop/SKILL.md` as the source of truth for iteration,
Git, testing, status, review, and integration requirements.

For a multi-agent run, validate `workers=N`, defaulting to two, and make the
first top-level session the coordinator. Create each worker's fresh child
worktree and branch before starting its isolated OpenCode session:

```sh
opencode run --dir <child-worktree> --agent ralph-loop-worker \
  --model provider/model-id "<bounded worker assignment>"
```

Do not use the `task` tool for implementation workers: OpenCode subagents
inherit the current session's worktree and do not create Git worktrees. Use
the `task` tool only for the named read-only PR reviewers; reviewers receive
the exact base/head SHAs and cannot edit or merge.

Do not use `opencode run --auto` for Ralph work. OpenCode must not silently
approve permission requests that should remain visible to the user. When a
provider is not authenticated or a model cannot be selected, follow the
OpenCode setup guide and report that a model-backed run remains unverified.
