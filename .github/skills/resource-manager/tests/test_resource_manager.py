import json
import os
import platform
import sys
import subprocess
import stat
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SKILL = ROOT / ".github" / "skills" / "resource-manager" / "SKILL.md"
MANAGER = (
    ROOT
    / ".github"
    / "skills"
    / "resource-manager"
    / "scripts"
    / "resource_manager.py"
)
sys.path.insert(0, str(MANAGER.parent))
import resource_manager as manager


GIB = 1024**3
NOW = datetime(2026, 9, 25, 12, 0, tzinfo=timezone.utc)


def read_document(path):
    return path.read_text(encoding="utf-8").lower() if path.is_file() else ""


def host_metrics(total_gib=8, available_gib=4, cpu_cores=6, load_1m=0.2):
    return manager.HostMetrics(
        total_memory_bytes=total_gib * GIB,
        available_memory_bytes=available_gib * GIB,
        cpu_cores=cpu_cores,
        load_1m=load_1m,
    )


class ResourceManagerContractTests(unittest.TestCase):
    def test_shared_resource_manager_skill_and_cli_exist(self):
        self.assertTrue(SKILL.is_file(), "resource-manager skill must be installed")
        self.assertTrue(
            MANAGER.is_file(),
            "shared local registration CLI must be installed with the skill",
        )

    def test_operational_guidance_gates_agent_spawning_on_registration(self):
        skill = read_document(SKILL)
        global_instructions = read_document(ROOT / ".github" / "copilot-instructions.md")
        ralph_agent = read_document(ROOT / ".github" / "agents" / "ralph-loop.agent.md")
        orchestration = read_document(
            ROOT
            / ".github"
            / "skills"
            / "ralph-loop"
            / "references"
            / "multi-agent-orchestration.md"
        )
        readme = read_document(ROOT / "README.md")

        for document, requirements in (
            (skill, ("registry.json", "reserve", "activate", "memory_pressure")),
            (global_instructions, ("resource-manager", "register", "reserve")),
            (ralph_agent, ("resource-manager", "activate", "no slot")),
            (orchestration, ("resource-manager", "counts as one agent", "reserve")),
            (readme, (".github/skills/resource-manager/skill.md",)),
        ):
            with self.subTest(requirements=requirements):
                for requirement in requirements:
                    self.assertTrue(
                        requirement in document,
                        f"missing requirement {requirement!r}",
                    )


class CapacityTests(unittest.TestCase):
    def test_eight_gib_six_core_machine_has_two_slots_at_normal_load(self):
        capacity = manager.calculate_capacity(host_metrics())
        self.assertEqual(2, capacity.max_agents)
        self.assertEqual(2, capacity.ram_agents)
        self.assertEqual(3, capacity.cpu_agents)

    def test_live_memory_and_cpu_pressure_reduce_admission(self):
        low_memory = manager.calculate_capacity(host_metrics(available_gib=2.5))
        critical_memory = manager.calculate_capacity(host_metrics(available_gib=1.5))
        high_load = manager.calculate_capacity(host_metrics(load_1m=5.2))
        saturated_cpu = manager.calculate_capacity(host_metrics(load_1m=6.0))

        self.assertEqual(1, low_memory.max_agents)
        self.assertEqual(0, critical_memory.max_agents)
        self.assertEqual(1, high_load.max_agents)
        self.assertEqual(0, saturated_cpu.max_agents)

    def test_capacity_obeys_ram_cpu_and_global_ceilings(self):
        small_host = manager.calculate_capacity(
            host_metrics(total_gib=8, available_gib=4, cpu_cores=2)
        )
        large_host = manager.calculate_capacity(
            host_metrics(total_gib=32, available_gib=24, cpu_cores=16)
        )

        self.assertEqual(1, small_host.max_agents)
        self.assertEqual(manager.MAX_AGENTS, large_host.max_agents)

    def test_macos_and_linux_memory_readers_parse_supported_formats(self):
        free_percentage = manager.parse_macos_free_percentage(
            "System-wide memory free percentage: 40%"
        )
        total, available = manager.parse_linux_memory_info(
            "MemTotal:       8388608 kB\nMemAvailable:   4194304 kB\n"
        )

        self.assertEqual(40, free_percentage)
        self.assertEqual(8388608 * 1024, total)
        self.assertEqual(4194304 * 1024, available)


class CommandLineTests(unittest.TestCase):
    @unittest.skipUnless(platform.system() in {"Darwin", "Linux"}, "unsupported host")
    def test_status_reads_live_hardware_and_fails_closed_without_inventory(self):
        with tempfile.TemporaryDirectory() as registry:
            environment = os.environ.copy()
            environment["COPILOT_AGENT_RESOURCE_MANAGER_DIR"] = registry
            result = subprocess.run(
                [
                    sys.executable,
                    str(MANAGER),
                    "status",
                ],
                check=False,
                capture_output=True,
                env=environment,
                text=True,
            )

        self.assertEqual(0, result.returncode, result.stderr)
        status = json.loads(result.stdout)
        self.assertIn(status["hardware"]["platform"], {"Darwin", "Linux"})
        self.assertFalse(status["inventory_fresh"])
        self.assertFalse(status["can_spawn"])


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.registry = Path(self.tempdir.name) / "shared-registry"
        self.metrics = host_metrics()

    def tearDown(self):
        self.tempdir.cleanup()

    def register_parent(self, observed=("orchestrator-runtime",)):
        return manager.register_agent(
            self.registry,
            "orchestrator",
            role="orchestrator",
            runtime_id="orchestrator-runtime",
            observed_session_ids=observed,
            metrics=self.metrics,
            now=NOW,
        )

    def reserve_worker(self, worker_id, observed=("orchestrator-runtime",)):
        return manager.reserve_agent(
            self.registry,
            worker_id,
            role="worker",
            parent_id="orchestrator",
            observed_session_ids=observed,
            metrics=self.metrics,
            now=NOW,
        )

    def test_observed_unregistered_sessions_consume_capacity(self):
        self.register_parent(("orchestrator-runtime", "existing-worker"))

        with self.assertRaises(manager.AdmissionDenied):
            self.reserve_worker("new-worker", ("orchestrator-runtime", "existing-worker"))

    def test_runtime_identity_cannot_be_bound_to_two_agents(self):
        self.register_parent()

        with self.assertRaises(manager.RegistryError):
            manager.register_agent(
                self.registry,
                "second-agent",
                role="agent",
                runtime_id="orchestrator-runtime",
                observed_session_ids=("orchestrator-runtime",),
                metrics=self.metrics,
                now=NOW,
            )

    @unittest.skipUnless(os.name == "posix", "POSIX file modes unavailable")
    def test_registry_rejects_shared_directory_with_open_permissions(self):
        self.registry.mkdir(mode=0o700)
        self.registry.chmod(0o755)

        with self.assertRaises(manager.RegistryError):
            self.register_parent()

    def test_reservation_counts_until_activation_and_release(self):
        self.register_parent()
        reserved = self.reserve_worker("worker-01")
        reservation_id = reserved["agent"]["reservation_id"]

        activated = manager.activate_agent(
            self.registry,
            "worker-01",
            reservation_id,
            "worker-runtime",
            NOW,
        )
        current = manager.get_status(
            self.registry,
            observed_session_ids=("orchestrator-runtime", "worker-runtime"),
            metrics=self.metrics,
            now=NOW,
        )

        self.assertEqual("active", activated["agent"]["status"])
        self.assertEqual(2, current["active_agent_count"])
        self.assertFalse(current["can_spawn"])
        manager.release_agent(self.registry, "worker-01", now=NOW)
        self.assertEqual(
            1,
            manager.get_status(
                self.registry,
                observed_session_ids=("orchestrator-runtime",),
                metrics=self.metrics,
                now=NOW,
            )["active_agent_count"],
        )

    def test_concurrent_reservations_cannot_exceed_capacity(self):
        self.register_parent()

        def attempt(index):
            try:
                return self.reserve_worker(f"worker-{index}")
            except manager.AdmissionDenied:
                return None

        with ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(attempt, range(8)))

        self.assertEqual(1, sum(result is not None for result in results))
        status = manager.get_status(
            self.registry,
            observed_session_ids=("orchestrator-runtime",),
            metrics=self.metrics,
            now=NOW,
        )
        self.assertEqual(2, status["active_agent_count"])
        self.assertEqual(1, status["reserved_agent_count"])

    def test_existing_overcommitted_agent_can_register_but_cannot_spawn(self):
        self.register_parent(
            ("orchestrator-runtime", "existing-worker-01", "existing-worker-02")
        )
        status = manager.get_status(
            self.registry,
            metrics=self.metrics,
            now=NOW,
        )

        self.assertEqual(3, status["active_agent_count"])
        self.assertTrue(status["inventory_fresh"])
        self.assertFalse(status["can_spawn"])

    @unittest.skipUnless(os.name == "posix", "POSIX file modes unavailable")
    def test_registry_files_are_private_to_the_current_user(self):
        self.register_parent()
        for path in (self.registry, self.registry / "registry.json", self.registry / "registry.lock"):
            self.assertEqual(0, stat.S_IMODE(path.stat().st_mode) & 0o077)

    def test_expired_leases_are_pruned_and_corrupt_state_is_not_reset(self):
        self.register_parent()
        expired_status = manager.get_status(
            self.registry,
            metrics=self.metrics,
            now=NOW.replace(hour=13),
        )
        self.assertEqual(0, expired_status["registered_agent_count"])

        registry_file = self.registry / "registry.json"
        registry_file.write_text("{invalid", encoding="utf-8")
        with self.assertRaises(manager.RegistryError):
            manager.get_status(self.registry, metrics=self.metrics, now=NOW)


if __name__ == "__main__":
    unittest.main()
