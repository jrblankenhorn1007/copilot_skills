#!/usr/bin/env python3
"""Publish one agent's coordination snapshot directly to origin/main."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import sys
import tempfile
import time
from typing import Any, Dict, List, Optional


STATUSES = {
    "IN_PROGRESS",
    "BLOCKED",
    "AWAITING_MERGE",
    "COMPLETE",
    "FAILED",
    "CANCELLED",
}
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
TERMINAL_STATUSES = {"AWAITING_MERGE", "COMPLETE", "FAILED", "CANCELLED"}
MAX_ATTEMPTS = 5
MAIN_OWNERSHIP_PATH = "docs/agent-sync/main/ownership.json"
MAIN_REF = "refs/heads/main"
DEFAULT_WAIT_SECONDS = 30


class PublishError(Exception):
    """An input, concurrency, or remote-policy error safe to report to an agent."""


class UnverifiedPushError(PublishError):
    """The remote may contain this commit, so do not release it as failed."""

    def __init__(self, commit_sha: str):
        super().__init__(f"could not verify whether commit {commit_sha} reached main")
        self.commit_sha = commit_sha


def redact(text: str) -> str:
    text = re.sub(
        r"(?i)(https?://)[^\s/@]+(?::[^\s/@]*)?@",
        r"\1[redacted]@",
        text,
    )
    return re.sub(
        r"\b(?:gh[pousr]_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+)\b",
        "[redacted]",
        text,
    )


def run_git(
    repository: Path,
    *args: str,
    env: Optional[Dict[str, str]] = None,
    input_data: Optional[bytes] = None,
    check: bool = True,
) -> subprocess.CompletedProcess[bytes]:
    if (
        (repository / "HEAD").is_file()
        and (repository / "objects").is_dir()
        and (repository / "config").is_file()
    ):
        command = ["git", "--git-dir", str(repository), *args]
    else:
        command = ["git", "-C", str(repository), *args]
    result = subprocess.run(
        command,
        env=env,
        input=input_data,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and result.returncode:
        stderr = redact(result.stderr.decode("utf-8", errors="replace").strip())
        command = " ".join(args[:2])
        raise PublishError(
            f"git {command} failed (exit {result.returncode}): {stderr}"
        )
    return result


def text_output(result: subprocess.CompletedProcess[bytes]) -> str:
    return result.stdout.decode("utf-8", errors="strict").strip()


def validate_timestamp(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise PublishError(f"{field} must be an ISO 8601 UTC timestamp ending in Z")
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as error:
        raise PublishError(f"{field} is not a valid ISO 8601 timestamp") from error


def validate_status(
    status: Any,
    *,
    run_id: str,
    agent_id: str,
    status_path: str,
) -> dict[str, Any]:
    if not isinstance(status, dict):
        raise PublishError("status JSON must be an object")
    if type(status.get("schema_version")) is not int or status["schema_version"] != 1:
        raise PublishError("status schema_version must be 1")
    if status.get("run_id") != run_id or status.get("agent_id") != agent_id:
        raise PublishError("status run_id and agent_id must match the command")
    for field in ("worker_id", "worker_name", "task_id"):
        if not isinstance(status.get(field), str) or not status[field].strip():
            raise PublishError(f"status {field} must be a non-empty string")
    if not isinstance(status.get("status"), str) or status["status"] not in STATUSES:
        raise PublishError(f"status must be one of: {', '.join(sorted(STATUSES))}")
    revision = status.get("revision")
    if isinstance(revision, bool) or not isinstance(revision, int) or revision < 1:
        raise PublishError("status revision must be a positive integer")
    for field in ("started_at_utc", "updated_at_utc", "sign_in_at_utc"):
        validate_timestamp(status.get(field), field)
    if status.get("prompt_path") != status_path.replace("/status.json", "/prompt.md"):
        raise PublishError("prompt_path must identify this agent's prompt.md")
    prompt_sha256 = status.get("prompt_sha256")
    if not isinstance(prompt_sha256, str) or not SHA256.fullmatch(prompt_sha256):
        raise PublishError("prompt_sha256 must be a lowercase SHA-256 hex digest")

    profile = status.get("agent_profile")
    if not isinstance(profile, dict):
        raise PublishError("agent_profile must be an object")
    for field in (
        "harness",
        "agent_definition",
        "model_id",
        "reasoning_effort",
        "context_tier",
        "context_window_tokens",
        "context_usage_tokens",
    ):
        if field not in profile:
            raise PublishError(f"agent_profile must include {field}; use null if unknown")

    git_state = status.get("git")
    if not isinstance(git_state, dict):
        raise PublishError("git must be an object")
    for field in (
        "remote_name",
        "repository",
        "implementation_branch",
        "worktree_path",
        "base_ref",
        "base_sha",
        "worktree_head_sha_at_sign_in",
    ):
        if not isinstance(git_state.get(field), str) or not git_state[field].strip():
            raise PublishError(f"git.{field} must be a non-empty string")
    edit_scope = git_state.get("edit_scope")
    if (
        not isinstance(edit_scope, list)
        or not edit_scope
        or any(not isinstance(path, str) or not path.strip() for path in edit_scope)
    ):
        raise PublishError("git.edit_scope must be a non-empty list of paths")

    sign_out = status.get("sign_out")
    if not isinstance(sign_out, dict):
        raise PublishError("sign_out must be an object")
    for field in (
        "at_utc",
        "implementation_commit_sha",
        "summary",
        "checks",
        "next_action",
    ):
        if field not in sign_out:
            raise PublishError(f"sign_out must include {field}")
    if sign_out["at_utc"] is not None:
        validate_timestamp(sign_out["at_utc"], "sign_out.at_utc")
    if status["status"] in TERMINAL_STATUSES and sign_out["at_utc"] is None:
        raise PublishError(
            f"{status['status']} requires sign_out.at_utc because the agent stopped editing"
        )
    if not isinstance(sign_out["checks"], list):
        raise PublishError("sign_out.checks must be a list")
    return status


def canonical_json(value: Dict[str, Any]) -> bytes:
    serialized = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)
    return (serialized + "\n").encode("utf-8")


def read_remote_blob(
    repository: Path,
    commit: str,
    path: str,
) -> Optional[bytes]:
    tree_paths = run_git(
        repository,
        "ls-tree",
        "-r",
        "--name-only",
        commit,
        "--",
        path,
    )
    if path not in tree_paths.stdout.decode("utf-8", errors="strict").splitlines():
        return None
    return run_git(repository, "cat-file", "blob", f"{commit}:{path}").stdout


def is_ancestor(repository: Path, ancestor: str, descendant: str) -> bool:
    result = run_git(
        repository,
        "merge-base",
        "--is-ancestor",
        ancestor,
        descendant,
        check=False,
    )
    if result.returncode == 0:
        return True
    if result.returncode == 1:
        return False
    error = redact(result.stderr.decode("utf-8", errors="replace").strip())
    raise PublishError(f"could not verify Git ancestry: {error}")


def fetch_main(repository: Path) -> str:
    temporary_ref = f"refs/agent-sync/fetch/{secrets.token_hex(16)}"
    try:
        run_git(
            repository,
            "fetch",
            "--no-tags",
            "--no-write-fetch-head",
            "origin",
            f"{MAIN_REF}:{temporary_ref}",
        )
        return text_output(
            run_git(
                repository,
                "rev-parse",
                "--verify",
                f"{temporary_ref}^{{commit}}",
            )
        )
    finally:
        exists = run_git(
            repository, "show-ref", "--verify", "--quiet", temporary_ref, check=False
        )
        if exists.returncode == 0:
            run_git(repository, "update-ref", "-d", temporary_ref)
        elif exists.returncode != 1:
            raise PublishError("could not verify temporary main fetch ref for cleanup")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )


def read_main_owner(
    repository: Path, base: str, repository_id: str
) -> Optional[Dict[str, Any]]:
    content = read_remote_blob(repository, base, MAIN_OWNERSHIP_PATH)
    if content is None:
        return None
    try:
        record = json.loads(content)
    except json.JSONDecodeError as error:
        raise PublishError("remote main ownership JSON is invalid") from error
    if not isinstance(record, dict) or type(record.get("schema_version")) is not int or record["schema_version"] != 1:
        raise PublishError("remote main ownership schema_version must be 1")
    revision = record.get("revision")
    if type(revision) is not int or revision < 1:
        raise PublishError("remote main ownership revision is invalid")
    if record.get("repository") != repository_id or record.get("ref") != MAIN_REF:
        raise PublishError("remote main ownership repository/ref does not match")
    if record.get("state") not in ("OWNED", "FREE"):
        raise PublishError("remote main ownership state is invalid")
    owner = record.get("owner")
    sign_out = record.get("sign_out")
    if not isinstance(owner, dict) or not isinstance(sign_out, dict):
        raise PublishError("remote main ownership owner/sign_out is invalid")
    if (
        not isinstance(owner.get("run_id"), str)
        or not SAFE_ID.fullmatch(owner["run_id"])
        or not isinstance(owner.get("agent_id"), str)
        or not SAFE_ID.fullmatch(owner["agent_id"])
        or owner.get("operation") not in ("STATUS", "MERGE")
        or not isinstance(owner.get("token"), str)
        or not owner["token"]
        or not isinstance(owner.get("start_main_sha"), str)
        or not re.fullmatch(r"[0-9a-f]{40}", owner["start_main_sha"])
    ):
        raise PublishError("remote main ownership identity is invalid")
    validate_timestamp(owner.get("signed_in_at_utc"), "owner.signed_in_at_utc")
    if record["state"] == "OWNED":
        if (
            sign_out.get("at_utc") is not None
            or sign_out.get("result_commit_sha") is not None
            or sign_out.get("outcome") is not None
        ):
            raise PublishError("an active main owner cannot be signed out")
    else:
        validate_timestamp(sign_out.get("at_utc"), "sign_out.at_utc")
        outcome = sign_out.get("outcome")
        result_sha = sign_out.get("result_commit_sha")
        if outcome in ("PUBLISHED", "MERGED"):
            if (
                not isinstance(result_sha, str)
                or not re.fullmatch(r"[0-9a-f]{40}", result_sha)
                or result_sha == owner["start_main_sha"]
                or not is_ancestor(repository, owner["start_main_sha"], result_sha)
                or not is_ancestor(repository, result_sha, base)
            ):
                raise PublishError("main sign-out result commit is not verified")
        elif outcome in ("FAILED", "UNCHANGED", "QUEUED"):
            if result_sha is not None:
                raise PublishError("main sign-out outcome cannot have a result SHA")
        else:
            raise PublishError("main sign-out outcome is invalid")
    return record


def create_metadata_commit(
    repository: Path,
    base: str,
    changed_paths: List[tuple[str, bytes]],
    message: str,
    env: Dict[str, str],
) -> str:
    run_git(repository, "read-tree", base, env=env)
    for path, content in changed_paths:
        blob = text_output(
            run_git(repository, "hash-object", "-w", "--stdin", input_data=content)
        )
        run_git(
            repository,
            "update-index",
            "--add",
            "--cacheinfo",
            f"100644,{blob},{path}",
            env=env,
        )
    tree = text_output(run_git(repository, "write-tree", env=env))
    return text_output(
        run_git(repository, "commit-tree", tree, "-p", base, "-m", message)
    )


def push_metadata_commit(
    repository: Path, base: str, commit: str
) -> Optional[str]:
    push = run_git(
        repository,
        "push",
        "--porcelain",
        "origin",
        f"{commit}:{MAIN_REF}",
        check=False,
    )
    for verification in range(3):
        try:
            remote_tip = fetch_main(repository)
            break
        except PublishError as error:
            if verification == 2:
                raise UnverifiedPushError(commit) from error
    if is_ancestor(repository, commit, remote_tip):
        return remote_tip
    if remote_tip != base and is_ancestor(repository, base, remote_tip):
        return None
    push_error = redact(push.stderr.decode("utf-8", errors="replace").strip())
    raise PublishError(
        "status-only push to refs/heads/main was rejected. Confirm that origin "
        "permits docs/agent-sync metadata commits; no force-push or PR "
        f"fallback was attempted. Remote response: {push_error}"
    )


def check_main_worktree(repository: Path, worktree_path: Optional[Path]) -> None:
    if worktree_path is None:
        return
    worktree = worktree_path.resolve()
    if text_output(
        run_git(worktree, "symbolic-ref", "--quiet", "--short", "HEAD")
    ) != "main":
        raise PublishError("the specified main checkout is not attached to main")
    if run_git(worktree, "status", "--porcelain").stdout:
        raise PublishError("the specified main checkout has uncommitted changes")
    if text_output(run_git(worktree, "remote", "get-url", "origin")) != text_output(
        run_git(repository, "remote", "get-url", "origin")
    ):
        raise PublishError("the specified main checkout has a different origin")


def acquire_main(
    *,
    repository: Path,
    repository_id: str,
    run_id: str,
    agent_id: str,
    operation: str,
    runtime_agent_id: Optional[str],
    worktree_path: Optional[Path],
    max_attempts: int,
    wait_seconds: float,
) -> Dict[str, Any]:
    if (
        not SAFE_ID.fullmatch(run_id)
        or not SAFE_ID.fullmatch(agent_id)
        or not isinstance(repository_id, str)
        or not repository_id.strip()
        or operation not in ("STATUS", "MERGE")
    ):
        raise PublishError("main owner run, agent, repository, or operation is invalid")
    if not 0 <= wait_seconds <= 120:
        raise PublishError("main ownership wait must be between 0 and 120 seconds")
    repository = repository.resolve()
    check_main_worktree(repository, worktree_path)
    token = secrets.token_hex(16)
    deadline = time.monotonic() + wait_seconds
    with tempfile.TemporaryDirectory(prefix="ralph-main-owner-index-") as temporary:
        env = os.environ.copy()
        env["GIT_INDEX_FILE"] = str(Path(temporary) / "index")
        attempts = 0
        while attempts < max_attempts:
            base = fetch_main(repository)
            current = read_main_owner(repository, base, repository_id)
            if current is not None and current["state"] == "OWNED":
                owner = current["owner"]
                if time.monotonic() >= deadline:
                    raise PublishError(
                        "main is reserved by "
                        f"{owner['run_id']}/{owner['agent_id']} for "
                        f"{owner['operation']}; wait for its verified sign out"
                    )
                time.sleep(min(1, max(0, deadline - time.monotonic())))
                continue
            attempts += 1
            record = {
                "schema_version": 1,
                "revision": 1 if current is None else current["revision"] + 1,
                "repository": repository_id,
                "ref": MAIN_REF,
                "state": "OWNED",
                "owner": {
                    "run_id": run_id,
                    "agent_id": agent_id,
                    "runtime_agent_id": runtime_agent_id,
                    "operation": operation,
                    "worktree_path": (
                        str(worktree_path.resolve()) if worktree_path else None
                    ),
                    "start_main_sha": base,
                    "signed_in_at_utc": utc_now(),
                    "token": token,
                },
                "sign_out": {
                    "at_utc": None,
                    "result_commit_sha": None,
                    "outcome": None,
                },
            }
            commit = create_metadata_commit(
                repository,
                base,
                [(MAIN_OWNERSHIP_PATH, canonical_json(record))],
                f"agent-sync(main): reserve {operation} for {run_id}/{agent_id}",
                env,
            )
            remote_tip = push_metadata_commit(repository, base, commit)
            if remote_tip is None:
                continue
            confirmed = read_main_owner(repository, remote_tip, repository_id)
            if (
                confirmed is None
                or confirmed["state"] != "OWNED"
                or confirmed["owner"]["token"] != token
            ):
                raise PublishError("main reservation changed before it could be verified")
            return {
                "result": "ACQUIRED",
                "token": token,
                "commit_sha": commit,
                "origin_main_sha": remote_tip,
                "revision": record["revision"],
            }
    raise PublishError(
        "origin/main kept advancing during main reservation; reread the owner "
        "before retrying"
    )


def release_main(
    *,
    repository: Path,
    repository_id: str,
    run_id: str,
    agent_id: str,
    token: str,
    result_commit_sha: Optional[str],
    outcome: str,
    max_attempts: int,
) -> Dict[str, Any]:
    if not SAFE_ID.fullmatch(run_id) or not SAFE_ID.fullmatch(agent_id) or not token:
        raise PublishError("main release owner identity/token is invalid")
    if outcome not in ("PUBLISHED", "FAILED", "UNCHANGED", "MERGED", "QUEUED"):
        raise PublishError("main release outcome is invalid")
    if outcome in ("PUBLISHED", "MERGED") and result_commit_sha is None:
        raise PublishError("a published status or merged branch requires its result SHA")
    if outcome in ("FAILED", "UNCHANGED", "QUEUED") and result_commit_sha is not None:
        raise PublishError("this main release outcome cannot include a result SHA")
    if result_commit_sha is not None and not re.fullmatch(
        r"[0-9a-f]{40}", result_commit_sha
    ):
        raise PublishError("main release result commit must be a full SHA")
    repository = repository.resolve()
    with tempfile.TemporaryDirectory(prefix="ralph-main-owner-index-") as temporary:
        env = os.environ.copy()
        env["GIT_INDEX_FILE"] = str(Path(temporary) / "index")
        for _ in range(max_attempts):
            base = fetch_main(repository)
            current = read_main_owner(repository, base, repository_id)
            if current is None:
                raise PublishError("main ownership record is missing; cannot release")
            owner = current["owner"]
            if (
                owner["run_id"] != run_id
                or owner["agent_id"] != agent_id
                or owner["token"] != token
            ):
                raise PublishError("another agent owns main; foreign release refused")
            if current["state"] == "FREE":
                if (
                    current["sign_out"]["outcome"] == outcome
                    and current["sign_out"]["result_commit_sha"] == result_commit_sha
                ):
                    return {
                        "result": "ALREADY_RELEASED",
                        "commit_sha": None,
                        "origin_main_sha": base,
                        "revision": current["revision"],
                    }
                raise PublishError("main was released with a different outcome")
            if result_commit_sha is not None:
                start_sha = owner["start_main_sha"]
                if (
                    result_commit_sha == start_sha
                    or not is_ancestor(repository, start_sha, result_commit_sha)
                    or not is_ancestor(repository, result_commit_sha, base)
                ):
                    raise PublishError(
                        "main release result commit must follow sign-in on origin/main"
                    )
            released = {
                **current,
                "revision": current["revision"] + 1,
                "state": "FREE",
                "sign_out": {
                    "at_utc": utc_now(),
                    "result_commit_sha": result_commit_sha,
                    "outcome": outcome,
                },
            }
            commit = create_metadata_commit(
                repository,
                base,
                [(MAIN_OWNERSHIP_PATH, canonical_json(released))],
                f"agent-sync(main): release {owner['operation']} for {run_id}/{agent_id}",
                env,
            )
            remote_tip = push_metadata_commit(repository, base, commit)
            if remote_tip is not None:
                return {
                    "result": "RELEASED",
                    "commit_sha": commit,
                    "origin_main_sha": remote_tip,
                    "revision": released["revision"],
                }
    raise PublishError(
        "origin/main kept advancing during main release; main remains reserved"
    )


def _publish_status(
    *,
    repository: Path,
    run_id: str,
    agent_id: str,
    status: Dict[str, Any],
    prompt_bytes: Optional[bytes],
    max_attempts: int,
    lease_token: str,
) -> Dict[str, Any]:
    status_path = f"docs/agent-sync/runs/{run_id}/agents/{agent_id}/status.json"
    prompt_path = status_path[:-len("status.json")] + "prompt.md"
    status_bytes = canonical_json(status)
    with tempfile.TemporaryDirectory(prefix="ralph-agent-sync-index-") as temporary:
        env = os.environ.copy()
        env["GIT_INDEX_FILE"] = str(Path(temporary) / "index")

        for attempt in range(1, max_attempts + 1):
            base = fetch_main(repository)
            owner = read_main_owner(repository, base, status["git"]["repository"])
            if (
                owner is None
                or owner["state"] != "OWNED"
                or owner["owner"]["token"] != lease_token
                or owner["owner"]["run_id"] != run_id
                or owner["owner"]["agent_id"] != agent_id
                or owner["owner"]["operation"] != "STATUS"
            ):
                raise PublishError("main ownership changed before status publication")
            previous_status_bytes = read_remote_blob(repository, base, status_path)
            previous_prompt_bytes = read_remote_blob(repository, base, prompt_path)

            if previous_status_bytes is None:
                if status["revision"] != 1:
                    raise PublishError("the first agent status update must use revision 1")
            else:
                try:
                    previous_status = json.loads(previous_status_bytes)
                except json.JSONDecodeError as error:
                    raise PublishError("the current remote status JSON is invalid") from error
                previous_revision = previous_status.get("revision")
                if (
                    isinstance(previous_revision, bool)
                    or not isinstance(previous_revision, int)
                    or previous_revision < 1
                ):
                    raise PublishError("the current remote status revision is invalid")
                if status["revision"] == previous_revision:
                    if previous_status == status:
                        return {
                            "result": "ALREADY_CURRENT",
                            "commit_sha": None,
                            "origin_main_sha": base,
                            "status_path": status_path,
                        }
                    raise PublishError(
                        "status revision is already used; refresh the remote status "
                        "and increment revision before publishing"
                    )
                if status["revision"] != previous_revision + 1:
                    raise PublishError(
                        "status revision must increment the current remote revision "
                        "by exactly one"
                    )

            if previous_prompt_bytes is None and prompt_bytes is None:
                raise PublishError(
                    "the first sign-in must publish prompt.md with --prompt-file"
                )
            if (
                previous_prompt_bytes is not None
                and prompt_bytes is not None
                and prompt_bytes != previous_prompt_bytes
            ):
                raise PublishError("prompt.md is immutable after sign-in")
            current_prompt = prompt_bytes if prompt_bytes is not None else previous_prompt_bytes
            if hashlib.sha256(current_prompt).hexdigest() != status["prompt_sha256"]:
                raise PublishError("prompt_sha256 does not match the stored prompt.md")

            changed_paths = [(status_path, status_bytes)]
            if previous_prompt_bytes is None:
                changed_paths.append((prompt_path, current_prompt))
            message = (
                f"agent-sync({agent_id}): {status['status']} "
                f"{run_id} revision {status['revision']}"
            )
            commit = create_metadata_commit(
                repository, base, changed_paths, message, env
            )
            try:
                remote_tip = push_metadata_commit(repository, base, commit)
            except UnverifiedPushError as error:
                try:
                    remote_tip = fetch_main(repository)
                except PublishError as recovery_error:
                    raise UnverifiedPushError(commit) from recovery_error
                if not is_ancestor(repository, commit, remote_tip):
                    raise PublishError(
                        f"status commit {commit} was not applied to origin/main"
                    ) from error
            if remote_tip is not None:
                return {
                    "result": "PUBLISHED",
                    "commit_sha": commit,
                    "origin_main_sha": remote_tip,
                    "status_path": status_path,
                    "revision": status["revision"],
                    "attempt": attempt,
                }

    raise PublishError(
        f"origin/main kept advancing during {max_attempts} status publish attempts; "
        "refresh other agent records and retry with the next revision"
    )


def publish(
    *,
    repository: Path,
    run_id: str,
    agent_id: str,
    status_file: Optional[Path],
    prompt_file: Optional[Path],
    max_attempts: int,
    wait_seconds: float = DEFAULT_WAIT_SECONDS,
) -> Dict[str, Any]:
    if not SAFE_ID.fullmatch(run_id) or not SAFE_ID.fullmatch(agent_id):
        raise PublishError("run-id and agent-id must be safe path components")
    repository = repository.resolve()
    run_git(repository, "rev-parse", "--absolute-git-dir")
    run_git(repository, "remote", "get-url", "origin")
    run_git(repository, "var", "GIT_AUTHOR_IDENT")
    run_git(repository, "var", "GIT_COMMITTER_IDENT")

    status_path = f"docs/agent-sync/runs/{run_id}/agents/{agent_id}/status.json"
    try:
        status_content = (
            sys.stdin.buffer.read() if status_file is None else status_file.read_bytes()
        )
        status = json.loads(status_content)
    except json.JSONDecodeError as error:
        raise PublishError(f"status file is not valid JSON: {error}") from error
    status = validate_status(
        status, run_id=run_id, agent_id=agent_id, status_path=status_path
    )
    if status["git"]["remote_name"] != "origin":
        raise PublishError("status git.remote_name must be origin")
    prompt_bytes = prompt_file.read_bytes() if prompt_file is not None else None
    if prompt_bytes is not None:
        prompt_bytes.decode("utf-8")
        if hashlib.sha256(prompt_bytes).hexdigest() != status["prompt_sha256"]:
            raise PublishError("prompt_sha256 does not match the exact prompt file bytes")

    base = fetch_main(repository)
    previous_status_bytes = read_remote_blob(repository, base, status_path)
    if previous_status_bytes is not None:
        try:
            previous_status = json.loads(previous_status_bytes)
        except json.JSONDecodeError as error:
            raise PublishError("the current remote status JSON is invalid") from error
        if previous_status == status:
            prompt_path = status_path[:-len("status.json")] + "prompt.md"
            previous_prompt = read_remote_blob(repository, base, prompt_path)
            if previous_prompt is None:
                raise PublishError("the current remote prompt.md is missing")
            if prompt_bytes is not None and prompt_bytes != previous_prompt:
                raise PublishError("prompt.md is immutable after sign-in")
            if hashlib.sha256(previous_prompt).hexdigest() != status["prompt_sha256"]:
                raise PublishError("prompt_sha256 does not match the stored prompt.md")
            return {
                "result": "ALREADY_CURRENT",
                "commit_sha": None,
                "origin_main_sha": base,
                "status_path": status_path,
                "revision": status["revision"],
                "main_sign_in_commit_sha": None,
                "main_sign_out_commit_sha": None,
            }

    repository_id = status["git"]["repository"]
    lease = acquire_main(
        repository=repository,
        repository_id=repository_id,
        run_id=run_id,
        agent_id=agent_id,
        operation="STATUS",
        runtime_agent_id=status["agent_profile"].get("runtime_agent_id"),
        worktree_path=None,
        max_attempts=max_attempts,
        wait_seconds=wait_seconds,
    )
    try:
        result = _publish_status(
            repository=repository,
            run_id=run_id,
            agent_id=agent_id,
            status=status,
            prompt_bytes=prompt_bytes,
            max_attempts=max_attempts,
            lease_token=lease["token"],
        )
    except UnverifiedPushError as error:
        raise PublishError(
            f"status push {error.commit_sha} is unverified; main remains reserved "
            "until the owner can reconcile and sign out"
        ) from error
    except (OSError, UnicodeError, PublishError) as publication_error:
        try:
            release_main(
                repository=repository,
                repository_id=repository_id,
                run_id=run_id,
                agent_id=agent_id,
                token=lease["token"],
                result_commit_sha=None,
                outcome="FAILED",
                max_attempts=max_attempts,
            )
        except (OSError, UnicodeError, PublishError) as release_error:
            raise PublishError(
                f"status publication failed: {publication_error}; "
                f"main release also failed: {release_error}"
            ) from release_error
        raise
    try:
        release = release_main(
            repository=repository,
            repository_id=repository_id,
            run_id=run_id,
            agent_id=agent_id,
            token=lease["token"],
            result_commit_sha=result["commit_sha"],
            outcome="PUBLISHED" if result["commit_sha"] else "UNCHANGED",
            max_attempts=max_attempts,
        )
    except (OSError, UnicodeError, PublishError) as error:
        raise PublishError(
            f"status commit {result['commit_sha']} succeeded but main release "
            f"failed: {error}"
        ) from error
    result["main_sign_in_commit_sha"] = lease["commit_sha"]
    result["main_sign_out_commit_sha"] = release["commit_sha"]
    result["origin_main_sha"] = release["origin_main_sha"]
    return result


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Commit only one agent's docs/agent-sync status snapshot directly "
            "to origin/main without checking out a branch or creating a worktree."
        )
    )
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--agent-id", required=True)
    parser.add_argument(
        "--status-file",
        help="Path to the status JSON, or - to read it from stdin.",
    )
    parser.add_argument(
        "--prompt-file",
        type=Path,
        help="Required for first sign-in; the prompt is immutable after publication.",
    )
    parser.add_argument("--max-attempts", type=int, default=MAX_ATTEMPTS)
    parser.add_argument("--wait-seconds", type=float, default=DEFAULT_WAIT_SECONDS)
    parser.add_argument("--main-action", choices=("acquire", "release"))
    parser.add_argument("--repository-id")
    parser.add_argument("--operation", choices=("STATUS", "MERGE"), default="MERGE")
    parser.add_argument("--runtime-agent-id")
    parser.add_argument("--main-worktree", type=Path)
    parser.add_argument("--main-token")
    parser.add_argument("--result-commit-sha")
    parser.add_argument(
        "--outcome", choices=("PUBLISHED", "FAILED", "UNCHANGED", "MERGED", "QUEUED")
    )
    args = parser.parse_args(argv)
    if not 1 <= args.max_attempts <= 10:
        parser.error("--max-attempts must be between 1 and 10")
    if not 0 <= args.wait_seconds <= 120:
        parser.error("--wait-seconds must be between 0 and 120")
    if args.main_action:
        if not args.repository_id:
            parser.error("--repository-id is required for a main action")
        if args.status_file or args.prompt_file:
            parser.error("main actions do not accept status or prompt files")
        if args.main_action == "release" and (not args.main_token or not args.outcome):
            parser.error("main release requires --main-token and --outcome")
    elif not args.status_file:
        parser.error("--status-file is required for status publication")
    return args


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        if args.main_action:
            run_git(args.repository, "var", "GIT_AUTHOR_IDENT")
            run_git(args.repository, "var", "GIT_COMMITTER_IDENT")
        if args.main_action == "acquire":
            result = acquire_main(
                repository=args.repository,
                repository_id=args.repository_id,
                run_id=args.run_id,
                agent_id=args.agent_id,
                operation=args.operation,
                runtime_agent_id=args.runtime_agent_id,
                worktree_path=args.main_worktree,
                max_attempts=args.max_attempts,
                wait_seconds=args.wait_seconds,
            )
        elif args.main_action == "release":
            result = release_main(
                repository=args.repository,
                repository_id=args.repository_id,
                run_id=args.run_id,
                agent_id=args.agent_id,
                token=args.main_token,
                result_commit_sha=args.result_commit_sha,
                outcome=args.outcome,
                max_attempts=args.max_attempts,
            )
        else:
            result = publish(
                repository=args.repository,
                run_id=args.run_id,
                agent_id=args.agent_id,
                status_file=(
                    None if args.status_file == "-" else Path(args.status_file)
                ),
                prompt_file=args.prompt_file,
                max_attempts=args.max_attempts,
                wait_seconds=args.wait_seconds,
            )
    except (OSError, UnicodeError, PublishError) as error:
        print(f"agent-sync publish failed: {redact(str(error))}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
