# Ralph coordinator progress

## Iteration 1 — pre-merge code review gate

- **Run:** `copilot-skills-premerge-code-review-20260924`
- **Task:** `code-review-gate-coordination`
- **Coordinator branch/worktree:** `ralph/code-review-gate-20260924-2131` /
  `/Users/jrblankenhorn/copilot_skills.worktrees/ralph-code-review-gate-20260924-2131`
- **Runtime agent ID:** `copilotcli:/ac00179e-f9e2-4693-8f9f-710a82b06af9`
- **Base `origin/main` SHA:** `485b4a64c871f581f9295e46c867b188b0e3ccee`
- **Status:** `IN_PROGRESS`

### Acceptance slice

Add an independent AI code-review step before each PR-backed Ralph merge,
specialized reviewer agents, a hard limit of ten reviewer/author rounds per
branch, and an explicit author decision once that limit is reached. Preserve
the current coordinator-authorization, branch-owner merge, CI, and human
approval requirements. Keep the existing no-PR fast-forward workflow
unchanged.

### Setup and repository evidence

- The canonical skills checkout and active project are both
  `jrblankenhorn1007/copilot_skills`; the clean primary worktree is
  `/Users/jrblankenhorn/copilot_skills`, attached to `main` and tracking
  `origin/main`.
- `git -C /Users/jrblankenhorn/copilot_skills pull --ff-only` — already up
  to date.
- `git fetch origin` — PASS; `origin/main` is
  `485b4a64c871f581f9295e46c867b188b0e3ccee`.
- Git author and committer identities are configured. Coordinator worktree
  was created from that exact `origin/main` SHA and is clean.
- The active Ralph dashboard was `COMPLETE`; no current project plan or
  runner is present. The user request supplies the acceptance criteria.
- Existing project records describe coordinator-managed verified
  fast-forward integration without opening a PR for these documentation
  changes; the PR-specific review gate does not apply to this run.

### Research notes

- Google's reviewer guidance prioritizes design, behavior, edge cases, test
  quality, and meaningful code-health improvement over subjective style
  preferences or perfection.
- GitHub's Copilot code-review documentation describes repository-context
  gathering as an accuracy aid and emphasizes that the product uses a tuned
  review approach; this supports context-rich, commit-bound review rather
  than choosing an unverified model.
- The repository's Agentic Eval skill recommends explicit criteria,
  structured evaluator output, bounded iteration, and convergence checks.
- Local/public skill research (including GitHub Awesome Copilot's
  `audit-integrity` and the `bug-hunter` project) informed evidence checks
  and a skeptical pass; no third-party code or skill text is being copied or
  installed.

### Split plan and current work

- `worker-01` owns `.github/skills/ralph-pr-review/SKILL.md`, the dedicated
  code and conditional security reviewer agent files, and the Ralph Loop
  agent's reviewer allowlist.
- `worker-02` owns the Ralph PR-review lifecycle/status guidance, merge guide,
  static documentation-contract checks, and README links.
- Both workers were dispatched with disjoint implementation paths and the
  shared exact interface (reviewer names, skill path, ten-round semantics).
- Worker sign-offs and checks remain pending. Exact commands/results,
  integration SHA, and memory-review disposition will be appended here.

### Decisions

1. Every PR must receive one read-only independent correctness/regression
   review; add a conditional security specialist for security-sensitive
   changes rather than paying for overlapping full reviews on every PR.
2. Bind every report to the reviewed base and head SHAs. Any change to either
   invalidates the prior report before merge authorization.
3. Count the initial reviewer report as round one and stop automated
   reviewer/author exchanges after ten rounds. At that point the author must
   explicitly choose a next action; no reviewer may merge or bypass policy.
4. Do not add an AI model preference without comparative evidence.

### Verification and integration

Documentation-only work: no TDD Red phase is applicable. The documentation
contract test, diff inspection, worker merges, remote-main verification, and
post-merge memory review remain pending.
