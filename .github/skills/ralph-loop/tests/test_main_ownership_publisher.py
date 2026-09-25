from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[4]
PUBLISHER = ROOT / ".github/skills/ralph-loop/scripts/publish_agent_sync.py"
OWNERSHIP_PATH = "docs/agent-sync/main/ownership.json"


class MainOwnershipPublisherTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.remote = self.root / "origin.git"
        self.seed = self.root / "seed"
        self.publisher = self.root / "publisher.git"
        self.prompt_file = self.root / "prompt.md"
        self.status_file = self.root / "status.json"
        self.git(self.root, "init", "--bare", "--initial-branch=main", str(self.remote))
        self.git(self.root, "init", "--initial-branch=main", str(self.seed))
        self.git(self.seed, "config", "user.name", "Main Ownership Test")
        self.git(self.seed, "config", "user.email", "ownership@example.invalid")
        (self.seed / "README.md").write_text("seed\n", encoding="utf-8")
        self.git(self.seed, "add", "README.md")
        self.git(self.seed, "commit", "-m", "seed main")
        self.git(self.seed, "remote", "add", "origin", str(self.remote))
        self.git(self.seed, "push", "origin", "main")
        self.git(self.root, "clone", "--bare", str(self.remote), str(self.publisher))
        self.git(self.publisher, "config", "user.name", "Main Ownership Test")
        self.git(self.publisher, "config", "user.email", "ownership@example.invalid")
        self.initial_main = self.git(self.remote, "rev-parse", "refs/heads/main")
        self.prompt = b"Implement only the assigned task.\n"
        self.prompt_file.write_bytes(self.prompt)

    def git(self, repository, *args):
        command = ["git", *args]
        if repository in (getattr(self, "remote", None), getattr(self, "publisher", None)):
            command = ["git", "--git-dir", str(repository), *args]
        result = subprocess.run(
            command,
            cwd=self.root if command[1] == "--git-dir" else repository,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, f"git {' '.join(args)}: {result.stderr}")
        return result.stdout.strip()

    def status(self, *, revision=1):
        run_id = "test-run"
        agent_id = "worker-01"
        return {
            "schema_version": 1,
            "run_id": run_id,
            "agent_id": agent_id,
            "worker_id": agent_id,
            "worker_name": agent_id,
            "task_id": "ownership-publisher-test",
            "status": "IN_PROGRESS",
            "revision": revision,
            "started_at_utc": "2026-09-25T00:00:00Z",
            "updated_at_utc": f"2026-09-25T00:0{revision}:00Z",
            "prompt_path": f"docs/agent-sync/runs/{run_id}/agents/{agent_id}/prompt.md",
            "prompt_sha256": hashlib.sha256(self.prompt).hexdigest(),
            "agent_profile": {
                "harness": "test",
                "agent_definition": ".github/agents/ralph-loop.agent.md",
                "runtime_agent_id": None,
                "model_id": None,
                "reasoning_effort": None,
                "context_tier": None,
                "context_window_tokens": None,
                "context_usage_tokens": None,
            },
            "git": {
                "remote_name": "origin",
                "repository": "test/repository",
                "implementation_branch": "refs/heads/ralph/test-worker-01",
                "worktree_path": "/test/worker-01",
                "base_ref": "refs/heads/main",
                "base_sha": self.initial_main,
                "worktree_head_sha_at_sign_in": self.initial_main,
                "edit_scope": ["src/example.py"],
            },
            "sign_in_at_utc": "2026-09-25T00:00:00Z",
            "sign_out": {
                "at_utc": None,
                "implementation_commit_sha": None,
                "summary": None,
                "checks": [],
                "next_action": None,
            },
        }

    def invoke(self, status, *, first=True, extra_args=()):
        self.status_file.write_text(json.dumps(status), encoding="utf-8")
        command = [
            sys.executable,
            str(PUBLISHER),
            "--repository",
            str(self.publisher),
            "--run-id",
            status["run_id"],
            "--agent-id",
            status["agent_id"],
            "--status-file",
            str(self.status_file),
        ]
        if first:
            command.extend(["--prompt-file", str(self.prompt_file)])
        command.extend(extra_args)
        return subprocess.run(
            command, cwd=self.root, capture_output=True, text=True, check=False
        )

    def ownership(self):
        return json.loads(self.git(self.remote, "show", f"main:{OWNERSHIP_PATH}"))

    def action(
        self,
        action,
        *,
        run_id="test-run",
        agent_id="worker-01",
        token=None,
        outcome=None,
        result_commit=None,
        worktree=None,
    ):
        command = [
            sys.executable,
            str(PUBLISHER),
            "--repository",
            str(self.publisher),
            "--repository-id",
            "test/repository",
            "--run-id",
            run_id,
            "--agent-id",
            agent_id,
            "--main-action",
            action,
            "--wait-seconds",
            "0",
        ]
        if worktree is not None:
            command.extend(["--main-worktree", str(worktree)])
        if token is not None:
            command.extend(["--main-token", token])
        if outcome is not None:
            command.extend(["--outcome", outcome])
        if result_commit is not None:
            command.extend(["--result-commit-sha", result_commit])
        return subprocess.run(
            command, cwd=self.root, capture_output=True, text=True, check=False
        )

    def load_publisher(self):
        spec = importlib.util.spec_from_file_location("main_ownership_publisher", PUBLISHER)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def changed_paths(self, commit):
        return self.git(
            self.remote, "diff-tree", "--no-commit-id", "--name-only", "-r", commit
        ).splitlines()

    def test_status_commit_is_bounded_by_main_signin_and_immediate_signout(self):
        result = self.invoke(self.status())
        self.assertEqual(result.returncode, 0, result.stderr)
        published = json.loads(result.stdout)
        status_commit = published["commit_sha"]
        release_commit = self.git(self.remote, "rev-parse", "refs/heads/main")
        self.assertNotEqual(status_commit, release_commit)
        self.assertEqual(
            self.changed_paths(release_commit), [OWNERSHIP_PATH],
            "the last commit must release main without unrelated changes",
        )
        claim_commit = self.git(self.remote, "rev-parse", f"{status_commit}^")
        self.assertEqual(self.changed_paths(claim_commit), [OWNERSHIP_PATH])
        self.assertEqual(published["main_sign_in_commit_sha"], claim_commit)
        self.assertEqual(published["main_sign_out_commit_sha"], release_commit)
        claim = json.loads(self.git(self.remote, "show", f"{claim_commit}:{OWNERSHIP_PATH}"))
        self.assertEqual(claim["state"], "OWNED")
        self.assertEqual(claim["owner"]["operation"], "STATUS")
        self.assertIsNone(claim["owner"]["worktree_path"])
        self.assertIsNone(claim["sign_out"]["at_utc"])
        self.assertEqual(
            self.changed_paths(status_commit),
            [
                "docs/agent-sync/runs/test-run/agents/worker-01/prompt.md",
                "docs/agent-sync/runs/test-run/agents/worker-01/status.json",
            ],
        )
        ownership = self.ownership()
        self.assertEqual(ownership["state"], "FREE")
        self.assertEqual(ownership["owner"]["run_id"], "test-run")
        self.assertEqual(ownership["owner"]["agent_id"], "worker-01")
        self.assertEqual(ownership["sign_out"]["result_commit_sha"], status_commit)
        task = json.loads(
            self.git(
                self.remote,
                "show",
                "main:docs/agent-sync/runs/test-run/agents/worker-01/status.json",
            )
        )
        self.assertEqual(task["status"], "IN_PROGRESS")
        self.assertIsNone(task["sign_out"]["at_utc"])
        self.assertEqual(
            self.git(self.publisher, "rev-parse", "refs/heads/main"),
            self.initial_main,
            "status publication must not check out or advance local main",
        )

    def test_idempotent_status_retry_does_not_reserve_main_or_push(self):
        status = self.status()
        first = self.invoke(status)
        self.assertEqual(first.returncode, 0, first.stderr)
        settled_head = self.git(self.remote, "rev-parse", "refs/heads/main")

        repeated = self.invoke(status, first=False)
        self.assertEqual(repeated.returncode, 0, repeated.stderr)
        self.assertEqual(json.loads(repeated.stdout)["result"], "ALREADY_CURRENT")
        self.assertEqual(
            self.git(self.remote, "rev-parse", "refs/heads/main"),
            settled_head,
            "an unchanged status must not acquire and release main again",
        )

    def test_foreign_main_owner_blocks_status_publication(self):
        owner = {
            "schema_version": 1,
            "revision": 1,
            "repository": "test/repository",
            "ref": "refs/heads/main",
            "state": "OWNED",
            "owner": {
                "run_id": "another-run",
                "agent_id": "worker-02",
                "runtime_agent_id": None,
                "operation": "MERGE",
                "worktree_path": None,
                "start_main_sha": self.initial_main,
                "signed_in_at_utc": "2026-09-25T00:00:00Z",
                "token": "another-unique-token",
            },
            "sign_out": {
                "at_utc": None,
                "result_commit_sha": None,
                "outcome": None,
            },
        }
        path = self.seed / OWNERSHIP_PATH
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(owner), encoding="utf-8")
        self.git(self.seed, "add", OWNERSHIP_PATH)
        self.git(self.seed, "commit", "-m", "reserve main for another agent")
        self.git(self.seed, "push", "origin", "main")
        reserved_head = self.git(self.remote, "rev-parse", "refs/heads/main")

        result = self.invoke(self.status(), extra_args=("--wait-seconds", "0"))
        self.assertNotEqual(result.returncode, 0, "foreign main owner must block")
        self.assertIn("main", result.stderr.lower())
        self.assertEqual(self.git(self.remote, "rev-parse", "refs/heads/main"), reserved_head)
        self.assertEqual(self.ownership(), owner)

    def test_competing_agents_wait_until_recorded_owner_signs_out(self):
        with ThreadPoolExecutor(max_workers=2) as executor:
            first = executor.submit(
                self.action, "acquire", run_id="run-one", agent_id="worker-01"
            )
            second = executor.submit(
                self.action, "acquire", run_id="run-two", agent_id="worker-02"
            )
            results = [first.result(), second.result()]
        winners = [result for result in results if result.returncode == 0]
        losers = [result for result in results if result.returncode != 0]
        self.assertEqual(len(winners), 1, [result.stderr for result in results])
        self.assertEqual(len(losers), 1, [result.stderr for result in results])
        self.assertIn("wait for", losers[0].stderr)
        winner = json.loads(winners[0].stdout)
        owner = self.ownership()
        self.assertEqual(owner["revision"], 1)
        self.assertEqual(owner["state"], "OWNED")
        self.assertEqual(owner["owner"]["token"], winner["token"])
        self.assertEqual(
            self.git(
                self.publisher,
                "for-each-ref",
                "--format=%(refname)",
                "refs/agent-sync/fetch",
            ),
            "",
            "temporary per-agent fetch refs must be cleaned up",
        )

        other_run = "run-two" if owner["owner"]["run_id"] == "run-one" else "run-one"
        other_agent = "worker-02" if other_run == "run-two" else "worker-01"
        foreign_release = self.action(
            "release",
            run_id=other_run,
            agent_id=other_agent,
            token=winner["token"],
            outcome="QUEUED",
        )
        self.assertNotEqual(foreign_release.returncode, 0)
        self.assertEqual(self.ownership(), owner)
        release = self.action(
            "release",
            run_id=owner["owner"]["run_id"],
            agent_id=owner["owner"]["agent_id"],
            token=winner["token"],
            outcome="QUEUED",
        )
        self.assertEqual(release.returncode, 0, release.stderr)
        self.assertEqual(self.ownership()["state"], "FREE")
        next_owner = self.action("acquire", run_id=other_run, agent_id=other_agent)
        self.assertEqual(next_owner.returncode, 0, next_owner.stderr)
        self.assertEqual(self.ownership()["revision"], 3)
        self.assertEqual(self.ownership()["owner"]["run_id"], other_run)

    def test_waiting_status_agent_proceeds_only_after_first_owner_releases(self):
        first = self.action("acquire", run_id="run-one", agent_id="worker-01")
        self.assertEqual(first.returncode, 0, first.stderr)
        token = json.loads(first.stdout)["token"]
        second_status = self.status()
        second_status["run_id"] = "run-two"
        second_status["agent_id"] = "worker-02"
        second_status["worker_id"] = "worker-02"
        second_status["worker_name"] = "worker-02"
        second_status["prompt_path"] = (
            "docs/agent-sync/runs/run-two/agents/worker-02/prompt.md"
        )
        with ThreadPoolExecutor(max_workers=1) as executor:
            waiting = executor.submit(
                self.invoke,
                second_status,
                extra_args=("--wait-seconds", "5"),
            )
            time.sleep(0.25)
            self.assertFalse(waiting.done(), "status agent must wait for main sign-out")
            self.assertEqual(self.ownership()["owner"]["run_id"], "run-one")
            released = self.action(
                "release",
                run_id="run-one",
                agent_id="worker-01",
                token=token,
                outcome="QUEUED",
            )
            self.assertEqual(released.returncode, 0, released.stderr)
            result = waiting.result(timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.ownership()["state"], "FREE")
        self.assertEqual(self.ownership()["owner"]["run_id"], "run-two")

    def test_verified_local_main_merge_can_release_the_reserved_checkout(self):
        claimed = self.action("acquire", worktree=self.seed)
        self.assertEqual(claimed.returncode, 0, claimed.stderr)
        token = json.loads(claimed.stdout)["token"]
        self.assertEqual(
            self.ownership()["owner"]["worktree_path"], str(self.seed.resolve())
        )

        self.git(self.seed, "fetch", "origin")
        self.git(self.seed, "merge", "--ff-only", "origin/main")
        (self.seed / "README.md").write_text("merged content\n", encoding="utf-8")
        self.git(self.seed, "add", "README.md")
        self.git(self.seed, "commit", "-m", "authorized merge result")
        merged_sha = self.git(self.seed, "rev-parse", "HEAD")
        self.git(self.seed, "push", "origin", "main")
        released = self.action(
            "release", token=token, outcome="MERGED", result_commit=merged_sha
        )
        self.assertEqual(released.returncode, 0, released.stderr)
        self.assertEqual(self.ownership()["sign_out"]["result_commit_sha"], merged_sha)
        self.assertEqual(self.ownership()["state"], "FREE")

    def test_release_rejects_a_result_from_before_main_signin(self):
        claimed = self.action("acquire")
        self.assertEqual(claimed.returncode, 0, claimed.stderr)
        token = json.loads(claimed.stdout)["token"]
        stale_release = self.action(
            "release",
            token=token,
            result_commit=self.initial_main,
            outcome="MERGED",
        )
        self.assertNotEqual(stale_release.returncode, 0)
        self.assertEqual(self.ownership()["state"], "OWNED")

    def test_merge_cannot_be_signed_out_without_a_verified_result_commit(self):
        claimed = self.action("acquire")
        self.assertEqual(claimed.returncode, 0, claimed.stderr)
        token = json.loads(claimed.stdout)["token"]
        incomplete = self.action("release", token=token, outcome="MERGED")
        self.assertNotEqual(incomplete.returncode, 0)
        self.assertEqual(self.ownership()["state"], "OWNED")

    def test_status_revisions_survive_unrelated_main_updates(self):
        first = self.invoke(self.status())
        self.assertEqual(first.returncode, 0, first.stderr)
        self.git(self.seed, "fetch", "origin")
        self.git(self.seed, "merge", "--ff-only", "origin/main")
        (self.seed / "README.md").write_text("seed\nunrelated update\n", encoding="utf-8")
        self.git(self.seed, "add", "README.md")
        self.git(self.seed, "commit", "-m", "unrelated main change")
        unrelated_main = self.git(self.seed, "rev-parse", "HEAD")
        self.git(self.seed, "push", "origin", "main")

        second = self.invoke(self.status(revision=2), first=False)
        self.assertEqual(second.returncode, 0, second.stderr)
        published = json.loads(second.stdout)
        self.assertEqual(
            self.git(self.remote, "rev-parse", f"{published['main_sign_in_commit_sha']}^"),
            unrelated_main,
        )
        self.assertEqual(
            self.git(self.remote, "rev-parse", f"{published['commit_sha']}^"),
            published["main_sign_in_commit_sha"],
        )
        stored = json.loads(
            self.git(
                self.remote,
                "show",
                "main:docs/agent-sync/runs/test-run/agents/worker-01/status.json",
            )
        )
        self.assertEqual(stored["revision"], 2)

        rejected = self.invoke(
            self.status(revision=4),
            first=False,
            extra_args=("--wait-seconds", "0"),
        )
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn("revision must increment", rejected.stderr)
        self.assertEqual(self.ownership()["state"], "FREE")
        self.assertEqual(self.ownership()["sign_out"]["outcome"], "FAILED")
        stored = json.loads(
            self.git(
                self.remote,
                "show",
                "main:docs/agent-sync/runs/test-run/agents/worker-01/status.json",
            )
        )
        self.assertEqual(stored["revision"], 2)

    def test_ambiguous_push_result_is_reconciled_at_each_transaction_step(self):
        module = self.load_publisher()
        original_run_git = module.run_git
        for phase in (1, 2, 3):
            with self.subTest(ambiguous_push=phase):
                pushes = 0

                def lose_push_response(repository, *args, **kwargs):
                    nonlocal pushes
                    result = original_run_git(repository, *args, **kwargs)
                    if args[0] == "push":
                        pushes += 1
                        if pushes == phase:
                            return subprocess.CompletedProcess(
                                result.args, 1, result.stdout, b"connection dropped"
                            )
                    return result

                self.status_file.write_text(
                    json.dumps(self.status(revision=phase)), encoding="utf-8"
                )
                with patch.object(module, "run_git", side_effect=lose_push_response):
                    result = module.publish(
                        repository=self.publisher,
                        run_id="test-run",
                        agent_id="worker-01",
                        status_file=self.status_file,
                        prompt_file=self.prompt_file if phase == 1 else None,
                        max_attempts=3,
                        wait_seconds=0,
                    )
                self.assertEqual(pushes, 3)
                self.assertEqual(result["result"], "PUBLISHED")
                self.assertEqual(self.ownership()["state"], "FREE")
                self.assertEqual(
                    self.ownership()["sign_out"]["result_commit_sha"],
                    result["commit_sha"],
                )

    def test_failed_release_surfaces_blocker_and_leaves_main_reserved(self):
        module = self.load_publisher()
        original_run_git = module.run_git
        pushes = 0

        def reject_release(repository, *args, **kwargs):
            nonlocal pushes
            if args[0] == "push":
                pushes += 1
                if pushes == 3:
                    return subprocess.CompletedProcess(
                        ["git", *args], 1, b"", b"main release denied"
                    )
            return original_run_git(repository, *args, **kwargs)

        self.status_file.write_text(json.dumps(self.status()), encoding="utf-8")
        with patch.object(module, "run_git", side_effect=reject_release):
            with self.assertRaisesRegex(module.PublishError, "main release failed"):
                module.publish(
                    repository=self.publisher,
                    run_id="test-run",
                    agent_id="worker-01",
                    status_file=self.status_file,
                    prompt_file=self.prompt_file,
                    max_attempts=3,
                    wait_seconds=0,
                )
        self.assertEqual(pushes, 3)
        self.assertEqual(self.ownership()["state"], "OWNED")
        self.assertEqual(
            self.changed_paths(self.git(self.remote, "rev-parse", "refs/heads/main")),
            [
                "docs/agent-sync/runs/test-run/agents/worker-01/prompt.md",
                "docs/agent-sync/runs/test-run/agents/worker-01/status.json",
            ],
        )

    def test_transient_verification_fetch_failure_does_not_mislabel_published_status(self):
        module = self.load_publisher()
        original_run_git = module.run_git
        original_fetch_main = module.fetch_main
        for revision, interruptions in ((1, 1), (2, 3)):
            with self.subTest(verification_failures=interruptions):
                pushes = 0
                failures_remaining = interruptions

                def track_pushes(repository, *args, **kwargs):
                    nonlocal pushes
                    result = original_run_git(repository, *args, **kwargs)
                    if args[0] == "push":
                        pushes += 1
                    return result

                def fail_verification(repository):
                    nonlocal failures_remaining
                    if pushes == 2 and failures_remaining:
                        failures_remaining -= 1
                        raise module.PublishError("temporary verification fetch failure")
                    return original_fetch_main(repository)

                self.status_file.write_text(
                    json.dumps(self.status(revision=revision)), encoding="utf-8"
                )
                with (
                    patch.object(module, "run_git", side_effect=track_pushes),
                    patch.object(module, "fetch_main", side_effect=fail_verification),
                ):
                    result = module.publish(
                        repository=self.publisher,
                        run_id="test-run",
                        agent_id="worker-01",
                        status_file=self.status_file,
                        prompt_file=self.prompt_file if revision == 1 else None,
                        max_attempts=3,
                        wait_seconds=0,
                    )
                self.assertEqual(failures_remaining, 0)
                self.assertEqual(result["result"], "PUBLISHED")
                self.assertEqual(self.ownership()["state"], "FREE")
                self.assertEqual(self.ownership()["sign_out"]["outcome"], "PUBLISHED")

    def test_dirty_main_worktree_is_not_used_for_a_merge_reservation(self):
        (self.seed / "README.md").write_text("uncommitted\n", encoding="utf-8")
        result = self.action("acquire", worktree=self.seed)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(
            self.git(self.remote, "rev-parse", "refs/heads/main"), self.initial_main
        )

    def test_fetch_interruption_cleans_its_temporary_ref(self):
        module = self.load_publisher()
        original_run_git = module.run_git

        def fail_after_fetch(repository, *args, **kwargs):
            result = original_run_git(repository, *args, **kwargs)
            if args[0] == "fetch":
                raise module.PublishError("simulated interruption after fetch")
            return result

        with patch.object(module, "run_git", side_effect=fail_after_fetch):
            with self.assertRaisesRegex(module.PublishError, "after fetch"):
                module.fetch_main(self.publisher)
        self.assertEqual(
            self.git(
                self.publisher,
                "for-each-ref",
                "--format=%(refname)",
                "refs/agent-sync/fetch",
            ),
            "",
        )


if __name__ == "__main__":
    unittest.main()
