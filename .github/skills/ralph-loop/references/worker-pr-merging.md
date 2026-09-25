# Worker-owned PR merging

Every PR-backed Ralph iteration has one merge actor: the agent that owns the
iteration branch. In a multi-agent run, the coordinator reviews the worker's
sign-off, checks, and integration readiness, then authorizes one worker PR at
a time. The worker that owns the branch executes its own PR merge after that
coordinator authorization.

Never open, navigate, or automate a browser for Git or GitHub repository
operations. Use the Git CLI (`git`) for local repository operations—status,
diff, fetch/pull, branch/worktree, rebase, commit, and push. Use the configured
GitHub CLI (`gh`) or supported GitHub integration/MCP tools for pull requests,
checks, reviews, and merges. If the required CLI or integration is unavailable
or not authorized, report a blocker; do not fall back to a browser. Continue to
follow the existing Git identity and authentication rules.

## Independent pre-merge review gate

This gate applies to every PR-backed iteration. After worker sign-off and
before the coordinator authorizes merge, launch an independent **Ralph Code
Reviewer**. Also launch **Ralph Security Reviewer** if the diff touches
authentication or authorization, untrusted input, secrets or sensitive data,
cryptography, process execution, external boundaries, dependencies, or
security configuration. Follow
`.github/skills/ralph-pr-review/SKILL.md`. Reviewers are separate from the
author and read-only; they report findings but do not edit the branch, apply
fixes, or merge.

Each completed pass is bound to the exact full PR base and head SHAs. The
coordinator checks that both still match before authorizing merge. If either
SHA changed, the report is stale and blocks authorization until a fresh review
is complete. A clean report is evidence—not a guarantee of correctness or a
replacement for CI, branch protection, or required human approvals.

Focus findings on design, intended functionality and edge cases, complexity,
correctness, and tests. Ground each finding in changed code and available
project context; personal preference, cosmetic style, and nits are
nonblocking unless they violate a written project standard. Google's review
guidance likewise prioritizes design, functionality, and useful tests over
polishing every minor issue ([standard](https://google.github.io/eng-practices/review/reviewer/standard.html),
[what to look for](https://google.github.io/eng-practices/review/reviewer/looking-for.html)).
GitHub describes full-project context as improving review specificity and
accuracy ([Copilot code review](https://docs.github.com/en/copilot/concepts/agents/code-review));
use that context when available without treating model output as proof.
Use explicit criteria, structured evidence-bounded findings, a separate
evaluator/author role, and an adversarial check that each finding is real and
relevant, consistent with the local
[Agentic Eval skill](../../agentic-eval/SKILL.md). Its example numeric
scoring and optimizer loops are not adopted here: do not use unverified
numeric scores or broad autonomous fixing.

Allow at most **10 completed review rounds per branch/PR**. The first
completed reviewer report counts as round 1; a required code review and
security review for the same base/head pair form one pass. Stop at round 10,
preserve the count, and never launch round 11. At the cap, the author records
one explicit choice and non-empty rationale: `FIX_MANUALLY`,
`ACCEPT_FINDINGS_AND_REQUEST_MERGE`,
`ESCALATE_FOR_HUMAN_REVIEW`, or `CLOSE`. `ACCEPT_FINDINGS_AND_REQUEST_MERGE`
allows only normal merge consideration and never bypasses repository policy.
If a manual fix changes the head after the cap, the report is stale; obtain a
fresh human review or use a new branch/PR, not an 11th agent review on the
same branch/PR.

The coordinator-managed no-PR fast-forward workflow is unchanged. Record
review as `NOT_APPLICABLE`, launch no reviewer, and follow the existing
coordinator-reviewed and remote-verified integration path.

## Merge procedure

1. Confirm the coordinator authorized this exact PR after the worker's
   sign-off and a completed review pass whose base/head SHAs match the current
   PR. A `CLEAN` report, or at the cap an
   `AUTHOR_DECISION_RECORDED` report with choice
   `ACCEPT_FINDINGS_AND_REQUEST_MERGE`, is eligible for normal merge
   consideration only. Do not merge with a stale or blocked review, another
   author decision, missing required review, failed check, or unsatisfied
   branch-update requirement. Do not merge another worker's PR or treat an
   open PR as authorization.
2. Use the worker's own existing authentication through the configured
   GitHub CLI (`gh`) or supported GitHub integration/MCP tools, following the
   repository's configured merge method. For example, when using `gh` and
   merge commits are configured, use `gh pr merge <number> --merge`. If the
   repository requires a merge queue, use its normal queue-enabled merge
   process instead (for example, `gh pr merge <number> --auto --merge` when
   configured). `gh auth status`, when using the CLI, can confirm that it is
   signed in; it does not prove the worker has permission to merge this PR.
   An integration being available likewise does not prove merge permission.
3. Wait for GitHub to report the PR as merged. Fetch `origin`, identify the
   resulting merge SHA, and verify that the exact SHA is reachable from
   `origin/main` (for example, with
   `git merge-base --is-ancestor <merge-sha> origin/main`). For squash or
   merge-queue flows, verify the resulting remote merge SHA rather than
   requiring the original implementation commit to remain an ancestor.
4. Record the worker who submitted or queued the merge action as
   `merge_actor_worker_id` in the leaf status, and append the exact merge
   command, resulting SHA, remote verification method, and timestamp to the
   worker's progress evidence. The coordinator independently verifies the
   merge, refreshes the aggregate dashboard, and completes the post-merge
   memory review before marking the iteration `COMPLETE`.

The coordinator serializes authorization; it does not merge a worker PR on
the worker's behalf. The coordinator does not use its own credentials to
merge a worker PR, and workers must not share or request credentials. Never
use `--admin`, push directly to `main`, or override managed host or repository
policy to force a merge.

If the worker's merge permission is denied, a required check or review is
missing, or the host does not expose the normal merge tool, preserve the
branch and PR and report a sanitized blocker. Do not retry with another
identity, ask for a token, or silently transfer merge ownership to the
coordinator. Resume only when the normal authorization, permission, and
repository requirements are satisfied.
