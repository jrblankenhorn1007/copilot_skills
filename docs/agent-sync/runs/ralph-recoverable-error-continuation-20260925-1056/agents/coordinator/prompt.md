Ralph iteration: recoverable-error-continuation-20260925-1056

Revise the canonical Ralph Loop agent's terminal conditions so a recoverable operational error does not stop the run while safe, authorized work remains. Diagnose a failed operation, use a bounded cause-based retry or a documented authorized alternative, never repeat a known-denied operation, and continue independent ready work. Mark an individual workstream blocked only when it needs external intervention; mark the overall run blocked only when no safe authorized action can advance. Do not report completion until all requested acceptance, verification, integration, and required memory gates pass.

Scope: `.github/agents/ralph-loop.agent.md` and `.github/skills/ralph-loop/tests/test_multi_agent_contract.py`. Do not edit the currently owned `.github/skills/ralph-loop/SKILL.md` or another session's branches. Add a focused regression test that fails against the current operational-error stop condition, then update the agent guidance and run the targeted test and full Ralph contract suite.

This is one cohesive documentation-and-contract-test scope. No worker is dispatched because Resource Manager reports zero available capacity; record that limitation and the reason in the branch status/progress records.
