---
name: project-memory
description: Capture and maintain concise, evidence-backed project lessons in category-organized repository memory, especially after a merged Ralph iteration.
---

# Project Memory

Use version-controlled project memory to preserve reusable knowledge between
sessions. Memory is authored guidance, not a task journal or a substitute for
the current source, tests, or acceptance criteria.

## Before applying memory

Read `.github/memory/README.md` and the relevant category files before
planning or changing work. Check each lesson against the active project's
current sources; stale or conflicting memory never overrides verified code,
tests, or project instructions. In another repository, use its documented
memory store rather than writing into this skill's repository.

## When to capture a lesson

Review learnings after every Ralph iteration's implementation content has been
merged and verified on remote `main`. Also capture a confirmed recurring
pattern, correction, non-obvious constraint, or costly gotcha when it is
discovered. A memory review is required; a new entry is not required when the
iteration produced no durable, transferable lesson.

## Capture procedure

1. Review evidence from the iteration: changed sources, test results, review
   feedback, corrections, and integration outcomes. Identify the root cause or
   invariant rather than retelling the task.
2. Generalize to the highest-level rule that remains accurate across cases.
   Prefer a concise principle or constraint over a chain of literal `if`
   statements. Include a condition only when it materially changes where the
   rule applies.
3. Confirm the lesson from a reliable source or repeatable observation. One
   successful run or an unverified assumption is not enough to establish a
   general rule.
4. Search the index and category files for duplicates or conflicts. Refine an
   existing lesson before adding another; correct or remove guidance that has
   become stale.
5. Put the lesson in its primary category and keep it concise. Record a
   specific gotcha only when it is hard to infer, likely to recur, and useful
   beyond the current task. Cross-reference rather than duplicate a lesson
   across categories.
6. Recheck the entry for accuracy, useful scope, working links, and sensitive
   data before committing it.

## Memory format and categories

The canonical store is `.github/memory/`. Its `README.md` is the category
index; store lessons in one Markdown file per category, creating a category
file only when it has a useful entry. Use this format:

```markdown
### [Short, rule-oriented heading]
- **Rule:** [Reusable constraint or practice.]
- **Why:** [Evidence or consequence that makes the rule useful.]
- **Scope:** [Only when applicability needs clarification.]
- **Gotcha:** [Only for a specific, non-obvious trap worth retaining.]
```

Keep entries focused on durable project knowledge. Do not store task
chronologies, transient environment state, secrets, personal data, or
unsupported assumptions.

## Ralph post-merge updates

1. Wait until the iteration's implementation content is merged and its merge
   result is verified on fetched `origin/main`.
2. Review the iteration's evidence and update the relevant category when a
   durable lesson was learned.
3. Submit any memory change through the repository's normal integration
   process. In Git workflows, create a fresh follow-up branch from the latest
   `origin/main`, then merge and verify the memory update; never write directly
   to shared `main` or amend an already merged branch.
4. Treat the memory follow-up as part of the same iteration, not a new Ralph
   iteration. Do not recursively run another memory review for the
   memory-only follow-up.
5. When there is no new reusable lesson, leave the memory files unchanged and
   record that review outcome in the active progress or status record when one
   exists.
