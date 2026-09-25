# Structured Ralph task prompt generation

Turn a user's natural-language request into a bounded, evidence-based prompt
before planning, dispatching workers, or implementing. The generated prompt is
the execution contract for one Ralph task; it is not a verbatim copy of the
user's message.

## Read current context first

Use the refreshed active project as the source of truth. Read its current
project instructions and the task-defining plan, prompt or runner, status,
progress, decision, and test guidance that applies to the request. Load the
applicable skills, including the project's TDD guidance for behavior changes
and Project Memory guidance when relevant. Read the relevant project memory
index and category files, and validate memory against current sources and
authoritative instructions; stale, unsupported, or conflicting memory is not
a requirement. Inspect the available tools and their actual limits, such as
repository access, test runners, agent dispatch, GitHub PR creation, and
platform-specific verification. Mark a required but unavailable capability as
a gap instead of claiming it is available.

Do not treat the raw request as the only source of requirements or use memory
or tool availability to invent extra work. Keep evidence categories separate:
user intent comes from the user's request, while derived project requirements
must cite the current project source that establishes them.

## Preserve intent and bound the work

- Preserve the user's explicit scope: the objective, included work,
  exclusions, and requested deliverables. Paraphrase faithfully; do not
  silently narrow, broaden, replace, or reinterpret them.
- Distinguish user-stated requirements from project-derived requirements.
  Label any assumptions separately, explain why each is necessary, and keep
  them low-risk and reversible.
- Do not invent work such as features, cleanup, refactors, deliverables, or
  acceptance criteria. Add only project constraints needed to carry out the
  explicit request safely and consistently with current instructions.
- Surface material ambiguity that could change the objective, scope, risk,
  acceptance criteria, or integration path. Ask the user for clarification
  before finalizing the execution prompt, dispatching work, or editing. Do not
  hide a material decision in the assumptions section. For non-material
  uncertainty, record the smallest reasonable assumption explicitly.
- Bound the task to one useful Ralph iteration. Make exclusions and any work
  deferred to another iteration explicit.

## Required prompt structure

Write the prompt with each of these fields. Use `None` when a field genuinely
has no applicable entry rather than omitting it.

### Objective

State the observable outcome requested by the user.

### User-stated scope

List the explicit inclusions, exclusions, and deliverables, preserving their
meaning without copying unrelated or sensitive raw text.

### Derived project requirements

List only requirements imposed by current project instructions, plans,
acceptance conventions, or other authoritative sources. Identify the source
path for each requirement and keep these separate from user-stated scope.

### Assumptions

Record only necessary, non-material assumptions and their rationale. If an
assumption could change what the user gets, ask for clarification instead.

### Constraints and non-goals

State owned paths, relevant safety or compatibility constraints, explicit
non-goals, and anything that must not be changed.

### Applicable skills, validated project memory, and available tools

Name the skills to apply and the relevant memory lessons after validation.
List the tools and capabilities actually available for this iteration, along
with important limitations or unverified platforms. Do not claim a tool,
permission, or capability that has not been confirmed.

### Bounded work plan

Give a short, ordered plan for this iteration. For behavior changes, include
the required Red-Green-Refactor sequence. Keep each action traceable to the
objective or a cited project requirement.

### Acceptance criteria

State observable outcomes that decide whether the requested task is satisfied.
Keep criteria within the explicit user scope and cite any project-derived
criterion.

### Verification

List the narrowest relevant commands or procedures, the expected result for
each, and any environment gap that will remain. Do not present a test as run
or passed until it has actually been executed.

### Integration end condition

State the required branch, commit, PR process, status handoff, remote-main
verification, and post-merge memory-review condition. For a worker-owned PR,
state that the branch owner opens the PR and waits for the coordinator to
authorize that exact PR before the worker merges it with the worker's existing
authentication. Until authorization, keep the worker `AWAITING_MERGE` and do
not merge. Do not equate a pushed branch or open PR with completion.

### Clarifications needed

List material questions that must be answered before work begins. If any
remain open, the prompt is not ready for execution or worker dispatch.

## Use the prompt for execution and worker assignments

Treat the generated structured prompt as the source of truth for execution and
worker assignments, not the raw user message. The coordinator may divide the
prompt into smaller worker assignments, but each assignment must be a bounded
subset that preserves the applicable objective, constraints, acceptance
criteria, verification, and integration condition. Do not forward verbatim
user text to a worker when a sanitized, scoped assignment is sufficient.

A worker executes only the coordinator-provided structured prompt and its
exclusive assignment. If the prompt, ownership, or acceptance criteria are
missing or materially ambiguous, ask the coordinator rather than reconstructing
work from unrelated context or inventing a scope.

## Save the branch-local prompt safely

After the iteration branch is known and before its implementation work, save
the exact structured prompt that will govern that branch at:

`docs/decisions/<branch-slug>/prompt.md`

Derive `<branch-slug>` from the exact branch ref by lowercasing it and
replacing `/` with `-`. Link it from that branch's README.md at
`docs/decisions/<branch-slug>/README.md`; commit both records on the branch
before integration. A worker records its scoped structured assignment, not an
unneeded full conversation.

Sanitize the prompt before saving it. Never store secrets, credentials, tokens,
secret values, or unrelated private context. Do not persist a verbatim raw user
message when it contains such material or information unnecessary for the
task. Preserve intent with a minimal, faithful, redacted summary; use
placeholders such as `[REDACTED]` only when a sensitive value must be
acknowledged to explain a constraint. Include no private context unrelated to
the objective.
