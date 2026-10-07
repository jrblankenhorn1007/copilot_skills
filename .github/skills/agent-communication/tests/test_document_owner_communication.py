"""Contract checks for fast, auditable document-owner communication."""

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SKILL = ROOT / ".github" / "skills" / "agent-communication" / "SKILL.md"
MATRIX = (
    ROOT
    / ".github"
    / "skills"
    / "agentic-eval"
    / "tests"
    / "live_model_cases.json"
)


class DocumentOwnerCommunicationTests(unittest.TestCase):
    def test_ownership_updates_are_event_triggered_and_artifact_first(self):
        content = " ".join(SKILL.read_text(encoding="utf-8").casefold().split())
        for phrase in (
            "document-owner communication",
            "routine edits",
            "scope collision",
            "blocker",
            "review-ready handoff",
            "verified completion",
            "status.md",
            "progress.md",
            "commit sha",
            "next action",
        ):
            with self.subTest(phrase=phrase):
                self.assertTrue(
                    phrase in content,
                    f"Missing document-owner communication rule: {phrase}",
                )

    def test_live_matrix_exercises_timing_and_handoff_payload(self):
        matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        case = next(
            case
            for case in matrix["skills"]
            if case["skill_id"] == "agent-communication"
        )
        self.assertTrue(
            "document_owner_communication_experiment" in matrix,
            "Missing document-owner communication experiment.",
        )
        experiment = matrix["document_owner_communication_experiment"]
        communication_policy = case["expected"]["communication_policy"]

        self.assertEqual(
            set(experiment["arms"]),
            {"per_edit_updates", "event_triggered_checkpoints"},
        )
        self.assertEqual(experiment["case_id"], case["case_id"])
        self.assertEqual(experiment["repetitions"], 5)
        self.assertIn("transport_latency", experiment["not_measured"])
        self.assertIn(
            "blocking_dependency",
            communication_policy["required_message_events"],
        )
        required_payloads = communication_policy["required_payloads"]
        expected_payloads = {
            "scope_collision": {
                "document path",
                "both owners",
                "branch or base SHA",
                "conflict",
                "decision needed",
            },
            "blocking_dependency": {
                "document path",
                "blocking dependency",
                "impact",
                "safe check tried",
                "decision needed",
                "reply deadline",
                "next action",
            },
            "review_ready_handoff": {
                "document paths",
                "full commit SHA",
                "checks and results",
                "unresolved blockers",
                "next owner and action",
            },
            "verified_completion_to_waiting_owner": {
                "verified remote ref",
                "merge SHA",
                "next action",
            },
        }
        for event_id, payload_fields in expected_payloads.items():
            with self.subTest(event_id=event_id):
                self.assertEqual(set(required_payloads[event_id]), payload_fields)
        self.assertIn("routine edits", case["request"].casefold())
        for field in (
            "task sign-in",
            "scope collision",
            "blocking dependency",
            "review-ready handoff",
            "commit SHA",
            "checks",
            "next action",
            "reply deadline",
        ):
            with self.subTest(field=field):
                self.assertIn(
                    field.casefold(),
                    " ".join(case["expected"]["must_mention"]).casefold(),
                )


if __name__ == "__main__":
    unittest.main()
