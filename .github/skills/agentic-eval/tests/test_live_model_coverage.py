"""Coverage contract for the repository's live-model evaluation matrix."""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
MATRIX = ROOT / ".github" / "skills" / "agentic-eval" / "tests" / "live_model_cases.json"


def skill_ids():
    return {
        path.parent.name
        for path in (ROOT / ".github" / "skills").glob("*/SKILL.md")
    }


def copilot_agent_ids():
    ids = set()
    for path in (ROOT / ".github" / "agents").glob("*.agent.md"):
        content = path.read_text(encoding="utf-8")
        metadata = content.split("---\n", 2)[1]
        match = re.search(r"(?m)^name: (.+)$", metadata)
        if match is None:
            raise AssertionError(f"Missing agent name in {path}")
        ids.add(path.name.removesuffix(".agent.md"))
    return ids


def opencode_agent_ids():
    return {
        path.stem
        for path in (ROOT / ".opencode" / "agents").glob("*.md")
    }


class LiveModelCoverageTests(unittest.TestCase):
    def load_matrix(self):
        self.assertTrue(
            MATRIX.is_file(),
            "Every current skill and agent needs a frozen live-model case matrix.",
        )
        return json.loads(MATRIX.read_text(encoding="utf-8"))

    def test_every_skill_has_a_live_model_case(self):
        matrix = self.load_matrix()
        covered = {case["skill_id"] for case in matrix["skills"]}
        self.assertEqual(skill_ids(), covered)

    def test_every_copilot_and_opencode_agent_has_a_live_model_case(self):
        matrix = self.load_matrix()
        covered_copilot = {
            case["agent_id"] for case in matrix["copilot_agents"]
        }
        covered_opencode = {
            case["agent_id"] for case in matrix["opencode_agents"]
        }
        self.assertEqual(copilot_agent_ids(), covered_copilot)
        self.assertEqual(opencode_agent_ids(), covered_opencode)

    def test_opencode_role_cases_invoke_the_profile_under_test(self):
        matrix = self.load_matrix()
        for case in matrix["opencode_agents"]:
            with self.subTest(agent=case["agent_id"]):
                self.assertEqual(case["runner_agent_id"], case["agent_id"])

    def test_instruction_cases_include_the_target_definition(self):
        matrix = self.load_matrix()
        for case in matrix["skills"]:
            with self.subTest(skill=case["skill_id"]):
                self.assertIn(case["skill_path"], case["context_files"])
        for group in ("copilot_agents", "opencode_agents"):
            for case in matrix[group]:
                with self.subTest(group=group, agent=case["agent_id"]):
                    self.assertIn(case["agent_path"], case["context_files"])

    def test_all_live_cases_use_the_requested_model_profile(self):
        matrix = self.load_matrix()
        self.assertEqual(
            matrix["requested_profile"],
            {
                "model_id": "gpt-6-luna",
                "reasoning_effort": "max",
                "context_tier": "default",
            },
        )
        for group in (
            "skills",
            "copilot_agents",
            "opencode_agents",
            "routing_boundaries",
        ):
            for case in matrix[group]:
                with self.subTest(group=group, case=case["case_id"]):
                    self.assertNotIn("model_id", case)
                    self.assertNotIn("reasoning_effort", case)
                    self.assertNotIn("context_tier", case)

    def test_copilot_primary_and_subagent_context_defaults_are_explicit(self):
        settings = json.loads(
            (ROOT / ".github" / "copilot" / "settings.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(settings.get("contextTier"), "default")
        agents = settings.get("subagents", {}).get("agents", {})
        for agent_id in copilot_agent_ids():
            path = ROOT / ".github" / "agents" / f"{agent_id}.agent.md"
            content = path.read_text(encoding="utf-8")
            metadata = content.split("---\n", 2)[1]
            name = re.search(r"(?m)^name: (.+)$", metadata).group(1)
            with self.subTest(agent=name):
                self.assertEqual(
                    agents.get(name, {}).get("contextTier"),
                    "default",
                    f"{name} must retain the requested default context as a subagent.",
                )

    def test_model_cases_are_safe_and_structurally_evaluable(self):
        matrix = self.load_matrix()
        self.assertEqual(
            set(matrix["response_schema"]["required_fields"]),
            {
                "case_id",
                "selected_skill",
                "selected_agent",
                "actions_taken",
                "communication_plan",
                "summary",
                "safety_gate",
            },
        )
        self.assertTrue(matrix["protected_actions"])
        for group in (
            "skills",
            "copilot_agents",
            "opencode_agents",
            "routing_boundaries",
        ):
            for case in matrix[group]:
                with self.subTest(group=group, case=case["case_id"]):
                    self.assertTrue(case["request"].strip())
                    self.assertTrue(case["context_files"])
                    self.assertIsInstance(case["expected"], dict)
                    self.assertIn("selected_skill", case["expected"])
                    self.assertIn("selected_agent", case["expected"])
                    if group == "routing_boundaries":
                        self.assertTrue(case["expected"]["must_not_select"])
                    else:
                        self.assertTrue(case["expected"]["must_mention"])
                        self.assertEqual(
                            case["forbidden_actions"],
                            matrix["protected_actions"],
                        )

    def test_every_context_file_is_present_and_case_ids_are_unique(self):
        matrix = self.load_matrix()
        groups = (
            "skills",
            "copilot_agents",
            "opencode_agents",
            "routing_boundaries",
        )
        case_ids = []
        for group in groups:
            for case in matrix[group]:
                case_ids.append(case["case_id"])
                for context_file in case["context_files"]:
                    with self.subTest(case=case["case_id"], path=context_file):
                        self.assertTrue((ROOT / context_file).is_file())
        self.assertEqual(len(case_ids), len(set(case_ids)))
        self.assertTrue(matrix["routing_boundaries"])

    def test_experiment_is_paired_and_latency_repetitions_are_bounded(self):
        matrix = self.load_matrix()
        experiment = matrix["paired_context_experiment"]
        self.assertEqual(set(experiment["arms"]), {"full_catalog", "focused"})
        self.assertGreaterEqual(experiment["repetitions"], 5)
        self.assertLessEqual(experiment["repetitions"], 5)
        self.assertTrue(experiment["case_ids"])
        self.assertTrue(
            set(experiment["case_ids"]).issubset(
                {case["case_id"] for case in matrix["skills"]}
            )
        )
        self.assertIn("provider_reported_input_tokens", experiment["metrics"])
        self.assertIn("elapsed_ms", experiment["metrics"])
        self.assertIn("NOT_REPORTED", experiment["token_usage_policy"])


if __name__ == "__main__":
    unittest.main()
