Synchronize the open worktree-isolation change in PR #7 without modifying its
published branch. Replay only its unique implementation commit
7fd155ba0bd4814f85a890207bae71b4e13a7f8a onto a fresh branch based on the
exact fetched origin/main SHA 741f23521dbfc2465d5f0943de4451c0a3a42f5a.
Preserve current main content, tests, and history; resolve conflicts
minimally; update the recovered and replacement branch status/progress/decision
records and the dashboard; run the relevant Ralph, routing, specialist,
ownership, Resource Manager, syntax, and whitespace checks; then open a
replacement PR. Do not merge without independent exact-SHA Code and Security
reviews, required checks, and normal approvals. Do not spawn reviewers unless
a fresh Resource Manager inventory and atomic reservations permit it. Keep
the original PR #7 branch and worktree unchanged until replacement integration
is verified. Edit only the paths listed in the task sign-in.
