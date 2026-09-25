# Ralph Branch Decision Records — Status-First Agent Reporting

- **Branch:** `ralph/agent-status-reporting-20260924-2313`
- **Branch slug:** `ralph-agent-status-reporting-20260924-2313`
- **Base `origin/main` SHA:** `9558f99cc34cbed8dd1d24f4f15fc03f5d78b6ea`
- **Latest rebase onto `origin/main`:** `5e673fa5235b99bd36c1cd56ea7d2dab6e7562c0`
- **Latest fetched `origin/main`:** `1d74599aab767c4ee9ad331874b7b6dacd3c4ba8`
- **Implementation commit SHA:** `4097b48af54c3e1c31740ffcffcf2bb0dbca9ffb`
- **Run:** `copilot_skills-agent-status-reporting-20260924`
- **Agents:** coordinator, worker-01, worker-02
- **PR:** `NOT_OPENED` under the repository's existing verified fast-forward
  integration path; use a PR if current branch policy requires one.

## Agent records

- [Coordinator integration record](agents/coordinator/pr-not-opened.md)
- [Worker-02 child record](../ralph-agent-status-contract-worker-02-20260924-2324/agents/worker-02/pr-not-opened.md)
- [Worker-01 child record](../ralph-agent-status-reporting-worker-01-20260925-0602/agents/worker-01/pr-not-opened.md)

## Decisions

### Report run and agent states instead of binary completion text

- **Context:** An assistant can return a progress update while authorized
  agents, checks, review, or integration are still running. A binary
  completion label makes that nonterminal update look like a failure.
- **Decision:** Begin interim and final reports with the run's explicit
  overall status and show every assigned agent's exact current state and next
  action.
- **Rationale:** The run dashboard already tracks `IN_PROGRESS`, `BLOCKED`,
  and `COMPLETE`, while agent leaves distinguish queued, running, awaiting
  merge, blocked, and terminal states.
- **Consequences:** Use `IN_PROGRESS` whenever work can still proceed,
  `BLOCKED` only when external intervention is required, and `COMPLETE` only
  after all acceptance, verification, integration, and memory gates pass.

### Write the report contract test before its documentation implementation

- **Context:** The reporting format is agent behavior encoded in shared skill
  and workflow guidance.
- **Decision:** Integrate a focused contract test that demonstrates the
  current missing behavior before the documentation worker starts; run it to
  Green after the guidance is updated.
- **Rationale:** This gives the prompt/pipeline change an observable,
  repeatable regression check without inventing an application runtime test.
- **Consequences:** A short-lived expected Red is recorded as test evidence,
  not as a task blocker.
