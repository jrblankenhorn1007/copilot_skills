"""Unit tests for the opt-in live-model case runner."""

import importlib.util
import io
import json
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
TESTS = ROOT / ".github" / "skills" / "agentic-eval" / "tests"
RUNNER = TESTS / "run_live_model_cases.py"
MATRIX = TESTS / "live_model_cases.json"


class LiveModelRunnerTests(unittest.TestCase):
    def load_runner(self):
        self.assertTrue(RUNNER.is_file(), "Missing opt-in live-model runner.")
        spec = importlib.util.spec_from_file_location("live_model_case_runner", RUNNER)
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_command_pins_model_and_max_effort_without_context_override(self):
        runner = self.load_runner()
        matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        case = matrix["skills"][0]
        model_id = "openai/gpt-6-luna"
        command = runner.build_command(ROOT, case, model_id, "safe test prompt")

        self.assertEqual(command[command.index("--model") + 1], model_id)
        self.assertEqual(command[command.index("--variant") + 1], "max")
        self.assertEqual(command[command.index("--agent") + 1], "plan")
        self.assertNotIn("--context", command)
        self.assertNotIn("--auto", command)
        file_arguments = [
            command[index + 1]
            for index, argument in enumerate(command[:-1])
            if argument == "--file"
        ]
        self.assertTrue(file_arguments)
        self.assertTrue(all(argument.startswith(str(ROOT)) for argument in file_arguments))

    def test_opencode_role_invocation_selects_the_named_profile(self):
        runner = self.load_runner()
        matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        case = next(
            item
            for item in matrix["opencode_agents"]
            if item["agent_id"] == "ralph-loop-worker"
        )

        command = runner.build_command(
            ROOT,
            case,
            "openai/gpt-6-luna",
            "safe test prompt",
        )

        self.assertEqual(command[command.index("--agent") + 1], "ralph-loop-worker")

    def test_model_id_must_match_the_requested_luna_model(self):
        runner = self.load_runner()
        matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        with self.assertRaises(runner.LiveModelBlocked):
            runner.validate_model_id("openai/gpt-6-astra", matrix["runner"])
        self.assertEqual(
            runner.validate_model_id("openai/gpt-6-luna", matrix["runner"]),
            "openai/gpt-6-luna",
        )

    def test_live_admission_requires_parent_in_fresh_observed_inventory(self):
        runner = self.load_runner()

        with self.assertRaises(runner.LiveModelBlocked):
            runner.validate_observed_sessions("copilotcli:/parent", [])
        with self.assertRaises(runner.LiveModelBlocked):
            runner.validate_observed_sessions(
                "copilotcli:/parent",
                ["copilotcli:/other"],
            )
        self.assertEqual(
            runner.validate_observed_sessions(
                "copilotcli:/parent",
                ["copilotcli:/parent", "copilotcli:/other"],
            ),
            ["copilotcli:/parent", "copilotcli:/other"],
        )

    def test_live_suite_stops_after_an_evaluator_error(self):
        runner = self.load_runner()
        matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        error_result = {
            "case_id": "skill-acquire-codebase-knowledge",
            "status": "EVALUATOR_ERROR",
            "safety_failure": False,
            "failures": ["model session timed out"],
        }
        with patch.object(runner, "run_case", return_value=error_result) as run_case:
            results = runner.run_smoke_suite(
                ROOT,
                matrix,
                "openai/gpt-6-luna",
                30,
            )

        self.assertEqual(len(results), 1)
        run_case.assert_called_once()

    def test_resource_manager_denial_prevents_every_live_model_call(self):
        runner = self.load_runner()
        output = io.StringIO()
        with patch.object(
            runner,
            "preflight",
            return_value="openai/gpt-6-luna",
        ):
            with patch.object(
                runner,
                "reserve_live_test_worker",
                side_effect=runner.LiveModelBlocked("capacity is 0"),
            ):
                with patch.object(runner, "run_smoke_suite") as run_smoke:
                    with redirect_stdout(output):
                        exit_code = runner.main([
                            "--live",
                            "--parent-session-id",
                            "copilotcli:/parent",
                            "--observed-session-id",
                            "copilotcli:/parent",
                        ])

        self.assertEqual(exit_code, 2)
        run_smoke.assert_not_called()
        self.assertIn('"status": "BLOCKED"', output.getvalue())

    def test_json_event_stream_produces_a_structured_result(self):
        runner = self.load_runner()
        output = (
            '{"type":"text","part":{"type":"text","text":'
            '"{\\"case_id\\":\\"skill-docs-sync-audit\\",'
            '\\"selected_skill\\":\\"docs-sync-audit\\",'
            '\\"selected_agent\\":\\"Ralph Docs Specialist\\",'
            '\\"actions_taken\\":[],\\"communication_plan\\":[],'
            '\\"summary\\":\\"Flag --legacy against --format\\",'
            '\\"safety_gate\\":\\"PASS\\"}"}}\n'
        )

        result = runner.parse_result(output)

        self.assertEqual(result["case_id"], "skill-docs-sync-audit")
        self.assertEqual(result["selected_skill"], "docs-sync-audit")
        self.assertEqual(result["actions_taken"], [])

    def test_result_evaluation_fails_on_wrong_route_or_protected_action(self):
        runner = self.load_runner()
        matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        case = next(
            item for item in matrix["skills"]
            if item["case_id"] == "skill-docs-sync-audit"
        )
        result = {
            "case_id": case["case_id"],
            "selected_skill": "agent-skill-stack",
            "selected_agent": "Ralph Docs Specialist",
            "actions_taken": ["file_write"],
            "communication_plan": [],
            "summary": "This result does not follow the expected route.",
            "safety_gate": "FAIL",
        }

        evaluation = runner.evaluate_case(case, result, matrix["protected_actions"])

        self.assertEqual(evaluation["status"], "FAIL")
        self.assertTrue(evaluation["safety_failure"])

    def test_missing_provider_usage_is_not_estimated(self):
        runner = self.load_runner()

        usage = runner.reported_usage([])

        self.assertEqual(usage["status"], "NOT_REPORTED")
        self.assertIsNone(usage["input_tokens"])
        self.assertIsNone(usage["output_tokens"])
        self.assertIsNone(usage["total_tokens"])

    def test_reported_usage_does_not_infer_total_tokens(self):
        runner = self.load_runner()

        usage = runner.reported_usage(
            [{"usage": {"input_tokens": 120, "output_tokens": 30}}]
        )

        self.assertEqual(usage["status"], "PARTIAL")
        self.assertEqual(usage["input_tokens"], 120)
        self.assertEqual(usage["output_tokens"], 30)
        self.assertIsNone(usage["total_tokens"])

    def test_unknown_safety_evidence_remains_unknown(self):
        runner = self.load_runner()
        matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        case = matrix["skills"][0]
        result = {
            "case_id": case["case_id"],
            "selected_skill": case["expected"]["selected_skill"],
            "selected_agent": case["expected"]["selected_agent"],
            "actions_taken": [],
            "communication_plan": [],
            "summary": "This summary contains " + ", ".join(case["expected"]["must_mention"]),
            "safety_gate": "UNKNOWN",
        }

        evaluation = runner.evaluate_case(case, result, matrix["protected_actions"])

        self.assertEqual(evaluation["status"], "UNKNOWN")
        self.assertFalse(evaluation["safety_failure"])

    def test_model_catalog_never_falls_back_to_another_model(self):
        runner = self.load_runner()
        matrix = json.loads(MATRIX.read_text(encoding="utf-8"))

        self.assertEqual(
            runner.resolve_model_id(
                matrix,
                "openai/gpt-6-luna\n",
            ),
            "openai/gpt-6-luna",
        )
        with self.assertRaises(runner.LiveModelBlocked):
            runner.resolve_model_id(
                matrix,
                "openai/gpt-6-astra\n",
                "openai/gpt-6-astra",
            )
        with self.assertRaises(runner.LiveModelBlocked):
            runner.resolve_model_id(
                matrix,
                "openai/gpt-6-luna",
                "provider/openai/gpt-6-luna",
            )
        with self.assertRaises(runner.LiveModelBlocked):
            runner.resolve_model_id(
                matrix,
                "provider/openai/gpt-6-luna",
            )
        with self.assertRaises(runner.LiveModelBlocked):
            runner.resolve_model_id(matrix, "")

    def test_full_catalog_arm_covers_every_skill_and_agent_definition(self):
        runner = self.load_runner()
        catalog = set(runner.full_catalog_files(ROOT))
        expected = {"README.md"}
        expected.update(
            str(path.relative_to(ROOT))
            for path in (ROOT / ".github" / "skills").glob("*/SKILL.md")
        )
        expected.update(
            str(path.relative_to(ROOT))
            for path in (ROOT / ".github" / "agents").glob("*.agent.md")
        )
        expected.update(
            str(path.relative_to(ROOT))
            for path in (ROOT / ".opencode" / "agents").glob("*.md")
        )

        self.assertEqual(catalog, expected)

    def test_offline_context_experiment_reports_bytes_without_token_estimates(self):
        runner = self.load_runner()
        matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        self.assertTrue(
            hasattr(runner, "measure_context_sizes"),
            "Missing deterministic focused-versus-catalog measurement.",
        )

        results = runner.measure_context_sizes(ROOT, matrix)

        self.assertEqual(
            {item["case_id"] for item in results},
            set(matrix["paired_context_experiment"]["case_ids"]),
        )
        for item in results:
            with self.subTest(case=item["case_id"]):
                self.assertGreater(item["full_catalog_bytes"], item["focused_bytes"])
                self.assertGreater(item["bytes_saved"], 0)
                self.assertIsNone(item["provider_reported_input_tokens"])
                self.assertEqual(item["model_calls"], 0)

    def test_document_owner_simulation_reduces_chatter_without_latency_claims(self):
        runner = self.load_runner()
        matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        self.assertTrue(
            hasattr(runner, "measure_document_owner_communication"),
            "Missing frozen document-owner communication comparison.",
        )

        result = runner.measure_document_owner_communication(matrix)

        self.assertEqual(result["status"], "OFFLINE_SIMULATION")
        self.assertEqual(result["control"]["message_count"], 7)
        self.assertEqual(result["candidate"]["message_count"], 4)
        self.assertEqual(result["messages_saved"], 3)
        self.assertEqual(result["message_count_reduction_percent"], 42.9)
        self.assertEqual(result["model_calls"], 0)
        self.assertEqual(result["transport_latency"], "NOT_MEASURED")
        self.assertFalse(result["messages_sent"])

    def test_communication_policy_checks_message_timing_and_handoff_payload(self):
        runner = self.load_runner()
        matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        case = next(
            case for case in matrix["skills"]
            if case["skill_id"] == "agent-communication"
        )
        policy = case["expected"]["communication_policy"]
        result = {
            "case_id": case["case_id"],
            "selected_skill": case["expected"]["selected_skill"],
            "selected_agent": case["expected"]["selected_agent"],
            "actions_taken": [],
            "communication_plan": [
                {
                    "event_id": event_id,
                    "channel": "message",
                    "payload": policy["required_payloads"].get(event_id, []),
                }
                for event_id in policy["required_message_events"]
            ],
            "summary": "This response includes " + ", ".join(
                case["expected"]["must_mention"]
            ),
            "safety_gate": "PASS",
        }

        evaluation = runner.evaluate_case(case, result, matrix["protected_actions"])

        self.assertEqual(evaluation["status"], "PASS")
        self.assertEqual(
            evaluation["communication_metrics"]["proposed_message_count"],
            4,
        )
        self.assertEqual(
            evaluation["communication_metrics"]["routine_message_count"],
            0,
        )
        self.assertTrue(
            evaluation["communication_metrics"]["required_payloads_complete"]
        )

    def test_communication_policy_rejects_chatter_and_missing_handoff_fields(self):
        runner = self.load_runner()
        matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        case = next(
            case for case in matrix["skills"]
            if case["skill_id"] == "agent-communication"
        )
        result = {
            "case_id": case["case_id"],
            "selected_skill": case["expected"]["selected_skill"],
            "selected_agent": case["expected"]["selected_agent"],
            "actions_taken": [],
            "communication_plan": [
                {
                    "event_id": "routine_heading_edit",
                    "channel": "message",
                    "payload": [],
                },
                {
                    "event_id": "scope_collision",
                    "channel": "message",
                    "payload": ["document path"],
                },
                {
                    "event_id": "review_ready_handoff",
                    "channel": "message",
                    "payload": ["document paths"],
                },
                {
                    "event_id": "verified_completion_to_waiting_owner",
                    "channel": "message",
                    "payload": ["merge SHA"],
                },
            ],
            "summary": "This response includes " + ", ".join(
                case["expected"]["must_mention"]
            ),
            "safety_gate": "PASS",
        }

        evaluation = runner.evaluate_case(case, result, matrix["protected_actions"])

        self.assertEqual(evaluation["status"], "FAIL")
        self.assertIn(
            "communication plan messaged during routine work",
            evaluation["failures"],
        )
        self.assertFalse(
            evaluation["communication_metrics"]["required_payloads_complete"]
        )

    def test_paired_context_summary_requires_five_valid_pairs_for_latency_claim(self):
        runner = self.load_runner()
        matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        self.assertTrue(
            hasattr(runner, "summarize_paired_context_results"),
            "Missing paired latency and correctness summary.",
        )
        results = []
        for case_id in matrix["paired_context_experiment"]["case_ids"]:
            for repetition in range(1, 6):
                for arm, elapsed in (("focused", 100), ("full_catalog", 140)):
                    results.append({
                        "case_id": case_id,
                        "experiment_case_id": case_id,
                        "repetition": repetition,
                        "arm": arm,
                        "status": "PASS",
                        "safety_failure": False,
                        "elapsed_ms": elapsed,
                        "prompt_bytes": 1000 if arm == "focused" else 2000,
                        "usage": {
                            "status": "NOT_REPORTED",
                            "input_tokens": None,
                            "output_tokens": None,
                            "total_tokens": None,
                        },
                    })

        summary = runner.summarize_paired_context_results(results, matrix)
        self.assertEqual(summary["status"], "COMPLETE")
        self.assertTrue(summary["latency_comparable"])
        self.assertEqual(summary["paired_count"], 15)
        self.assertEqual(
            summary["arms"]["focused"]["elapsed_ms"]["median"],
            100,
        )
        self.assertEqual(
            summary["arms"]["full_catalog"]["elapsed_ms"]["range"],
            [140, 140],
        )
        self.assertEqual(summary["paired_full_minus_focused_ms"]["median"], 40)
        self.assertEqual(
            summary["paired_full_minus_focused_ms"]["range"],
            [40, 40],
        )

        incomplete = runner.summarize_paired_context_results(results[:-1], matrix)
        self.assertEqual(incomplete["status"], "INCOMPLETE")
        self.assertFalse(incomplete["latency_comparable"])

    def test_safety_regression_makes_context_latency_incomparable(self):
        runner = self.load_runner()
        matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        results = []
        for case_id in matrix["paired_context_experiment"]["case_ids"]:
            for repetition in range(1, 6):
                for arm in ("focused", "full_catalog"):
                    safety_failure = (
                        case_id == matrix["paired_context_experiment"]["case_ids"][0]
                        and repetition == 1
                        and arm == "focused"
                    )
                    results.append({
                        "case_id": case_id,
                        "experiment_case_id": case_id,
                        "repetition": repetition,
                        "arm": arm,
                        "status": "FAIL" if safety_failure else "PASS",
                        "safety_failure": safety_failure,
                        "elapsed_ms": 100,
                        "prompt_bytes": 1000,
                        "usage": {"status": "NOT_REPORTED"},
                    })

        summary = runner.summarize_paired_context_results(results, matrix)

        self.assertFalse(summary["latency_comparable"])
        self.assertEqual(
            summary["latency_interpretation"],
            "NOT_COMPARABLE_SAFETY_OR_CORRECTNESS_REGRESSION",
        )

    def test_document_owner_summary_requires_complete_correct_repetitions(self):
        runner = self.load_runner()
        matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        self.assertTrue(
            hasattr(runner, "summarize_document_owner_communication_results"),
            "Missing repeated owner-communication experiment summary.",
        )
        results = []
        for repetition in range(1, 6):
            for arm, message_count, routine_count in (
                ("per_edit_updates", 7, 3),
                ("event_triggered_checkpoints", 4, 0),
            ):
                results.append({
                    "experiment": "document-owner-communication",
                    "arm": arm,
                    "repetition": repetition,
                    "status": "PASS",
                    "usage": {"status": "NOT_REPORTED"},
                    "communication_metrics": {
                        "proposed_message_count": message_count,
                        "routine_message_count": routine_count,
                        "required_payloads_complete": True,
                    },
                })

        summary = runner.summarize_document_owner_communication_results(
            results,
            matrix,
        )

        self.assertEqual(summary["status"], "COMPLETE")
        self.assertTrue(summary["comparison_interpretable"])
        self.assertEqual(summary["median_messages_saved"], 3)
        self.assertEqual(summary["arms"]["per_edit_updates"]["routine_message_count"]["median"], 3)
        self.assertEqual(summary["transport_latency"], "NOT_MEASURED")
        self.assertFalse(summary["messages_sent"])

        incomplete = runner.summarize_document_owner_communication_results(
            results[:-1],
            matrix,
        )
        self.assertEqual(incomplete["status"], "INCOMPLETE")
        self.assertIsNone(incomplete["median_messages_saved"])

    def test_prompt_does_not_inject_the_expected_answer(self):
        runner = self.load_runner()
        matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        case = matrix["skills"][0]

        prompt = runner.build_prompt(case, matrix["response_schema"])

        self.assertIn(case["request"], prompt)
        self.assertNotIn(json.dumps(case["expected"], sort_keys=True), prompt)


if __name__ == "__main__":
    unittest.main()
