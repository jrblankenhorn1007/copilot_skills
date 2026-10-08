#!/usr/bin/env python3
"""Read-only preflight for an assigned Ralph Git worktree."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional


CHECK_NAMES = (
    "path_matches_expected",
    "git_root_matches_expected",
    "branch_matches_expected",
    "head_matches_expected_base",
    "working_tree_clean",
    "registry_matches_expected_identity",
)


class WorktreeIdentityError(Exception):
    """A worktree identity check could not be completed safely."""


def _run_git(arguments: List[str], cwd: Path) -> str:
    try:
        result = subprocess.run(
            ["git", *arguments],
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        command = " ".join(["git", *arguments])
        raise WorktreeIdentityError(f"required Git command failed: {command}") from exc
    return result.stdout.rstrip("\n")


def _canonical_path(value: str, label: str, strict: bool) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        raise WorktreeIdentityError(f"{label} must be an absolute path")
    try:
        return path.resolve(strict=strict)
    except (OSError, RuntimeError) as exc:
        raise WorktreeIdentityError(f"cannot resolve {label}") from exc


def _parse_worktree_registry(contents: str) -> List[Dict[str, str]]:
    entries: List[Dict[str, str]] = []
    for block in contents.split("\n\n"):
        fields: Dict[str, str] = {}
        for line in block.splitlines():
            key, separator, value = line.partition(" ")
            if separator:
                fields[key] = value
            elif key == "detached":
                fields[key] = ""
        if "worktree" in fields:
            entries.append(fields)
    return entries


def verify_worktree_identity(
    expected_path: str,
    expected_branch: str,
    expected_base_sha: str,
) -> Dict[str, object]:
    if not expected_branch:
        raise WorktreeIdentityError("expected branch must not be empty")
    if re.fullmatch(r"(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})", expected_base_sha) is None:
        raise WorktreeIdentityError("expected base SHA must be a full Git object ID")

    canonical_expected = _canonical_path(expected_path, "expected path", strict=True)
    try:
        observed_pwd = Path.cwd().resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise WorktreeIdentityError("cannot resolve the current working directory") from exc
    observed_root = _canonical_path(
        _run_git(["rev-parse", "--show-toplevel"], observed_pwd),
        "Git root",
        strict=True,
    )
    observed_branch = _run_git(["branch", "--show-current"], observed_pwd)
    observed_head = _run_git(["rev-parse", "HEAD"], observed_pwd).lower()
    status = _run_git(
        ["status", "--porcelain=v1", "--untracked-files=all"], observed_pwd
    )
    registry = _parse_worktree_registry(
        _run_git(["worktree", "list", "--porcelain"], observed_pwd)
    )

    matching_paths: List[Dict[str, str]] = []
    for entry in registry:
        try:
            registered_path = _canonical_path(
                entry["worktree"], "registered worktree path", strict=False
            )
        except WorktreeIdentityError:
            continue
        if registered_path == canonical_expected:
            matching_paths.append(entry)

    expected_head = expected_base_sha.lower()
    registry_entry: Optional[Dict[str, str]] = (
        matching_paths[0] if len(matching_paths) == 1 else None
    )
    checks = {
        "path_matches_expected": observed_pwd == canonical_expected,
        "git_root_matches_expected": observed_root == canonical_expected,
        "branch_matches_expected": observed_branch == expected_branch,
        "head_matches_expected_base": observed_head == expected_head,
        "working_tree_clean": status == "",
        "registry_matches_expected_identity": (
            registry_entry is not None
            and registry_entry.get("branch") == f"refs/heads/{expected_branch}"
            and registry_entry.get("HEAD", "").lower() == expected_head
        ),
    }
    report: Dict[str, object] = {
        "state": "VERIFIED" if all(checks.values()) else "BLOCKED",
        "expected": {
            "path": str(canonical_expected),
            "branch": expected_branch,
            "base_sha": expected_head,
        },
        "observed": {
            "pwd": str(observed_pwd),
            "git_root": str(observed_root),
            "branch": observed_branch,
            "head_sha": observed_head,
            "working_tree_clean": status == "",
            "registry_entry": registry_entry,
        },
        "checks": checks,
    }
    return report


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify the current session is bound to its assigned clean Git worktree."
    )
    parser.add_argument("--expected-path", required=True)
    parser.add_argument("--expected-branch", required=True)
    parser.add_argument("--expected-base-sha", required=True)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = _parser().parse_args(argv)
    try:
        report = verify_worktree_identity(
            args.expected_path,
            args.expected_branch,
            args.expected_base_sha,
        )
    except WorktreeIdentityError as exc:
        print(
            json.dumps(
                {
                    "state": "BLOCKED",
                    "checks": {name: False for name in CHECK_NAMES},
                    "error": str(exc),
                },
                indent=2,
            )
        )
        return 1

    print(json.dumps(report, indent=2))
    return 0 if report["state"] == "VERIFIED" else 1


if __name__ == "__main__":
    sys.exit(main())
