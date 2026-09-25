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
- **Skill improvements**: Comparing another skill's activation, helper choices,
  and non-activation boundaries before and after edits

---

## Evaluating a Skill Improvement

When changing another skill's trigger, helper guidance, examples, or
procedure, use a small paired evaluation rather than relying on a single
critique. A static read can assess whether the intended cues are written down;
it does not execute skill selection or prove runtime routing. Claim observed
activation or helper selection only when a representative run and its
evidence actually show it.

### Freeze cases before editing

Before changing the skill, freeze a small, representative set of requests
(usually 3–6) and the expected handling for each. Reuse the same case IDs,
request wording, success criteria, and evaluator/tool setup for the baseline
and revised skill. Do not tune the cases after seeing results. If new evidence
requires another case, keep the original set and mark the addition.

Include at least:

- A clear in-scope request that should activate the target skill.
- A natural paraphrase that tests the same trigger and expected supporting
  helper selection.
- A negative or out-of-scope request where the target skill must not activate.

For every case, record the request, expected primary skill, expected helper(s)
(write `none` when none are expected), unwanted skill selections, expected
outcome, and applicable protected invariants. This makes both missed
activation and unwanted activation visible.

### Compare with explicit evidence

Review the frozen cases against the baseline before editing, then compare the
revised skill against the same cases using the same criteria and evaluator
setup. Keep the evidence and outcome for each case; note any change in model,
prompt, tool, or evaluation mode that makes a comparison uncertain.

Use one of these outcomes and record a short reason:

- `PASS`: the available evidence supports the expected behavior at the level
  actually tested.
- `FAIL`: the evidence contradicts an expected behavior.
- `UNKNOWN`: evidence is insufficient to decide, such as an unobserved
  runtime route.
- `EVALUATOR_ERROR`: the evaluator or tool failed or returned an invalid
  result, so no valid judgment was produced.

`UNKNOWN` and `EVALUATOR_ERROR` are distinct from each other and from
`PASS`/`FAIL`; neither counts as a pass. A text review may confirm that a
trigger or helper rule is explicit, but without an observable run or trace the
runtime activation result remains `UNKNOWN`.

### Keep protected invariants as hard gates

Check each protected boundary independently of any quality score:
safety, authorization, privacy, consent, and external-side-effect limits.
Do not combine them into a weighted rubric or let a better quality score
compensate for a failed boundary. Do not perform an external action merely to
test whether the skill would request or authorize it.

Any regression in a protected invariant is a hard stop: reject that candidate
and do not continue refining it. A protected boundary that is `UNKNOWN` or
`EVALUATOR_ERROR` is not verified and prevents a passing result until it can
be evaluated safely.

### Bound revisions and stop conditions

Set a small hard cap before editing (for example, at most three revisions;
the baseline is not a revision). Compare every candidate with the same frozen
cases and the baseline. Stop when the target criteria are met and all
protected gates pass, when the cap is reached, or earlier if the evidence
shows no improvement in the target behavior or revisions have stopped
converging. Stop immediately on a protected-invariant regression. At the cap
or on an inconclusive result, report what remains unknown; do not label the
last candidate a pass merely because it is the newest.

### Worked example

Illustrative text review only; this is not a benchmark or a measurement of
runtime routing. Suppose a skill selector's baseline trigger only says
“Use for skill-related tasks,” and a revision clarifies its boundary. Freeze
these cases before editing:

| Frozen request | Expected selection (primary; helpers; unwanted) | Baseline text evidence | Revised text evidence |
| --- | --- | --- | --- |
| “Which skill should check whether our README reflects changed CLI options?” | Primary: Agent Skill Stack; helper: Docs Sync Audit; unwanted: TDD when no code behavior changed. | The broad trigger does not specify the helper. | The text directs skill-selection requests to Agent Skill Stack and names Docs Sync Audit for documentation drift. Runtime selection remains `UNKNOWN`. |
| “Our flags moved—what will catch stale examples?” | Primary: Agent Skill Stack; helper: Docs Sync Audit; unwanted: TDD for a docs-only request. | The paraphrase and helper choice are not stated. | The same selection and helper rule is explicit for this paraphrase. Runtime selection remains `UNKNOWN`. |
| “Check whether the README matches current CLI options.” | Primary: Docs Sync Audit; helper: none; unwanted: Agent Skill Stack. | The trigger does not distinguish selecting a skill from directly requesting a documentation audit. | The text assigns a direct documentation-drift request to Docs Sync Audit, outside the selector's role. Runtime selection remains `UNKNOWN`. |

The revised text is clearer against these frozen expectations; no runtime
selection was exercised, so the example supports no claim that routing
improved in practice.

---

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
