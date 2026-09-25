# Before/after routing checks for an existing Skill Stack

Use this procedure only to check how an existing or proposed Skill Stack
selects Skills for the user's outcome. It does not turn Agent Skill Stack
into a generic Skill editor, a runtime router, or a performance evaluator.
The [local index and project profile](local-index-and-profiles.md) help with
discovery and routing preferences; a profile alone cannot force a client to
activate a Skill.

## Fix the role contract before changing the stack

1. Identify the current active profile, installed Skill identities, index
   roots, and the particular Skill revision or route proposed for change.
   Resolve same-name duplicates and maintain the
   [source, safety, and consent gates](security-installation.md). A proposed
   edit to an existing Skill or profile needs an explicit review/approval,
   just as a new installation does; do not overwrite or install speculatively.
2. Define the *current* and *intended* role outcomes for four small, synthetic
   selection-only requests. Let `P` be the one primary for the main outcome
   and `H` the optional helper for a stated quality, accuracy, or compliance
   need. Freeze the four case meanings and expected roles before the baseline
   trial; do not replace a failed case with an easier one later.

| Probe for this stack | Intended primary | Intended helper | Exclusion |
| --- | --- | --- | --- |
| **Direct**: states the main outcome in ordinary task words | `P` | none unless the task actually needs `H` | No second primary or unrelated Skill |
| **Paraphrase**: same outcome with different words, no Skill name or exact route label | same `P` | same boundary as direct | A keyword-only match is insufficient |
| **Supporting**: same main task **plus** an explicit need handled by `H` | `P` | `H` at its defined handoff | No unrelated helper or duplicate primary |
| **OUT-OF-SCOPE / negative**: a task outside this stack, e.g. editing one already-known Skill or finding a single known Skill | no match for this stack | none from this stack | Neither `P` nor `H`; a different Skill or general agent may be appropriate |

Record an *intended delta* before the change if a capability is not yet
available: the baseline may correctly produce no match (or `P` without a
not-yet-added `H`) while the proposed result is `P` (or `P` plus `H`).
Previously correct cases must stay correct, and the negative must remain a
no-match. For an excluded task, no match means **this stack is not selected**;
it does not prohibit another appropriate Skill from working on the task.
Add a targeted negative for any known near-collision with a globally
installed Skill, but do not expand the stack's own activation description to
absorb that request.

## Observe baseline, change, and after-check

1. In the actual target host/profile when possible, present the frozen
   synthetic cases to a *selection-only* dry run, with no Skill execution,
   account actions, publishing, or external writes. Note whether the host
   visibly selected `P`, `H`, neither, or another Skill. If this cannot be
   observed without side effects, mark the host check not run; do not
   substitute `skill_index.py search`, a profile preview, or prose inspection
   for an activation observation. Those can verify discoverability and
   configuration, not real host recall.
2. Preview the proposed revision and its source/safety implications. Apply
   an installation, Skill update, or profile update **only after user
   confirmation**. Do not overwrite an existing destination via the staged
   installer; for profile edits, preview first and require explicit approval
   before `project_profile.py --update --apply`. Rebuild the local index after
   an approved installed-Skill or profile update.
3. Repeat the **same** selection-only cases with the same host, active
   profile, and relevant Skill set except for the approved change. Compare
   observations to the predeclared intended roles, not to a retrospective
   interpretation of the results. A trial that runs against a different
   client, model, or profile is not an apples-to-apples before/after check;
   disclose the difference and mark the comparison unverified.

## Admission and handoff

- **Admit** the changed route or Skill to the proposed stack only when its
  source and consent gates still pass, all mandatory after-case roles are
  observed as expected, no previously passing case regresses, the negative
  remains a no-match, and no new overlap or excessive helper permission is
  introduced. A failed or unrun mandatory case is not a pass.
- **Do not adopt on failure or uncertainty.** Keep the prior stack active
  where possible, or request approval for a safe rollback of a change already
  applied. Narrow the conflicting route or Skill description and repeat the
  *same* probes; do not weaken the cases or add a broad trigger merely to
  make the result pass. Stop for user direction when safe observation or
  rollback is unavailable.
- **Handoff, not duplication:** Agent Skill Stack owns selection, primary /
  helper boundaries, and these recall checks. Use
  [Agentic Eval](../../agentic-eval/SKILL.md) to evaluate the quality of a
  Skill's instructions or produced results with its own criteria and bounded
  refinement; it does not replace this routing gate. When a Skill or workflow
  update may leave examples or docs inconsistent with actual source or
  configuration, use the read-only
  [Docs Sync Audit](../../docs-sync-audit/SKILL.md) for that *specific* drift
  check; it does not prove activation.
- **Report honestly in plain language:** say “4/4 safe routing examples
  selected the intended primary/helper or stayed out of scope” only if all
  four were actually observed in the target host. Otherwise say “Routing
  could not be verified here,” identify the blocked case in everyday
  language, and do not claim a higher recall rate, measured improvement,
  installation safety, or a passed safe trial without evidence.

Keep role expectations and synthetic examples transient during the check.
Never collect or persist users' prompt histories, per-probe hit/miss logs,
routing feedback, or private user requests in the profile, index, lockfile,
or documentation. On request, a technical explanation may show **synthetic**
case types and intended/observed roles without retaining raw user prompts.
