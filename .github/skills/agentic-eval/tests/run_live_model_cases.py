#!/usr/bin/env python3
"""Run the frozen skill and agent instruction cases through OpenCode."""

from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import random
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence


ROOT = Path(__file__).resolve().parents[4]
MATRIX_PATH = Path(__file__).with_name("live_model_cases.json")
REQUIRED_RESULT_FIELDS = {
    "case_id",
    "selected_skill",
    "selected_agent",
    "actions_taken",
    "communication_plan",
    "summary",
    "safety_gate",
}
TOKEN_ALIASES = {
    "input_tokens": ("input_tokens", "inputTokens"),
    "output_tokens": ("output_tokens", "outputTokens"),
    "total_tokens": ("total_tokens", "totalTokens"),
}
MODEL_ID_PATTERN = re.compile(
    r"(?<![A-Za-z0-9_./-])([A-Za-z0-9_.-]+/gpt-6-luna)(?![A-Za-z0-9_.-])"
)


class LiveModelBlocked(RuntimeError):
    """The requested live model or execution setup is not available."""


class EvaluationError(RuntimeError):
    """The model runner failed to produce a usable evaluation result."""


def validate_observed_sessions(
    parent_session_id: Optional[str],
    observed_session_ids: Optional[Sequence[str]],
) -> List[str]:
    observed = list(observed_session_ids or [])
    if (
        not isinstance(parent_session_id, str)
        or not parent_session_id.strip()
        or not observed
        or any(not isinstance(item, str) or not item.strip() for item in observed)
        or parent_session_id not in observed
        or len(observed) != len(set(observed))
    ):
        raise LiveModelBlocked(
            "Live execution requires a fresh host session inventory with the "
            "registered parent session included exactly once."
        )
    return observed


def resource_manager_call(root: Path, *arguments: str) -> Dict[str, Any]:
    manager = root / ".github" / "skills" / "resource-manager" / "scripts" / "resource_manager.py"
    if not manager.is_file():
        raise LiveModelBlocked("The Resource Manager CLI is missing.")
    try:
        completed = subprocess.run(
            [sys.executable, str(manager), *arguments],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired as error:
        raise LiveModelBlocked("Resource Manager admission timed out.") from error
    if completed.returncode != 0:
        raise LiveModelBlocked(
            "Resource Manager denied admission or could not update its registry."
        )
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise LiveModelBlocked(
            "Resource Manager returned an invalid admission record."
        ) from error
    if not isinstance(result, dict):
        raise LiveModelBlocked("Resource Manager returned an invalid admission record.")
    return result


def reserve_live_test_worker(
    root: Path,
    parent_session_id: str,
    observed_session_ids: Sequence[str],
) -> Dict[str, str]:
    observed = validate_observed_sessions(parent_session_id, observed_session_ids)
    worker_id = f"live-model-eval-{os.getpid()}"
    command = [
        "reserve",
        "--agent-id",
        worker_id,
        "--parent-id",
        parent_session_id,
        "--role",
        "worker",
    ]
    for session_id in observed:
        command.extend(["--observed-session", session_id])
    reservation = resource_manager_call(root, *command)
    agent = reservation.get("agent")
    if not isinstance(agent, dict) or not isinstance(agent.get("reservation_id"), str):
        raise LiveModelBlocked("Resource Manager returned no live worker reservation.")
    reservation_id = agent["reservation_id"]
    runtime_id = f"live-model-eval-runner-{os.getpid()}"
    try:
        resource_manager_call(
            root,
            "activate",
            "--agent-id",
            worker_id,
            "--reservation-id",
            reservation_id,
            "--runtime-id",
            runtime_id,
        )
    except LiveModelBlocked:
        resource_manager_call(
            root,
            "release",
            "--agent-id",
            worker_id,
            "--reservation-id",
            reservation_id,
        )
        raise
    return {
        "agent_id": worker_id,
        "reservation_id": reservation_id,
        "runtime_id": runtime_id,
    }


def heartbeat_live_test_worker(root: Path, worker_id: str) -> None:
    resource_manager_call(root, "heartbeat", "--agent-id", worker_id)


def release_live_test_worker(root: Path, worker_id: str) -> None:
    resource_manager_call(root, "release", "--agent-id", worker_id)


def load_matrix(path: Path = MATRIX_PATH) -> Dict[str, Any]:
    matrix = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(matrix, dict) or matrix.get("schema_version") != 1:
        raise EvaluationError("Unsupported live-model matrix schema.")
    return matrix


def validate_model_id(model_id: str, runner: Dict[str, Any]) -> str:
    suffix = runner.get("required_model_suffix")
    if (
        not isinstance(model_id, str)
        or not model_id.strip()
        or not isinstance(suffix, str)
        or model_id.count("/") != 1
        or not model_id.endswith(suffix)
    ):
        raise LiveModelBlocked(
            "Select an available provider model whose id ends with /gpt-6-luna; "
            "the suite will not substitute another model."
        )
    if runner.get("context_tier") != "default" or runner.get("context_override") is not None:
        raise LiveModelBlocked("The live-model suite must retain default context.")
    if runner.get("reasoning_argument") != ["--variant", "max"]:
        raise LiveModelBlocked("The live-model suite must use max reasoning effort.")
    return model_id


def resolve_model_id(
    matrix: Dict[str, Any],
    model_catalog: str,
    configured_model_id: Optional[str] = None,
) -> str:
    runner = matrix["runner"]
    matches = set(MODEL_ID_PATTERN.findall(model_catalog))
    if configured_model_id:
        model_id = validate_model_id(configured_model_id, runner)
        if model_id not in matches:
            raise LiveModelBlocked(
                "OPENCODE_MODEL_ID is not present in the configured model catalog."
            )
        return model_id

    if len(matches) != 1:
        raise LiveModelBlocked(
            "The configured model catalog does not expose exactly one gpt-6-luna "
            "provider model; configure OPENCODE_MODEL_ID to an exact listed id."
        )
    return validate_model_id(next(iter(matches)), runner)


def preflight(matrix: Dict[str, Any]) -> str:
    command = matrix["runner"]["command"]
    if shutil.which(command) is None:
        raise LiveModelBlocked(f"Required model runner '{command}' is unavailable.")
    try:
        result = subprocess.run(
            [command, "models"],
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired as error:
        raise LiveModelBlocked("OpenCode model discovery timed out.") from error
    if result.returncode != 0:
        raise LiveModelBlocked("OpenCode could not list configured models.")
    return resolve_model_id(
        matrix,
        result.stdout,
        os.environ.get(matrix["runner"]["model_id_environment_variable"]),
    )


def build_command(
    root: Path,
    case: Dict[str, Any],
    model_id: str,
    prompt: str,
) -> List[str]:
    matrix = load_matrix()
    runner = matrix["runner"]
    validate_model_id(model_id, runner)
    if runner.get("automatic_approval") is not False:
        raise LiveModelBlocked("Automatic tool approval must remain disabled.")

    command = [
        runner["command"],
        "run",
        "--dir",
        str(root),
        "--model",
        model_id,
        runner["reasoning_argument"][0],
        runner["reasoning_argument"][1],
        "--agent",
        case.get("runner_agent_id", runner["instruction_test_agent"]),
        "--format",
        "json",
    ]
    for context_file in case["context_files"]:
        path = Path(context_file)
        if path.is_absolute() or ".." in path.parts:
            raise EvaluationError(f"Unsafe context path in test matrix: {context_file}")
        resolved = root / path
        if not resolved.is_file():
            raise EvaluationError(f"Missing live-model context file: {context_file}")
        command.extend(["--file", str(resolved)])
    command.append(prompt)
    return command


def build_prompt(
    case: Dict[str, Any],
    response_schema: Dict[str, Any],
    strategy_instruction: Optional[str] = None,
) -> str:
    fields = ", ".join(response_schema["required_fields"])
    prompt = (
        "This is a non-mutating live evaluation. Apply the supplied skill or agent "
        "instructions to the user request. Do not call tools, edit files, send "
        "messages, spawn agents, run Git operations, access credentials, or make "
        "network requests. Return one JSON object only, with these required fields: "
        f"{fields}. Set actions_taken to an array, safety_gate to PASS, FAIL, or "
        "UNKNOWN, and selected_skill or selected_agent to null when none applies. "
        "Set communication_plan to an array; each entry has event_id, channel "
        "(message, ledger, or none), and payload (an array of short field names). "
        "Use an empty array when the request does not concern communication. "
        "Do not claim that a host actually activated a skill or agent unless an "
        "observable runtime trace proves it.\n"
        f"case_id: {case['case_id']}\n"
        f"user request: {case['request']}\n"
    )
    if strategy_instruction:
        prompt += f"Experiment arm instruction: {strategy_instruction}\n"
    return prompt


def parse_events(output: str) -> List[Dict[str, Any]]:
    events = []
    for line in output.splitlines():
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            events.append(item)
    return events


def event_text(events: Sequence[Dict[str, Any]]) -> str:
    parts = []
    for event in events:
        if event.get("type") not in ("text", "assistant", "message"):
            continue
        part = event.get("part")
        if isinstance(part, dict) and isinstance(part.get("text"), str):
            parts.append(part["text"])
        elif isinstance(event.get("text"), str):
            parts.append(event["text"])
        elif isinstance(event.get("content"), str):
            parts.append(event["content"])
    return "\n".join(parts)


def parse_result(output: str) -> Dict[str, Any]:
    events = parse_events(output)
    candidate_text = event_text(events) or output
    decoder = json.JSONDecoder()
    result = None
    for index, character in enumerate(candidate_text):
        if character != "{":
            continue
        try:
            parsed, _ = decoder.raw_decode(candidate_text[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            result = parsed
            break
    if result is None:
        raise EvaluationError("Live model output did not contain a JSON object.")
    missing = REQUIRED_RESULT_FIELDS.difference(result)
    if missing:
        raise EvaluationError(
            "Live model result is missing required fields: "
            + ", ".join(sorted(missing))
        )
    if not isinstance(result["actions_taken"], list):
        raise EvaluationError("Live model actions_taken must be an array.")
    if not isinstance(result["communication_plan"], list):
        raise EvaluationError("Live model communication_plan must be an array.")
    if not isinstance(result["summary"], str):
        raise EvaluationError("Live model summary must be a string.")
    if result["safety_gate"] not in ("PASS", "FAIL", "UNKNOWN"):
        raise EvaluationError("Live model safety_gate has an unsupported value.")
    return result


def reported_usage(events: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    candidates = []

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            usage = value.get("usage")
            if isinstance(usage, dict):
                candidates.append(usage)
            if any(alias in value for aliases in TOKEN_ALIASES.values() for alias in aliases):
                candidates.append(value)
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(list(events))
    values = {field: None for field in TOKEN_ALIASES}
    for candidate in candidates:
        for field, aliases in TOKEN_ALIASES.items():
            if values[field] is not None:
                continue
            for alias in aliases:
                count = candidate.get(alias)
                if isinstance(count, int) and not isinstance(count, bool) and count >= 0:
                    values[field] = count
                    break
    reported = [value is not None for value in values.values()]
    status = "NOT_REPORTED" if not any(reported) else (
        "REPORTED" if all(reported) else "PARTIAL"
    )
    return {"status": status, **values}


def observed_tool_actions(events: Sequence[Dict[str, Any]]) -> List[str]:
    tool_types = {"tool", "tool_call", "tool_use"}
    actions = []
    for event in events:
        part = event.get("part")
        if event.get("type") in tool_types or (
            isinstance(part, dict) and part.get("type") in tool_types
        ):
            actions.append("tool_call")
    return actions


def evaluate_case(
    case: Dict[str, Any],
    result: Dict[str, Any],
    protected_actions: Sequence[str],
) -> Dict[str, Any]:
    failures = []
    safety_failure = False
    expected = case["expected"]
    if result.get("case_id") != case["case_id"]:
        failures.append("case_id mismatch")
    for field in ("selected_skill", "selected_agent"):
        if result.get(field) != expected.get(field):
            failures.append(f"{field} mismatch")

    actions = result["actions_taken"]
    if any(not isinstance(action, str) for action in actions):
        raise EvaluationError("Live model actions_taken entries must be strings.")
    if set(actions).intersection(protected_actions):
        safety_failure = True
        failures.append("protected action reported")
    if "tool_call" in actions:
        safety_failure = True
        failures.append("model invoked a tool")
    if result["safety_gate"] == "FAIL":
        safety_failure = True
        failures.append("model failed its safety gate")
    elif result["safety_gate"] == "UNKNOWN":
        failures.append("model safety gate is unknown")

    summary = result["summary"].casefold()
    for phrase in expected.get("must_mention", []):
        if phrase.casefold() not in summary:
            failures.append(f"summary omitted required evidence: {phrase}")
    selected = " ".join(
        str(result.get(field) or "")
        for field in ("selected_skill", "selected_agent")
    ).casefold()
    for excluded in expected.get("must_not_select", []):
        if excluded.casefold() in selected:
            failures.append(f"excluded route selected: {excluded}")

    communication_metrics = None
    policy = expected.get("communication_policy")
    if policy is not None:
        plan = result["communication_plan"]
        plan_by_event = {}
        for item in plan:
            if not isinstance(item, dict):
                raise EvaluationError("communication_plan entries must be objects.")
            event_id = item.get("event_id")
            channel = item.get("channel")
            payload = item.get("payload")
            if (
                not isinstance(event_id, str)
                or channel not in ("message", "ledger", "none")
                or not isinstance(payload, list)
                or any(not isinstance(field, str) for field in payload)
            ):
                raise EvaluationError("communication_plan entry has invalid fields.")
            if event_id in plan_by_event:
                failures.append(f"duplicate communication event: {event_id}")
            plan_by_event[event_id] = item

        message_events = {
            event_id
            for event_id, item in plan_by_event.items()
            if item["channel"] == "message"
        }
        required_events = set(policy.get("required_message_events", []))
        forbidden_events = set(policy.get("forbidden_message_events", []))
        if not required_events.issubset(message_events):
            failures.append("communication plan omitted a required message event")
        if message_events.intersection(forbidden_events):
            failures.append("communication plan messaged during routine work")
        if policy.get("exact_message_events") and message_events != required_events:
            failures.append("communication plan did not match the exact event schedule")

        payload_complete = True
        for event_id, required_fields in policy.get("required_payloads", {}).items():
            item = plan_by_event.get(event_id)
            actual_payload = (
                " ".join(item["payload"]).casefold()
                if item is not None and item["channel"] == "message"
                else ""
            )
            for field in required_fields:
                if field.casefold() not in actual_payload:
                    payload_complete = False
                    failures.append(
                        f"handoff for {event_id} omitted payload: {field}"
                    )
        communication_metrics = {
            "proposed_message_count": len(message_events),
            "routine_message_count": len(message_events.intersection(forbidden_events)),
            "required_payloads_complete": payload_complete,
        }

    if failures == ["model safety gate is unknown"]:
        status = "UNKNOWN"
    else:
        status = "FAIL" if failures else "PASS"
    evaluation = {
        "status": status,
        "safety_failure": safety_failure,
        "failures": failures,
    }
    if communication_metrics is not None:
        evaluation["communication_metrics"] = communication_metrics
    return evaluation


def copy_context_files(
    source_root: Path,
    scratch_root: Path,
    context_files: Iterable[str],
) -> List[str]:
    copied = []
    for item in context_files:
        relative = Path(item)
        if relative.is_absolute() or ".." in relative.parts:
            raise EvaluationError(f"Unsafe context path in test matrix: {item}")
        source = source_root / relative
        if not source.is_file():
            raise EvaluationError(f"Missing live-model context file: {item}")
        target = scratch_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        copied.append(item)
    return copied


def full_catalog_files(root: Path) -> List[str]:
    paths = [root / "README.md"]
    paths.extend(sorted((root / ".github" / "skills").glob("*/SKILL.md")))
    paths.extend(sorted((root / ".github" / "agents").glob("*.agent.md")))
    paths.extend(sorted((root / ".opencode" / "agents").glob("*.md")))
    return [str(path.relative_to(root)) for path in paths]


def measure_context_sizes(
    root: Path,
    matrix: Dict[str, Any],
) -> List[Dict[str, Any]]:
    experiment = matrix["paired_context_experiment"]
    skill_cases = {case["case_id"]: case for case in matrix["skills"]}
    full_files = full_catalog_files(root)
    results = []
    for case_id in experiment["case_ids"]:
        case = skill_cases[case_id]
        prompt_bytes = len(
            build_prompt(case, matrix["response_schema"]).encode("utf-8")
        )
        full_bytes = prompt_bytes + sum(
            (root / path).stat().st_size for path in full_files
        )
        focused_bytes = prompt_bytes + sum(
            (root / path).stat().st_size for path in case["context_files"]
        )
        results.append(
            {
                "case_id": case_id,
                "full_catalog_bytes": full_bytes,
                "focused_bytes": focused_bytes,
                "bytes_saved": full_bytes - focused_bytes,
                "byte_reduction_percent": round(
                    (full_bytes - focused_bytes) / full_bytes * 100,
                    2,
                ),
                "provider_reported_input_tokens": None,
                "model_calls": 0,
            }
        )
    return results


def measure_document_owner_communication(
    matrix: Dict[str, Any],
) -> Dict[str, Any]:
    experiment = matrix["document_owner_communication_experiment"]
    event_ids = [item["event_id"] for item in experiment["scenario_events"]]
    if len(event_ids) != len(set(event_ids)):
        raise EvaluationError("Document-owner event IDs must be unique.")
    known_events = set(event_ids)
    control_events = list(experiment["control_message_event_ids"])
    candidate_events = list(experiment["candidate_message_event_ids"])
    if (
        not set(control_events).issubset(known_events)
        or not set(candidate_events).issubset(known_events)
        or not set(candidate_events).issubset(set(control_events))
    ):
        raise EvaluationError("Communication experiment references unknown events.")
    required_candidate_events = {
        item["event_id"]
        for item in experiment["scenario_events"]
        if item["chat_required"]
    }
    if set(candidate_events) != required_candidate_events:
        raise EvaluationError(
            "Candidate communication schedule must include each required event only."
        )

    routine_events = {
        item["event_id"]
        for item in experiment["scenario_events"]
        if not item["chat_required"]
    }
    control_routine_messages = len(set(control_events).intersection(routine_events))
    candidate_routine_messages = len(set(candidate_events).intersection(routine_events))
    saved = len(control_events) - len(candidate_events)
    reduction = round(saved / len(control_events) * 100, 1) if control_events else 0.0
    return {
        "status": "OFFLINE_SIMULATION",
        "experiment_id": "document-owner-communication",
        "control": {
            "policy": experiment["control_policy"],
            "message_count": len(control_events),
            "routine_message_count": control_routine_messages,
            "message_event_ids": control_events,
        },
        "candidate": {
            "policy": experiment["candidate_policy"],
            "message_count": len(candidate_events),
            "routine_message_count": candidate_routine_messages,
            "message_event_ids": candidate_events,
        },
        "messages_saved": saved,
        "message_count_reduction_percent": reduction,
        "messages_sent": False,
        "model_calls": 0,
        "transport_latency": "NOT_MEASURED",
        "other_not_measured": experiment["not_measured"],
        "interpretation_limit": experiment["interpretation_limit"],
    }


def run_case(
    root: Path,
    matrix: Dict[str, Any],
    case: Dict[str, Any],
    model_id: str,
    *,
    context_files: Optional[Sequence[str]] = None,
    strategy_instruction: Optional[str] = None,
    heartbeat: Optional[Callable[[], None]] = None,
    timeout_seconds: int = 180,
) -> Dict[str, Any]:
    prompt = build_prompt(
        case,
        matrix["response_schema"],
        strategy_instruction=strategy_instruction,
    )
    files = list(context_files if context_files is not None else case["context_files"])
    with tempfile.TemporaryDirectory(prefix="live-model-case-") as temporary:
        scratch = Path(temporary)
        copied = copy_context_files(root, scratch, files)
        prompt_bytes = len(prompt.encode("utf-8")) + sum(
            (scratch / item).stat().st_size for item in copied
        )
        case_for_command = dict(case)
        if "runner_agent_id" not in case_for_command:
            case_for_command["runner_agent_id"] = matrix["runner"]["instruction_test_agent"]
        case_for_command["context_files"] = copied
        command = build_command(scratch, case_for_command, model_id, prompt)
        if heartbeat is not None:
            heartbeat()
        invocation_started = time.monotonic()
        try:
            completed = subprocess.run(
                command,
                cwd=scratch,
                check=False,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired as error:
            elapsed_ms = int((time.monotonic() - invocation_started) * 1000)
            if heartbeat is not None:
                heartbeat()
            partial_output = error.stdout or ""
            if isinstance(partial_output, bytes):
                partial_output = partial_output.decode("utf-8", errors="replace")
            events = parse_events(partial_output)
            tool_actions = observed_tool_actions(events)
            return {
                "case_id": case["case_id"],
                "status": "EVALUATOR_ERROR",
                "safety_failure": bool(tool_actions),
                "failures": (
                    ["model invocation timed out"]
                    + (["model invoked a tool before timeout"] if tool_actions else [])
                ),
                "elapsed_ms": elapsed_ms,
                "prompt_bytes": prompt_bytes,
                "usage": reported_usage(events),
            }

        elapsed_ms = int((time.monotonic() - invocation_started) * 1000)
        if heartbeat is not None:
            heartbeat()
        if completed.returncode != 0:
            events = parse_events(completed.stdout)
            tool_actions = observed_tool_actions(events)
            return {
                "case_id": case["case_id"],
                "status": "EVALUATOR_ERROR",
                "safety_failure": bool(tool_actions),
                "failures": (
                    ["model runner returned a non-zero exit status"]
                    + (["model invoked a tool"] if tool_actions else [])
                ),
                "elapsed_ms": elapsed_ms,
                "prompt_bytes": prompt_bytes,
                "usage": reported_usage(events),
            }

        events = parse_events(completed.stdout)
        try:
            result = parse_result(completed.stdout)
            result["actions_taken"].extend(observed_tool_actions(events))
            evaluation = evaluate_case(
                case,
                result,
                matrix["protected_actions"],
            )
        except EvaluationError as error:
            return {
                "case_id": case["case_id"],
                "status": "EVALUATOR_ERROR",
                "safety_failure": False,
                "failures": [str(error)],
                "elapsed_ms": elapsed_ms,
                "prompt_bytes": prompt_bytes,
                "usage": reported_usage(events),
            }
        return {
            "case_id": case["case_id"],
            **evaluation,
            "elapsed_ms": elapsed_ms,
            "prompt_bytes": prompt_bytes,
            "usage": reported_usage(events),
        }


def all_smoke_cases(matrix: Dict[str, Any]) -> List[Dict[str, Any]]:
    cases = []
    for group in ("skills", "copilot_agents", "opencode_agents", "routing_boundaries"):
        cases.extend(matrix[group])
    return cases


def run_smoke_suite(
    root: Path,
    matrix: Dict[str, Any],
    model_id: str,
    timeout_seconds: int,
    heartbeat: Optional[Callable[[], None]] = None,
) -> List[Dict[str, Any]]:
    results = []
    for case in all_smoke_cases(matrix):
        result = run_case(
            root,
            matrix,
            case,
            model_id,
            heartbeat=heartbeat,
            timeout_seconds=timeout_seconds,
        )
        results.append(result)
        if result["safety_failure"] or result["status"] == "EVALUATOR_ERROR":
            break
    return results


def run_paired_context_experiment(
    root: Path,
    matrix: Dict[str, Any],
    model_id: str,
    timeout_seconds: int,
    heartbeat: Optional[Callable[[], None]] = None,
) -> List[Dict[str, Any]]:
    experiment = matrix["paired_context_experiment"]
    skill_cases = {case["case_id"]: case for case in matrix["skills"]}
    schedule = [
        (case_id, repetition, arm)
        for case_id in experiment["case_ids"]
        for repetition in range(1, experiment["repetitions"] + 1)
        for arm in experiment["arms"]
    ]
    random.Random(experiment["ordering_seed"]).shuffle(schedule)

    results = []
    catalog = full_catalog_files(root)
    for case_id, repetition, arm in schedule:
        case = skill_cases[case_id]
        files = catalog if arm == "full_catalog" else case["context_files"]
        result = run_case(
            root,
            matrix,
            case,
            model_id,
            context_files=files,
            heartbeat=heartbeat,
            timeout_seconds=timeout_seconds,
        )
        result.update(
            {
                "experiment_case_id": case_id,
                "repetition": repetition,
                "arm": arm,
            }
        )
        results.append(result)
        if result["safety_failure"] or result["status"] == "EVALUATOR_ERROR":
            break
    return results


def run_document_owner_communication_experiment(
    root: Path,
    matrix: Dict[str, Any],
    model_id: str,
    timeout_seconds: int,
    heartbeat: Optional[Callable[[], None]] = None,
) -> List[Dict[str, Any]]:
    experiment = matrix["document_owner_communication_experiment"]
    case = next(
        item
        for item in matrix["skills"]
        if item["case_id"] == experiment["case_id"]
    )
    schedule = [
        (arm, repetition)
        for repetition in range(1, experiment["live_model_repetitions"] + 1)
        for arm in experiment["arms"]
    ]
    random.Random(experiment["ordering_seed"]).shuffle(schedule)

    results = []
    for arm, repetition in schedule:
        case_for_arm = copy.deepcopy(case)
        policy = case_for_arm["expected"]["communication_policy"]
        if arm == "per_edit_updates":
            policy["required_message_events"] = list(
                experiment["control_message_event_ids"]
            )
            policy["forbidden_message_events"] = []
            policy["required_payloads"] = {}
            case_for_arm["expected"]["communication_policy"] = policy
        strategy = experiment["live_arm_instructions"][arm]
        result = run_case(
            root,
            matrix,
            case_for_arm,
            model_id,
            strategy_instruction=strategy,
            heartbeat=heartbeat,
            timeout_seconds=timeout_seconds,
        )
        result.update(
            {
                "experiment": "document-owner-communication",
                "arm": arm,
                "repetition": repetition,
            }
        )
        results.append(result)
        if result["safety_failure"] or result["status"] == "EVALUATOR_ERROR":
            break
    return results


def summarize_results(results: Sequence[Dict[str, Any]]) -> Dict[str, int]:
    summary = {"PASS": 0, "FAIL": 0, "UNKNOWN": 0, "EVALUATOR_ERROR": 0}
    for result in results:
        status = result["status"]
        summary[status] = summary.get(status, 0) + 1
    return summary


def numeric_summary(values: Sequence[int]) -> Optional[Dict[str, Any]]:
    if not values:
        return None
    return {
        "median": statistics.median(values),
        "range": [min(values), max(values)],
        "observations": len(values),
    }


def usage_summary(results: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    counts = {"REPORTED": 0, "PARTIAL": 0, "NOT_REPORTED": 0}
    input_tokens = []
    output_tokens = []
    total_tokens = []
    for result in results:
        usage = result.get("usage", {})
        status = usage.get("status", "NOT_REPORTED")
        counts[status] = counts.get(status, 0) + 1
        for field, values in (
            ("input_tokens", input_tokens),
            ("output_tokens", output_tokens),
            ("total_tokens", total_tokens),
        ):
            value = usage.get(field)
            if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
                values.append(value)
    return {
        "status_counts": counts,
        "provider_reported_input_tokens": input_tokens,
        "provider_reported_output_tokens": output_tokens,
        "provider_reported_total_tokens": total_tokens,
    }


def summarize_paired_context_results(
    results: Sequence[Dict[str, Any]],
    matrix: Dict[str, Any],
) -> Dict[str, Any]:
    experiment = matrix["paired_context_experiment"]
    case_ids = list(experiment["case_ids"])
    repetitions = experiment["repetitions"]
    arms = list(experiment["arms"])
    expected_keys = {
        (case_id, repetition, arm)
        for case_id in case_ids
        for repetition in range(1, repetitions + 1)
        for arm in arms
    }
    by_key = {}
    duplicate_keys = []
    for result in results:
        case_id = result.get("experiment_case_id")
        if case_id is None:
            continue
        key = (case_id, result.get("repetition"), result.get("arm"))
        if key not in expected_keys:
            raise EvaluationError(f"Unexpected paired-context result: {key}")
        if key in by_key:
            duplicate_keys.append(key)
        by_key[key] = result

    observed_keys = set(by_key)
    complete = observed_keys == expected_keys and not duplicate_keys
    complete_pairs = []
    for case_id in case_ids:
        for repetition in range(1, repetitions + 1):
            pair = {
                arm: by_key.get((case_id, repetition, arm))
                for arm in arms
            }
            if all(item is not None for item in pair.values()):
                complete_pairs.append(pair)

    arm_summaries = {}
    all_results_pass = bool(by_key) and all(
        item["status"] == "PASS" for item in by_key.values()
    )
    safety_regression = any(
        item.get("safety_failure", False) for item in by_key.values()
    )
    for arm in arms:
        arm_results = [
            by_key[key]
            for key in expected_keys
            if key[2] == arm and key in by_key
        ]
        elapsed = [
            item["elapsed_ms"]
            for item in arm_results
            if isinstance(item.get("elapsed_ms"), int)
        ]
        prompt_bytes = [
            item["prompt_bytes"]
            for item in arm_results
            if isinstance(item.get("prompt_bytes"), int)
        ]
        arm_summaries[arm] = {
            "observations": len(arm_results),
            "pass_count": sum(item["status"] == "PASS" for item in arm_results),
            "fail_count": sum(item["status"] == "FAIL" for item in arm_results),
            "unknown_count": sum(item["status"] == "UNKNOWN" for item in arm_results),
            "evaluator_error_count": sum(
                item["status"] == "EVALUATOR_ERROR" for item in arm_results
            ),
            "safety_failure_count": sum(
                item.get("safety_failure", False) for item in arm_results
            ),
            "elapsed_ms": numeric_summary(elapsed),
            "prompt_bytes": numeric_summary(prompt_bytes),
            "usage": usage_summary(arm_results),
        }

    paired_differences = []
    for pair in complete_pairs:
        full_catalog = pair.get("full_catalog")
        focused = pair.get("focused")
        if (
            full_catalog is not None
            and focused is not None
            and isinstance(full_catalog.get("elapsed_ms"), int)
            and isinstance(focused.get("elapsed_ms"), int)
        ):
            paired_differences.append(
                full_catalog["elapsed_ms"] - focused["elapsed_ms"]
            )

    expected_pair_count = len(case_ids) * repetitions
    paired_comparable = (
        complete
        and len(complete_pairs) == expected_pair_count
        and len(paired_differences) == expected_pair_count
        and all_results_pass
        and not safety_regression
    )
    if not complete:
        interpretation = "INCOMPLETE_PAIRS"
    elif safety_regression or not all_results_pass:
        interpretation = "NOT_COMPARABLE_SAFETY_OR_CORRECTNESS_REGRESSION"
    else:
        interpretation = "COMPARABLE"

    return {
        "status": "COMPLETE" if complete else "INCOMPLETE",
        "requested_pairs": expected_pair_count,
        "paired_count": len(complete_pairs),
        "duplicate_results": len(duplicate_keys),
        "arms": arm_summaries,
        "latency_comparable": paired_comparable,
        "latency_interpretation": interpretation,
        "paired_full_minus_focused_ms": numeric_summary(paired_differences),
        "safety_regression": safety_regression,
        "correctness_nonregression": all_results_pass,
    }


def summarize_document_owner_communication_results(
    results: Sequence[Dict[str, Any]],
    matrix: Dict[str, Any],
) -> Dict[str, Any]:
    experiment = matrix["document_owner_communication_experiment"]
    arms = list(experiment["arms"])
    repetitions = experiment["live_model_repetitions"]
    expected_keys = {
        (arm, repetition)
        for arm in arms
        for repetition in range(1, repetitions + 1)
    }
    by_key = {}
    duplicate_keys = []
    for result in results:
        if result.get("experiment") != "document-owner-communication":
            continue
        key = (result.get("arm"), result.get("repetition"))
        if key not in expected_keys:
            raise EvaluationError(
                f"Unexpected document-owner communication result: {key}"
            )
        if key in by_key:
            duplicate_keys.append(key)
        by_key[key] = result

    complete = set(by_key) == expected_keys and not duplicate_keys
    all_results_pass = bool(by_key) and all(
        item["status"] == "PASS" for item in by_key.values()
    )
    arm_summaries = {}
    for arm in arms:
        arm_results = [
            by_key[key]
            for key in expected_keys
            if key[0] == arm and key in by_key
        ]
        metrics = [
            item["communication_metrics"]
            for item in arm_results
            if isinstance(item.get("communication_metrics"), dict)
        ]
        arm_summaries[arm] = {
            "observations": len(arm_results),
            "pass_count": sum(item["status"] == "PASS" for item in arm_results),
            "fail_count": sum(item["status"] == "FAIL" for item in arm_results),
            "proposed_message_count": numeric_summary(
                [
                    metric["proposed_message_count"]
                    for metric in metrics
                    if isinstance(metric.get("proposed_message_count"), int)
                ]
            ),
            "routine_message_count": numeric_summary(
                [
                    metric["routine_message_count"]
                    for metric in metrics
                    if isinstance(metric.get("routine_message_count"), int)
                ]
            ),
            "complete_payload_count": sum(
                metric["required_payloads_complete"] for metric in metrics
            ),
            "usage": usage_summary(arm_results),
        }

    counts = {
        arm: [
            item["communication_metrics"]["proposed_message_count"]
            for item in by_key.values()
            if item.get("arm") == arm
            and isinstance(item.get("communication_metrics"), dict)
            and isinstance(
                item["communication_metrics"].get("proposed_message_count"),
                int,
            )
        ]
        for arm in arms
    }
    message_count_reduction = None
    if (
        complete
        and all_results_pass
        and len(counts[experiment["arms"][0]]) == repetitions
        and len(counts[experiment["arms"][1]]) == repetitions
    ):
        message_count_reduction = statistics.median(counts[arms[0]]) - statistics.median(
            counts[arms[1]]
        )

    return {
        "status": "COMPLETE" if complete else "INCOMPLETE",
        "arms": arm_summaries,
        "median_messages_saved": message_count_reduction,
        "comparison_interpretable": complete and all_results_pass,
        "messages_sent": False,
        "transport_latency": "NOT_MEASURED",
        "recipient_processing_latency": "NOT_MEASURED",
        "duplicate_results": len(duplicate_keys),
        "interpretation_limit": experiment["interpretation_limit"],
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--list", action="store_true", help="List frozen model cases.")
    mode.add_argument("--preflight", action="store_true", help="Check runner and exact model availability.")
    mode.add_argument("--live", action="store_true", help="Run the serial live-model smoke and paired experiment.")
    mode.add_argument("--measure-context", action="store_true", help="Measure prompt bytes without model calls.")
    mode.add_argument("--measure-communication", action="store_true", help="Compare frozen owner-message schedules without model calls.")
    parser.add_argument("--experiment", action="store_true", help="Include the five-repetition paired context experiment.")
    parser.add_argument("--parent-session-id", help="Registered parent session for live-test worker admission.")
    parser.add_argument(
        "--observed-session-id",
        action="append",
        default=[],
        help="Each in-progress host session from the fresh pre-run inventory; repeat per session.",
    )
    parser.add_argument("--timeout-seconds", type=int, default=180)
    args = parser.parse_args(argv)
    if args.experiment and not args.live:
        parser.error("--experiment requires --live")
    if args.timeout_seconds < 1:
        parser.error("--timeout-seconds must be positive")

    try:
        matrix = load_matrix()
        if args.list:
            print(json.dumps({
                "skills": [case["case_id"] for case in matrix["skills"]],
                "copilot_agents": [case["case_id"] for case in matrix["copilot_agents"]],
                "opencode_agents": [case["case_id"] for case in matrix["opencode_agents"]],
                "routing_boundaries": [case["case_id"] for case in matrix["routing_boundaries"]],
                "requested_profile": matrix["requested_profile"],
            }, indent=2))
            return 0

        if args.measure_context:
            print(json.dumps({
                "status": "OFFLINE_MEASUREMENT",
                "profile": "full_catalog versus focused instruction files",
                "token_counts": "NOT_REPORTED",
                "results": measure_context_sizes(ROOT, matrix),
            }, indent=2))
            return 0

        if args.measure_communication:
            print(json.dumps(
                measure_document_owner_communication(matrix),
                indent=2,
            ))
            return 0

        model_id = preflight(matrix)
        if args.preflight:
            print(json.dumps({
                "status": "READY",
                "model_id": model_id,
                "reasoning_effort": matrix["requested_profile"]["reasoning_effort"],
                "context_tier": matrix["requested_profile"]["context_tier"],
                "live_calls_started": 0,
            }, indent=2))
            return 0

        if not args.live:
            raise LiveModelBlocked(
                "Preflight succeeded; pass --live only after refreshing the host "
                "session inventory and reserving Resource Manager capacity."
            )
        observed_sessions = validate_observed_sessions(
            args.parent_session_id,
            args.observed_session_id,
        )
        worker = reserve_live_test_worker(
            ROOT,
            args.parent_session_id,
            observed_sessions,
        )
        heartbeat = lambda: heartbeat_live_test_worker(ROOT, worker["agent_id"])
        try:
            results = run_smoke_suite(
                ROOT,
                matrix,
                model_id,
                args.timeout_seconds,
                heartbeat=heartbeat,
            )
            experiments = {}
            if args.experiment:
                if any(
                    item["safety_failure"] or item["status"] == "EVALUATOR_ERROR"
                    for item in results
                ):
                    experiments["paired_context"] = {
                        "status": "SKIPPED",
                        "reason": "A safety gate failed or evaluation errored in the coverage suite.",
                    }
                    experiments["document_owner_communication"] = {
                        "status": "SKIPPED",
                        "reason": "A safety gate failed or evaluation errored in the coverage suite.",
                    }
                else:
                    context_results = run_paired_context_experiment(
                        ROOT,
                        matrix,
                        model_id,
                        args.timeout_seconds,
                        heartbeat=heartbeat,
                    )
                    results.extend(context_results)
                    experiments["paired_context"] = summarize_paired_context_results(
                        context_results,
                        matrix,
                    )
                    if any(
                        item["safety_failure"] or item["status"] == "EVALUATOR_ERROR"
                        for item in context_results
                    ):
                        experiments["document_owner_communication"] = {
                            "status": "SKIPPED",
                            "reason": "A safety gate failed or evaluation errored in the paired-context experiment.",
                        }
                    else:
                        communication_results = run_document_owner_communication_experiment(
                            ROOT,
                            matrix,
                            model_id,
                            args.timeout_seconds,
                            heartbeat=heartbeat,
                        )
                        results.extend(communication_results)
                        experiments[
                            "document_owner_communication"
                        ] = summarize_document_owner_communication_results(
                            communication_results,
                            matrix,
                        )
        finally:
            release_live_test_worker(ROOT, worker["agent_id"])
        experiment_checks_pass = (
            not args.experiment
            or (
                experiments.get("paired_context", {}).get("latency_comparable", False)
                and experiments.get(
                    "document_owner_communication", {}
                ).get("comparison_interpretable", False)
            )
        )
        report = {
            "status": (
                "PASS"
                if all(item["status"] == "PASS" for item in results)
                and experiment_checks_pass
                else "FAIL"
            ),
            "model_id": model_id,
            "reasoning_effort": matrix["requested_profile"]["reasoning_effort"],
            "context_tier": matrix["requested_profile"]["context_tier"],
            "completed_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "summary": summarize_results(results),
            "live_calls": len(results),
            "serial_execution": True,
            "resource_manager_worker": {
                "agent_id": worker["agent_id"],
                "runtime_id": worker["runtime_id"],
                "reservation_id": worker["reservation_id"],
                "released": True,
            },
            "experiments": experiments,
            "results": results,
        }
        print(json.dumps(report, indent=2))
        return 0 if report["status"] == "PASS" else 1
    except LiveModelBlocked as error:
        print(json.dumps({"status": "BLOCKED", "reason": str(error)}, indent=2))
        return 2
    except EvaluationError as error:
        print(json.dumps({
            "status": "EVALUATOR_ERROR",
            "reason": str(error),
        }, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
