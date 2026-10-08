import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
VERIFIER = (
    ROOT
    / ".github"
    / "skills"
    / "ralph-loop"
    / "scripts"
    / "verify_worktree_identity.py"
)


def git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


class WorktreeIdentityTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.repository = self.root / "repository"
        self.repository.mkdir()
        git(self.repository, "init", "--quiet", "--initial-branch=main")
        git(self.repository, "config", "user.name", "Identity Test")
        git(self.repository, "config", "user.email", "identity-test@example.invalid")
        (self.repository / "README.md").write_text("identity fixture\n", encoding="utf-8")
        git(self.repository, "add", "README.md")
        git(self.repository, "commit", "--quiet", "-m", "initialize fixture")
        self.base_sha = git(self.repository, "rev-parse", "HEAD")

    def tearDown(self):
        self.tempdir.cleanup()

    def run_verifier(
        self,
        expected_path=None,
        expected_branch="main",
        expected_base=None,
        environment=None,
    ):
        return subprocess.run(
            [
                sys.executable,
                str(VERIFIER),
                "--expected-path",
                str(expected_path or self.repository),
                "--expected-branch",
                expected_branch,
                "--expected-base-sha",
                expected_base or self.base_sha,
            ],
            cwd=self.repository,
            capture_output=True,
            text=True,
            check=False,
            env=environment,
        )

    def assert_blocked(self, result, check):
        self.assertEqual(1, result.returncode, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual("BLOCKED", report["state"])
        self.assertFalse(report["checks"][check])
        return report

    def test_exact_registered_worktree_identity_is_accepted(self):
        result = self.run_verifier()

        self.assertEqual(0, result.returncode, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual("VERIFIED", report["state"])
        self.assertEqual(
            {
                "path_matches_expected": True,
                "git_root_matches_expected": True,
                "branch_matches_expected": True,
                "head_matches_expected_base": True,
                "working_tree_clean": True,
                "registry_matches_expected_identity": True,
            },
            report["checks"],
        )

    def test_wrong_root_branch_and_head_are_rejected(self):
        other_path = self.root / "other"
        other_path.mkdir()
        cases = (
            (
                other_path,
                "main",
                self.base_sha,
                ("path_matches_expected", "git_root_matches_expected"),
            ),
            (
                self.repository,
                "other-branch",
                self.base_sha,
                ("branch_matches_expected",),
            ),
            (
                self.repository,
                "main",
                "0" * 40,
                ("head_matches_expected_base",),
            ),
        )

        for path, branch, head, failed_checks in cases:
            with self.subTest(path=path, branch=branch, head=head):
                result = self.run_verifier(path, branch, head)
                report = json.loads(result.stdout)
                self.assertEqual(1, result.returncode, result.stderr)
                self.assertEqual("BLOCKED", report["state"])
                for failed_check in failed_checks:
                    self.assertFalse(report["checks"][failed_check])
                self.assertEqual(
                    str(self.repository.resolve()), report["observed"]["git_root"]
                )

    def test_dirty_and_detached_worktrees_are_rejected(self):
        untracked = self.repository / "untracked.txt"
        untracked.write_text("dirty\n", encoding="utf-8")
        dirty = self.assert_blocked(self.run_verifier(), "working_tree_clean")
        self.assertFalse(dirty["checks"]["working_tree_clean"])
        untracked.unlink()

        git(self.repository, "checkout", "--quiet", "--detach", "HEAD")
        detached = self.assert_blocked(self.run_verifier(), "branch_matches_expected")
        self.assertEqual("", detached["observed"]["branch"])

    def test_registry_entry_must_match_exact_path_branch_and_head(self):
        real_git = shutil.which("git")
        self.assertIsNotNone(real_git)
        if real_git is None:
            return

        registry = git(self.repository, "worktree", "list", "--porcelain")
        expected_branch = "branch refs/heads/main"
        expected_head = f"HEAD {self.base_sha}"
        expected_path = f"worktree {self.repository.resolve()}"
        self.assertIn(expected_branch, registry)
        self.assertIn(expected_head, registry)
        self.assertIn(expected_path, registry)
        other_path = self.root / "registered-elsewhere"
        fake_registries = (
            registry.replace(expected_path, f"worktree {other_path}", 1),
            registry.replace(expected_branch, "branch refs/heads/other", 1),
            registry.replace(expected_head, f"HEAD {'0' * 40}", 1),
        )
        fake_bin = self.root / "bin"
        fake_bin.mkdir()
        git_wrapper = fake_bin / "git"
        git_wrapper.write_text(
            f"""#!{sys.executable}
import os
import sys

if sys.argv[1:] == ["worktree", "list", "--porcelain"]:
    sys.stdout.write(os.environ["MOCK_WORKTREE_REGISTRY"])
else:
    os.execv({real_git!r}, [{real_git!r}, *sys.argv[1:]])
""",
            encoding="utf-8",
        )
        git_wrapper.chmod(0o755)
        environment = os.environ.copy()
        environment["PATH"] = str(fake_bin) + os.pathsep + environment.get("PATH", "")
        for fake_registry in fake_registries:
            with self.subTest(registry=fake_registry):
                environment["MOCK_WORKTREE_REGISTRY"] = fake_registry
                report = self.assert_blocked(
                    self.run_verifier(environment=environment),
                    "registry_matches_expected_identity",
                )
                self.assertFalse(
                    report["checks"]["registry_matches_expected_identity"]
                )

    def test_git_command_failure_is_blocked(self):
        real_git = shutil.which("git")
        self.assertIsNotNone(real_git)
        if real_git is None:
            return

        fake_bin = self.root / "failing-bin"
        fake_bin.mkdir()
        git_wrapper = fake_bin / "git"
        git_wrapper.write_text(
            f"""#!{sys.executable}
import os
import sys

if sys.argv[1:] == ["rev-parse", "--show-toplevel"]:
    raise SystemExit(23)
os.execv({real_git!r}, [{real_git!r}, *sys.argv[1:]])
""",
            encoding="utf-8",
        )
        git_wrapper.chmod(0o755)
        environment = os.environ.copy()
        environment["PATH"] = str(fake_bin) + os.pathsep + environment.get("PATH", "")

        result = self.run_verifier(environment=environment)
        self.assertEqual(1, result.returncode)
        self.assertEqual("BLOCKED", json.loads(result.stdout)["state"])

    def test_failed_preflight_does_not_reach_edit_step(self):
        edit_marker = self.root / "edit-attempted"
        environment = os.environ.copy()
        environment.update(
            {
                "PYTHON": sys.executable,
                "VERIFIER": str(VERIFIER),
                "EXPECTED_PATH": str(self.repository),
                "EXPECTED_BRANCH": "main",
                "EXPECTED_BASE": "0" * 40,
                "EDIT_MARKER": str(edit_marker),
            }
        )
        result = subprocess.run(
            [
                "bash",
                "-c",
                'set -e; "$PYTHON" "$VERIFIER" --expected-path "$EXPECTED_PATH" '
                '--expected-branch "$EXPECTED_BRANCH" --expected-base-sha '
                '"$EXPECTED_BASE"; touch "$EDIT_MARKER"',
            ],
            cwd=self.repository,
            capture_output=True,
            text=True,
            check=False,
            env=environment,
        )

        self.assertEqual(1, result.returncode, result.stderr)
        self.assertFalse(edit_marker.exists())


if __name__ == "__main__":
    unittest.main()
