# Agent Decision Record — PR Pending

- **Run / parent request:** `translated-ralph-prompt-skills-20260925-0108` /
  `skills-routing-20260925-0108`
- **Task:** `generate-relevant-skills-in-translated-ralph-prompt`
- **Agent:** `worker-02 - shared Ralph prompt skill generation` (`worker-02`)
- **Runtime agent ID:** Not provided (`null`)
- **Iteration:** `1`
- **Branch:** `ralph/translated-ralph-skills-worker-02-20260925-0108`
- **Worktree:** `/Users/jrblankenhorn/copilot_skills.worktrees/ralph-translated-ralph-skills-worker-02-20260925-0108`
- **Base `origin/main`:** `485b4a64c871f581f9295e46c867b188b0e3ccee`
- **Rebased onto `origin/main`:** Not applicable.
- **Implementation commit SHA:** `3102b30cd012055055aa5c3dfe6e435620249459`
- **PR:** Pending; no number or PR URL exists yet. The branch is published.
- **Suggested PR creation URL:** <https://github.com/jrblankenhorn1007/copilot_skills/pull/new/ralph/translated-ralph-skills-worker-02-20260925-0108>

## Decisions

### Use the canonical Ralph Loop skill as the prompt authoring owner

- **Context:** A search of the shared `.github/skills` and `.github/agents`
  catalog found no separate Ralph prompt translator. The
  `copilot-instructions-blueprint-generator` description and output concern
  project-specific `copilot-instructions.md`, not a translated Ralph prompt.
- **Alternatives:** Change the generic Copilot-instructions blueprint
  generator, create another Ralph prompt skill, or add prompt-generation
  guidance to the canonical Ralph Loop workflow.
- **Decision:** Update `.github/skills/ralph-loop/SKILL.md`, including its
  activation description and a concise prompt-generation/translation
  procedure.
- **Rationale:** Ralph Loop owns the development lifecycle and the current
  prompt/plan discovery; it is the directly relevant shared workflow and
  narrowest existing owner.
- **Consequences:** Prompt authors are directed to select relevant skills
  dynamically from task evidence and skill descriptions/triggers and to put
  the resulting list into the generated prompt itself.

### Generate a short, task-specific skills section

- **Context:** The acceptance criteria require a visible section in the
  translated prompt and prevent the generator from dumping every skill or
  guessing a static stack.
- **Alternatives:** Keep skills only as generator metadata, add a fixed
  all-skills list, or select candidates from the current task and both
  canonical and project-local catalogs.
- **Decision:** Require `## Relevant skills` in prompt output, with one entry
  per selected skill naming its verified path/link and task or lifecycle
  reason. Always select Ralph Loop and Project Memory, select TDD for behavior
  changes, and include domain skills only when their descriptions/triggers
  match. Verify local paths and avoid duplicates.
- **Rationale:** This states the instructions actually available to the
  downstream Ralph agent while keeping the list grounded and minimal.
- **Consequences:** The section must be generated from the current project's
  catalogs; unavailable local paths and nonmatching skills are omitted.

### Keep aggregate status with the coordinator and do not merge

- **Context:** The worker assignment prohibits editing `docs/ralph-status.md`
  and merging this branch. The branch/agent leaf and decision records are
  worker-owned.
- **Alternatives:** Update the dashboard directly or merge the branch after
  checks.
- **Decision:** Create only this worker's leaf and decision records, publish
  the feature branch, and await coordinator integration.
- **Rationale:** This preserves the assigned ownership boundary and lets the
  coordinator synchronize the aggregate status.
- **Consequences:** `docs/ralph-status.md` still needs this leaf indexed;
  no remote merge or memory review is claimed by the worker.

## Verification

- The new contract test showed the expected Red before the skill procedure
  was added. After clarifying the instruction/test wording, the targeted test
  and the full 11-test contract suite passed.
- `git diff --check origin/main...HEAD` and
  `git show --check --format=oneline HEAD` passed.
- The published branch was verified at implementation commit
  `3102b30cd012055055aa5c3dfe6e435620249459`.
- After the worker-owned status/progress files were added, the full contract
  suite was rerun. It now has one failure in
  `test_docs_status_dashboard_indexes_every_branch_agent_folder`: this new
  status path is not yet linked in coordinator-owned
  `docs/ralph-status.md`. The assigned prompt-skill test still passes.

## Recovered issues

- An intermediate targeted-test run reported six text-contract mismatches
  because the first instruction draft did not state the local-catalog,
  no-static-list, explicit-section, domain-skill, and unavailable-path rules
  in the tested wording. The procedure was made explicit and the contract
  test was aligned to the required `## Relevant skills` heading; the
  targeted test and full suite then passed.

## Unresolved blockers

- PR creation is pending. The GitHub MCP tools available in this session are
  read-only, and `gh` is not installed. The branch is pushed; the URL above
  can be used by an authorized coordinator to create the normal PR.
- The coordinator must index this leaf in the coordinator-owned
  `docs/ralph-status.md`; this is also required to clear the single full-suite
  dashboard-index failure. The worker did not edit the aggregate dashboard.
