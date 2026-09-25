---
description: |-
    Patterns and techniques for evaluating and improving AI agent outputs. Use this skill when:
    - Implementing self-critique and reflection loops
    - Building evaluator-optimizer pipelines for quality-critical generation
    - Creating test-driven code refinement workflows
    - Designing rubric-based or LLM-as-judge evaluation systems
    - Adding iterative improvement to agent outputs (code, reports, analysis)
    - Measuring and improving agent response quality
metadata:
    github-path: skills/agentic-eval
    github-ref: refs/heads/main
    github-repo: https://github.com/github/awesome-copilot
    github-tree-sha: 2322ac3a69fa63b58268525481bf684b9ddf51a3
name: agentic-eval
---
# Agentic Evaluation Patterns

Patterns for self-improvement through iterative evaluation and refinement.

## Overview

Evaluation patterns enable agents to assess and improve their own outputs, moving beyond single-shot generation to iterative refinement loops.

```
Generate → Evaluate → Critique → Refine → Output
    ↑                              │
    └──────────────────────────────┘
```

## When to Use

- **Quality-critical generation**: Code, reports, analysis requiring high accuracy
- **Tasks with clear evaluation criteria**: Defined success metrics exist
- **Content requiring specific standards**: Style guides, compliance, formatting
- **Improving an existing Agent Skill**: Compare a specific `SKILL.md` revision
  against the same positive, negative, and failure cases as its baseline.

---

The code below sketches evaluation patterns, not production-ready PASS gates.
For example, `all()` returns true for an empty critique, and a score cannot
establish that every required check ran. Treat missing criteria, malformed
evaluator responses, unavailable tools, and unrun checks as unknown rather
than successful. Use the explicit gates in
[Evaluating and improving an existing Agent Skill](#evaluating-and-improving-an-existing-agent-skill)
before claiming an improvement.

## Pattern 1: Basic Reflection

Agent evaluates and improves its own output through self-critique.

```python
def reflect_and_refine(task: str, criteria: list[str], max_iterations: int = 3) -> str:
    """Generate with reflection loop."""
    output = llm(f"Complete this task:\n{task}")

    for i in range(max_iterations):
        # Self-critique
        critique = llm(f"""
        Evaluate this output against criteria: {criteria}
        Output: {output}
        Rate each: PASS/FAIL with feedback as JSON.
        """)

        critique_data = json.loads(critique)
        all_pass = all(c["status"] == "PASS" for c in critique_data.values())
        if all_pass:
            return output

        # Refine based on critique
        failed = {k: v["feedback"] for k, v in critique_data.items() if v["status"] == "FAIL"}
        output = llm(f"Improve to address: {failed}\nOriginal: {output}")

    return output
```

**Key insight**: Use structured JSON output for reliable parsing of critique results.

---

## Pattern 2: Evaluator-Optimizer

Separate generation and evaluation into distinct components for clearer responsibilities.

```python
class EvaluatorOptimizer:
    def __init__(self, score_threshold: float = 0.8):
        self.score_threshold = score_threshold

    def generate(self, task: str) -> str:
        return llm(f"Complete: {task}")

    def evaluate(self, output: str, task: str) -> dict:
        return json.loads(llm(f"""
        Evaluate output for task: {task}
        Output: {output}
        Return JSON: {{"overall_score": 0-1, "dimensions": {{"accuracy": ..., "clarity": ...}}}}
        """))

    def optimize(self, output: str, feedback: dict) -> str:
        return llm(f"Improve based on feedback: {feedback}\nOutput: {output}")

    def run(self, task: str, max_iterations: int = 3) -> str:
        output = self.generate(task)
        for _ in range(max_iterations):
            evaluation = self.evaluate(output, task)
            if evaluation["overall_score"] >= self.score_threshold:
                break
            output = self.optimize(output, evaluation)
        return output
```

---

## Pattern 3: Code-Specific Reflection

Test-driven refinement loop for code generation.

```python
class CodeReflector:
    def reflect_and_fix(self, spec: str, max_iterations: int = 3) -> str:
        code = llm(f"Write Python code for: {spec}")
        tests = llm(f"Generate pytest tests for: {spec}\nCode: {code}")

        for _ in range(max_iterations):
            result = run_tests(code, tests)
            if result["success"]:
                return code
            code = llm(f"Fix error: {result['error']}\nCode: {code}")
        return code
```

---

## Evaluation Strategies

### Outcome-Based
Evaluate whether output achieves the expected result.

```python
def evaluate_outcome(task: str, output: str, expected: str) -> str:
    return llm(f"Does output achieve expected outcome? Task: {task}, Expected: {expected}, Output: {output}")
```

### LLM-as-Judge
Use LLM to compare and rank outputs.

```python
def llm_judge(output_a: str, output_b: str, criteria: str) -> str:
    return llm(f"Compare outputs A and B for {criteria}. Which is better and why?")
```

### Rubric-Based
Score outputs against weighted dimensions.

```python
RUBRIC = {
    "accuracy": {"weight": 0.4},
    "clarity": {"weight": 0.3},
    "completeness": {"weight": 0.3}
}

def evaluate_with_rubric(output: str, rubric: dict) -> float:
    scores = json.loads(llm(f"Rate 1-5 for each dimension: {list(rubric.keys())}\nOutput: {output}"))
    return sum(scores[d] * rubric[d]["weight"] for d in rubric) / 5
```

---

## Best Practices

| Practice | Rationale |
|----------|-----------|
| **Clear criteria** | Define specific, measurable evaluation criteria upfront |
| **Iteration limits** | Set max iterations (3-5) to prevent infinite loops |
| **Convergence check** | Stop if output score isn't improving between iterations |
| **Log history** | Keep full trajectory for debugging and analysis |
| **Structured output** | Use JSON for reliable parsing of evaluation results |

---

## Quick Start Checklist

```markdown
## Evaluation Implementation Checklist

### Setup
- [ ] Define evaluation criteria/rubric
- [ ] Set score threshold for "good enough"
- [ ] Configure max iterations (default: 3)

### Implementation
- [ ] Implement generate() function
- [ ] Implement evaluate() function with structured output
- [ ] Implement optimize() function
- [ ] Wire up the refinement loop

### Safety
- [ ] Add convergence detection
- [ ] Log all iterations for debugging
- [ ] Handle evaluation parse failures gracefully
```

---

## Evaluating and improving an existing Agent Skill

Use this procedure when the goal is to refine an identified `SKILL.md`, not
to discover, install, or select a skill stack. If the target or desired
outcome is unclear, ask before editing. An evaluation is a comparison of
observed behavior under two versions, not a vote that the revised wording
"looks better."

1. **Freeze the baseline and the guardrails.** Record the target path and
   baseline commit or saved version before changing it. Read its trigger
   description, instructions, license, upstream attribution, relevant
   source/tests and documentation, and applicable
   [Project Memory](../project-memory/SKILL.md) lessons (validate them against
   current sources). State one observable improvement goal. List protected
   invariants: previously supported cases, scope and permissions (including
   read-only or installation-consent boundaries), safety and privacy rules,
   license/attribution, and any project-specific requirements. Do not relax an
   invariant to improve a score.
2. **Freeze a small case set and its oracles before editing.** For each case,
   record the prompt/task, expected activation or non-activation, expected
   output/action, required evidence, and whether it is a mandatory gate.
   Include a direct request, a paraphrase, an indirect/supporting request
   when applicable, an unrelated request that must *not* activate the skill,
   a negative or boundary case, and missing-input/evaluator-error cases.
   Prefer deterministic checks (tests, command exit codes, cited source and
   documentation lines) over subjective scoring. If using an LLM judge, fix
   its rubric and required fields in advance; keep its score separate from
   mandatory correctness and invariant gates.
3. **Measure the unchanged baseline.** Replay the frozen cases with a
   recorded harness, tool availability, model/settings, and repetition count
   (fixed seed where supported); retain the input, output, command/result,
   and evidence per case. Use the same setup for the revised version. If a
   live skill-routing harness is unavailable, record activation cases as
   not run and their mandatory gate as `UNKNOWN`; reading the trigger is not
   a measured activation test. A missing test, evaluator timeout, empty or
   invalid structured response, or unavailable source is `UNKNOWN` (or `BLOCKED`
   when work cannot proceed), **never `PASS`**. Only an executed check with
   the expected observable result and required evidence can be `PASS`;
   an executed contrary result is `FAIL`.
4. **Make one minimal, evidence-based revision.** Change only instructions
   tied to an observed gap; keep the frozen cases and invariants unchanged.
   For executable behavior, follow
   [TDD](../tdd/SKILL.md): run the relevant failing behavior test before the
   change, implement to Green, and rerun after refactoring. For documentation
   only, do *not* invent a Red phase: check frontmatter, links, examples and
   the actual source/command claims. Use
   [Docs Sync Audit](../docs-sync-audit/SKILL.md) to distinguish confirmed
   drift (both sides cited) from inferred gaps; a docs check cannot by itself
   prove better skill activation.
5. **Replay and adjudicate.** Run the *same* cases and checks on the revised
   version and compare case by case. Validate that the evaluator returned
   all required case IDs and legal statuses before looking at its score;
   missing IDs or parse errors invalidate that evaluation. You may retry a
   transient evaluator failure once within the budget, but preserve the
   failure and retry evidence. Require every mandatory case and protected
   invariant to `PASS`, with no new regression, before accepting a revision.
   Treat any `UNKNOWN`, `BLOCKED`, or unrun mandatory check as an
   unresolved gate, not an implicit success.
6. **Stop and report honestly.** Allow at most two focused revisions after
   the baseline (or a smaller agreed budget); stop sooner on a protected
   invariant failure, no improvement on the frozen cases, an unresolved
   evaluator error, unavailable required evidence, or user interruption.
   Report both version identifiers, the unchanged case set, observed
   before/after results, exact checks, regressions, unknowns, and remaining
   next action. Claim a measured improvement only when both versions were
   actually exercised under comparable conditions and the observed gain
   survives all mandatory gates. If not, say "not established" rather than
   substituting a favorable judge score or polished prose. After a verified
   merge, review transferable lessons through Project Memory; do not use
   memory as a substitute for current evidence.

### Worked example (illustrative, not a measured improvement)

Suppose a request proposes clarifying a documentation-audit skill so that an
unavailable package manifest cannot be reported as "all scripts match."
Save its unchanged `SKILL.md` as the baseline; preserve its MIT notice,
upstream attribution, and read-only audit default. Prepare a tiny fixture:
the README documents `npm run build`, while `package.json` has only a `test`
script. Freeze these cases *before* proposing wording:

| Case | Task/probe | Required expected result |
| --- | --- | --- |
| Direct | "Audit README scripts against package.json." | Activate the audit; cite the README claim and missing `build` script in the manifest. |
| Paraphrase | "Are our setup commands still in sync with the package scripts?" | Activate and check the same claim, not just the wording. |
| Non-activation | "Write a launch announcement." | Do not activate the documentation audit. |
| Missing source | "Audit scripts," but the manifest is inaccessible. | State `UNKNOWN`/`BLOCKED`; never report "all scripts match." |
| Evaluator error | The case evaluator returns `{}` or times out. | Mark the check `UNKNOWN`; do not let an empty result count as `PASS`. |

First run these unchanged cases on the baseline and record what actually
happens. **Only if a case exposes a gap**, propose the smallest instruction
clarifying source evidence and unknown results. For a documentation-only
revision, verify the new wording, links, and claims against the audit's
source and run the same cases again; preserve its read-only invariant.
If the baseline and revision cannot both be exercised, the comparison for
those cases remains unrun/`UNKNOWN`: this example specifies expected
behavior but asserts no observed win. A real report would attach the
before/after case records and exact verification results.
