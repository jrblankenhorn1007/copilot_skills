#!/usr/bin/env python3
"""Hardware-aware admission control for agents sharing one local machine."""

from __future__ import annotations

import argparse
import json
import math
import os
import platform
import re
import secrets
import stat
import subprocess
import sys
import tempfile
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple

try:
    import fcntl
except ImportError:
    fcntl = None


SCHEMA_VERSION = 1
MAX_AGENTS = 4
RAM_RESERVE_GIB = 4.0
RAM_PER_AGENT_GIB = 2.0
CPU_CORES_PER_AGENT = 2
DEGRADED_AVAILABLE_RAM_GIB = 3.0
CRITICAL_AVAILABLE_RAM_GIB = 1.5
DEGRADED_CPU_LOAD_RATIO = 0.85
ACTIVE_LEASE = timedelta(minutes=30)
RESERVATION_LEASE = timedelta(minutes=5)
OBSERVATION_LEASE = timedelta(minutes=3)
GIB = 1024**3
ROLES = {"agent", "orchestrator", "worker", "subagent"}


class ResourceManagerError(Exception):
    """A user-actionable resource-manager failure."""


class AdmissionDenied(ResourceManagerError):
    """An agent cannot acquire a slot under the current policy."""


class MetricsUnavailable(ResourceManagerError):
    """The host's resource usage cannot be measured safely."""


class RegistryError(ResourceManagerError):
    """The shared registry is unavailable or invalid."""


@dataclass(frozen=True)
class HostMetrics:
    total_memory_bytes: int
    available_memory_bytes: int
    cpu_cores: int
    load_1m: float
    platform_name: str = "test"


@dataclass(frozen=True)
class Capacity:
    max_agents: int
    base_agents: int
    ram_agents: int
    cpu_agents: int
    available_ram_gib: float
    load_1m: float
    reasons: Tuple[str, ...]


def default_registry_dir() -> Path:
    configured = os.environ.get("COPILOT_AGENT_RESOURCE_MANAGER_DIR")
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".copilot" / "agent-resource-manager"


def _run(command: List[str]) -> str:
    try:
        completed = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise MetricsUnavailable(
            f"cannot read host resource metrics with {command[0]!r}"
        ) from exc
    return completed.stdout


def parse_macos_free_percentage(output: str) -> float:
    match = re.search(
        r"System-wide memory free percentage:\s*([0-9]+(?:\.[0-9]+)?)%",
        output,
        re.IGNORECASE,
    )
    if match is None:
        raise MetricsUnavailable("macOS memory-pressure output was not recognized")
    percentage = float(match.group(1))
    if not 0 <= percentage <= 100:
        raise MetricsUnavailable("macOS reported an invalid free-memory percentage")
    return percentage


def parse_linux_memory_info(contents: str) -> Tuple[int, int]:
    values: Dict[str, int] = {}
    for line in contents.splitlines():
        match = re.match(r"^(MemTotal|MemAvailable):\s+([0-9]+)\s+kB$", line)
        if match is not None:
            values[match.group(1)] = int(match.group(2)) * 1024
    if "MemTotal" not in values or "MemAvailable" not in values:
        raise MetricsUnavailable("Linux /proc/meminfo lacks MemTotal or MemAvailable")
    if values["MemTotal"] <= 0 or values["MemAvailable"] > values["MemTotal"]:
        raise MetricsUnavailable("Linux reported invalid memory values")
    return values["MemTotal"], values["MemAvailable"]


def read_host_metrics() -> HostMetrics:
    system = platform.system()
    if system == "Darwin":
        try:
            total_memory = int(_run(["sysctl", "-n", "hw.memsize"]).strip())
        except ValueError as exc:
            raise MetricsUnavailable("macOS reported an invalid physical memory size") from exc
        free_percentage = parse_macos_free_percentage(_run(["memory_pressure"]))
        available_memory = int(total_memory * free_percentage / 100)
    elif system == "Linux":
        try:
            meminfo = Path("/proc/meminfo").read_text(encoding="utf-8")
        except OSError as exc:
            raise MetricsUnavailable("cannot read Linux /proc/meminfo") from exc
        total_memory, available_memory = parse_linux_memory_info(meminfo)
    else:
        raise MetricsUnavailable(
            f"resource metrics are supported on macOS and Linux, not {system}"
        )

    cpu_cores = os.cpu_count()
    if cpu_cores is None or cpu_cores < 1:
        raise MetricsUnavailable("cannot determine the host's logical CPU count")
    try:
        load_1m = os.getloadavg()[0]
    except (AttributeError, OSError) as exc:
        raise MetricsUnavailable("cannot read the host's one-minute load average") from exc
    return HostMetrics(
        total_memory_bytes=total_memory,
        available_memory_bytes=available_memory,
        cpu_cores=cpu_cores,
        load_1m=load_1m,
        platform_name=system,
    )


def calculate_capacity(metrics: HostMetrics) -> Capacity:
    if (
        metrics.total_memory_bytes <= 0
        or metrics.available_memory_bytes < 0
        or metrics.available_memory_bytes > metrics.total_memory_bytes
        or metrics.cpu_cores < 1
        or not math.isfinite(metrics.load_1m)
        or metrics.load_1m < 0
    ):
        raise MetricsUnavailable("host resource metrics contain invalid values")

    total_ram_gib = metrics.total_memory_bytes / GIB
    available_ram_gib = metrics.available_memory_bytes / GIB
    ram_agents = min(
        MAX_AGENTS,
        max(
            1,
            math.floor(
                max(0.0, total_ram_gib - RAM_RESERVE_GIB) / RAM_PER_AGENT_GIB
            ),
        ),
    )
    cpu_agents = min(
        MAX_AGENTS,
        max(1, metrics.cpu_cores // CPU_CORES_PER_AGENT),
    )
    base_agents = min(MAX_AGENTS, ram_agents, cpu_agents)
    max_agents = base_agents
    reasons: List[str] = []

    if (
        available_ram_gib <= CRITICAL_AVAILABLE_RAM_GIB
        or metrics.load_1m >= metrics.cpu_cores
    ):
        max_agents = 0
        if available_ram_gib <= CRITICAL_AVAILABLE_RAM_GIB:
            reasons.append("available memory is at or below the critical threshold")
        if metrics.load_1m >= metrics.cpu_cores:
            reasons.append("one-minute system load is at or above logical CPU count")
    elif (
        available_ram_gib < DEGRADED_AVAILABLE_RAM_GIB
        or metrics.load_1m >= metrics.cpu_cores * DEGRADED_CPU_LOAD_RATIO
    ):
        max_agents = max(1, base_agents - 1)
        if available_ram_gib < DEGRADED_AVAILABLE_RAM_GIB:
            reasons.append("available memory is below the degraded threshold")
        if metrics.load_1m >= metrics.cpu_cores * DEGRADED_CPU_LOAD_RATIO:
            reasons.append("one-minute system load is high")

    return Capacity(
        max_agents=max_agents,
        base_agents=base_agents,
        ram_agents=ram_agents,
        cpu_agents=cpu_agents,
        available_ram_gib=available_ram_gib,
        load_1m=metrics.load_1m,
        reasons=tuple(reasons),
    )


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _format_time(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )


def _parse_time(value: Any, field: str) -> datetime:
    if not isinstance(value, str):
        raise RegistryError(f"registry field {field!r} must be an ISO timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise RegistryError(f"registry field {field!r} is not an ISO timestamp") from exc
    if parsed.tzinfo is None:
        raise RegistryError(f"registry field {field!r} must include a timezone")
    return parsed.astimezone(timezone.utc)


def _validate_id(value: Optional[str], field: str) -> Optional[str]:
    if value is None:
        return None
    if not isinstance(value, str):
        raise RegistryError(f"{field} must be a string")
    normalized = value.strip()
    if not normalized or len(normalized) > 256:
        raise RegistryError(f"{field} must contain 1 to 256 characters")
    return normalized


def _unique_ids(values: Iterable[str]) -> List[str]:
    result = set()
    for value in values:
        normalized = _validate_id(value, "observed agent id")
        if normalized is None:
            raise RegistryError("observed agent id cannot be empty")
        result.add(normalized)
    return sorted(result)


def _empty_state() -> Dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "updated_at_utc": None,
        "agents": {},
        "observed_sessions": {"observed_at_utc": None, "agent_ids": []},
    }


def _validate_state(state: Any) -> Dict[str, Any]:
    if not isinstance(state, dict) or state.get("schema_version") != SCHEMA_VERSION:
        raise RegistryError("registry has an unsupported or invalid schema")
    agents = state.get("agents")
    observed = state.get("observed_sessions")
    if not isinstance(agents, dict) or not isinstance(observed, dict):
        raise RegistryError("registry is missing its agents or observed-session map")
    if not isinstance(observed.get("agent_ids"), list):
        raise RegistryError("registry observed-session ids are invalid")
    for session_id in observed["agent_ids"]:
        if _validate_id(session_id, "observed agent id") != session_id:
            raise RegistryError("registry contains an invalid observed agent id")
    for agent_id, record in agents.items():
        status = record.get("status") if isinstance(record, dict) else None
        role = record.get("role") if isinstance(record, dict) else None
        if (
            not isinstance(agent_id, str)
            or not isinstance(record, dict)
            or record.get("agent_id") != agent_id
            or not isinstance(status, str)
            or status not in {"active", "reserved"}
            or not isinstance(role, str)
            or role not in ROLES
        ):
            raise RegistryError("registry contains an invalid agent entry")
        for field in ("runtime_id", "parent_id"):
            value = record.get(field)
            if value is not None and _validate_id(value, field) != value:
                raise RegistryError(f"registry agent field {field!r} is invalid")
        reservation_id = record.get("reservation_id")
        if record["status"] == "reserved" and (
            not isinstance(reservation_id, str) or not reservation_id
        ):
            raise RegistryError("registry reservation id is invalid")
        if reservation_id is not None and (
            _validate_id(reservation_id, "reservation id") != reservation_id
        ):
            raise RegistryError("registry reservation id is invalid")
        _parse_time(record.get("expires_at_utc"), "expires_at_utc")
    observed_at = observed.get("observed_at_utc")
    if observed_at is not None:
        _parse_time(observed_at, "observed_at_utc")
    return state


def _ensure_registry_dir(registry_dir: Path) -> Path:
    try:
        directory = registry_dir.expanduser().resolve()
        directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        if not directory.is_dir():
            raise RegistryError(f"shared registry path is not a directory: {directory}")
        directory_mode = stat.S_IMODE(directory.stat().st_mode)
    except OSError as exc:
        raise RegistryError(
            f"cannot prepare shared registry directory {registry_dir}"
        ) from exc
    except RuntimeError as exc:
        raise RegistryError("cannot resolve the shared registry directory") from exc
    if os.name == "posix" and directory_mode & 0o077:
        raise RegistryError("shared registry directory must be accessible only by its owner")
    return directory


def _ensure_unique_identity(
    state: Dict[str, Any], agent_id: str, runtime_id: Optional[str]
) -> None:
    identities = {agent_id}
    if runtime_id is not None:
        identities.add(runtime_id)
    for other_id, record in state["agents"].items():
        if other_id == agent_id:
            continue
        other_identities = {other_id}
        if record.get("runtime_id") is not None:
            other_identities.add(record["runtime_id"])
        if identities & other_identities:
            raise RegistryError("agent or runtime id is already bound to another registration")


@contextmanager
def _locked_registry(registry_dir: Path) -> Iterator[Tuple[Path, Path]]:
    if fcntl is None:
        raise RegistryError("atomic registry locking requires macOS or Linux")
    directory = _ensure_registry_dir(registry_dir)
    registry_path = directory / "registry.json"
    lock_path = directory / "registry.lock"
    try:
        descriptor = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
        with os.fdopen(descriptor, "r+") as lock_file:
            os.chmod(lock_path, 0o600)
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            try:
                yield directory, registry_path
            finally:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
    except OSError as exc:
        raise RegistryError("cannot lock the shared local registry") from exc


def _read_state(registry_path: Path) -> Dict[str, Any]:
    if not registry_path.exists():
        return _empty_state()
    try:
        if os.name == "posix" and stat.S_IMODE(registry_path.stat().st_mode) & 0o077:
            raise RegistryError("shared registry file must be accessible only by its owner")
        content = registry_path.read_text(encoding="utf-8")
        return _validate_state(json.loads(content))
    except json.JSONDecodeError as exc:
        raise RegistryError("shared registry JSON is invalid; refusing to reset it") from exc
    except OSError as exc:
        raise RegistryError("cannot read the shared registry") from exc


def _write_state(directory: Path, registry_path: Path, state: Dict[str, Any]) -> None:
    temporary_path: Optional[Path] = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=directory,
            prefix=".registry-",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temporary_path = Path(stream.name)
            json.dump(state, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary_path, 0o600)
        os.replace(temporary_path, registry_path)
    except OSError as exc:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()
        raise RegistryError("cannot atomically write the shared registry") from exc


def _prune_expired(state: Dict[str, Any], now: datetime) -> None:
    expired = [
        agent_id
        for agent_id, record in state["agents"].items()
        if _parse_time(record.get("expires_at_utc"), "expires_at_utc") <= now
    ]
    for agent_id in expired:
        del state["agents"][agent_id]


def _set_observation(
    state: Dict[str, Any], observed_session_ids: Iterable[str], now: datetime
) -> None:
    state["observed_sessions"] = {
        "observed_at_utc": _format_time(now),
        "agent_ids": _unique_ids(observed_session_ids),
    }


def _observation_is_fresh(state: Dict[str, Any], now: datetime) -> bool:
    observed_at = state["observed_sessions"].get("observed_at_utc")
    return observed_at is not None and now - _parse_time(
        observed_at, "observed_at_utc"
    ) <= OBSERVATION_LEASE


def _counts(state: Dict[str, Any], now: datetime) -> Tuple[int, List[str], bool]:
    fresh = _observation_is_fresh(state, now)
    observed = (
        set(state["observed_sessions"]["agent_ids"])
        if fresh
        else set()
    )
    registered_ids = set()
    for agent_id, record in state["agents"].items():
        registered_ids.add(agent_id)
        if record.get("runtime_id") is not None:
            registered_ids.add(record["runtime_id"])
    external = sorted(observed - registered_ids)
    return len(state["agents"]) + len(external), external, fresh


def _status_document(
    registry_path: Path, state: Dict[str, Any], metrics: HostMetrics, now: datetime
) -> Dict[str, Any]:
    capacity = calculate_capacity(metrics)
    agent_count, external_ids, inventory_fresh = _counts(state, now)
    available_slots = max(0, capacity.max_agents - agent_count)
    if not inventory_fresh:
        available_slots = 0
    records = sorted(state["agents"].values(), key=lambda record: record["agent_id"])
    return {
        "registry_path": str(registry_path),
        "hardware": {
            "platform": metrics.platform_name,
            "total_ram_gib": round(metrics.total_memory_bytes / GIB, 2),
            "available_ram_gib": round(capacity.available_ram_gib, 2),
            "logical_cpu_cores": metrics.cpu_cores,
            "load_average_1m": round(metrics.load_1m, 2),
        },
        "capacity": {
            "max_agents": capacity.max_agents,
            "base_agents": capacity.base_agents,
            "ram_agents": capacity.ram_agents,
            "cpu_agents": capacity.cpu_agents,
            "reasons": list(capacity.reasons),
        },
        "inventory_fresh": inventory_fresh,
        "registered_agent_count": sum(
            record["status"] == "active" for record in records
        ),
        "reserved_agent_count": sum(
            record["status"] == "reserved" for record in records
        ),
        "observed_unregistered_agent_ids": external_ids,
        "active_agent_count": agent_count,
        "available_slots": available_slots,
        "can_spawn": inventory_fresh and capacity.max_agents > agent_count,
        "agents": records,
    }


def _save(
    directory: Path, registry_path: Path, state: Dict[str, Any], now: datetime
) -> None:
    state["updated_at_utc"] = _format_time(now)
    _write_state(directory, registry_path, state)


def observe_sessions(
    registry_dir: Path,
    observed_session_ids: Iterable[str],
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    now = now or _utc_now()
    with _locked_registry(registry_dir) as (directory, registry_path):
        state = _read_state(registry_path)
        _prune_expired(state, now)
        _set_observation(state, observed_session_ids, now)
        _save(directory, registry_path, state, now)
        return {
            "registry_path": str(registry_path),
            "observed_at_utc": state["observed_sessions"]["observed_at_utc"],
            "observed_agent_count": len(state["observed_sessions"]["agent_ids"]),
        }


def register_agent(
    registry_dir: Path,
    agent_id: str,
    *,
    role: str,
    runtime_id: Optional[str],
    observed_session_ids: Iterable[str],
    parent_id: Optional[str] = None,
    metrics: Optional[HostMetrics] = None,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    now = now or _utc_now()
    agent_id = _validate_id(agent_id, "agent id") or ""
    runtime_id = _validate_id(runtime_id, "runtime id")
    parent_id = _validate_id(parent_id, "parent id")
    if role not in ROLES:
        raise RegistryError(f"unsupported agent role: {role}")
    metrics = metrics or read_host_metrics()
    capacity = calculate_capacity(metrics)

    with _locked_registry(registry_dir) as (directory, registry_path):
        state = _read_state(registry_path)
        _prune_expired(state, now)
        _set_observation(state, observed_session_ids, now)
        _ensure_unique_identity(state, agent_id, runtime_id)
        existing = state["agents"].get(agent_id)
        if existing is not None:
            if existing["status"] != "active":
                raise AdmissionDenied(
                    "this agent id has a reservation; activate it instead of registering again"
                )
            if existing["role"] != role or existing.get("parent_id") != parent_id:
                raise RegistryError("agent id is already registered with different ownership")
            current_runtime_id = existing.get("runtime_id")
            if current_runtime_id and runtime_id and current_runtime_id != runtime_id:
                raise RegistryError("agent id is already bound to a different runtime session")
            existing["runtime_id"] = runtime_id or current_runtime_id
            existing["heartbeat_at_utc"] = _format_time(now)
            existing["expires_at_utc"] = _format_time(now + ACTIVE_LEASE)
            result = existing
        else:
            current_count, _, _ = _counts(state, now)
            observed_ids = set(state["observed_sessions"]["agent_ids"])
            is_already_running = agent_id in observed_ids or (
                runtime_id is not None and runtime_id in observed_ids
            )
            if not is_already_running and (
                capacity.max_agents == 0 or current_count >= capacity.max_agents
            ):
                raise AdmissionDenied(
                    f"capacity is {capacity.max_agents}; {current_count} agents are already "
                    "active or reserved"
                )
            result = {
                "agent_id": agent_id,
                "runtime_id": runtime_id,
                "role": role,
                "parent_id": parent_id,
                "status": "active",
                "reservation_id": None,
                "started_at_utc": _format_time(now),
                "heartbeat_at_utc": _format_time(now),
                "expires_at_utc": _format_time(now + ACTIVE_LEASE),
            }
            state["agents"][agent_id] = result
        _save(directory, registry_path, state, now)
        return {
            "agent": result,
            "status": _status_document(registry_path, state, metrics, now),
        }


def reserve_agent(
    registry_dir: Path,
    agent_id: str,
    *,
    role: str,
    parent_id: str,
    observed_session_ids: Iterable[str],
    metrics: Optional[HostMetrics] = None,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    now = now or _utc_now()
    agent_id = _validate_id(agent_id, "agent id") or ""
    parent_id = _validate_id(parent_id, "parent id") or ""
    if role not in ROLES:
        raise RegistryError(f"unsupported agent role: {role}")
    metrics = metrics or read_host_metrics()
    capacity = calculate_capacity(metrics)

    with _locked_registry(registry_dir) as (directory, registry_path):
        state = _read_state(registry_path)
        _prune_expired(state, now)
        _set_observation(state, observed_session_ids, now)
        parent = state["agents"].get(parent_id)
        if parent is None or parent["status"] != "active":
            raise AdmissionDenied("parent agent must be registered and active before reserving")
        if agent_id in state["agents"]:
            raise RegistryError(f"agent id is already present: {agent_id}")
        if agent_id in state["observed_sessions"]["agent_ids"]:
            raise RegistryError(f"agent id is already present in the live session inventory")
        _ensure_unique_identity(state, agent_id, None)
        current_count, _, inventory_fresh = _counts(state, now)
        if not inventory_fresh:
            raise AdmissionDenied("fresh live-agent inventory is required before spawning")
        if capacity.max_agents == 0 or current_count >= capacity.max_agents:
            raise AdmissionDenied(
                f"capacity is {capacity.max_agents}; {current_count} agents are already "
                "active or reserved"
            )

        reservation_id = uuid.uuid4().hex
        result = {
            "agent_id": agent_id,
            "runtime_id": None,
            "role": role,
            "parent_id": parent_id,
            "status": "reserved",
            "reservation_id": reservation_id,
            "reserved_at_utc": _format_time(now),
            "heartbeat_at_utc": _format_time(now),
            "expires_at_utc": _format_time(now + RESERVATION_LEASE),
        }
        state["agents"][agent_id] = result
        _save(directory, registry_path, state, now)
        return {
            "agent": result,
            "status": _status_document(registry_path, state, metrics, now),
        }


def activate_agent(
    registry_dir: Path,
    agent_id: str,
    reservation_id: str,
    runtime_id: str,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    now = now or _utc_now()
    agent_id = _validate_id(agent_id, "agent id") or ""
    runtime_id = _validate_id(runtime_id, "runtime id") or ""
    with _locked_registry(registry_dir) as (directory, registry_path):
        state = _read_state(registry_path)
        _prune_expired(state, now)
        record = state["agents"].get(agent_id)
        if record is None or record["status"] != "reserved":
            raise AdmissionDenied("no live reservation exists for this agent")
        if not secrets.compare_digest(record["reservation_id"], reservation_id):
            raise AdmissionDenied("reservation id does not match")
        _ensure_unique_identity(state, agent_id, runtime_id)
        record["runtime_id"] = runtime_id
        record["status"] = "active"
        record["started_at_utc"] = _format_time(now)
        record["heartbeat_at_utc"] = _format_time(now)
        record["expires_at_utc"] = _format_time(now + ACTIVE_LEASE)
        _save(directory, registry_path, state, now)
        return {"agent": record, "registry_path": str(registry_path)}


def heartbeat_agent(
    registry_dir: Path, agent_id: str, now: Optional[datetime] = None
) -> Dict[str, Any]:
    now = now or _utc_now()
    agent_id = _validate_id(agent_id, "agent id") or ""
    with _locked_registry(registry_dir) as (directory, registry_path):
        state = _read_state(registry_path)
        _prune_expired(state, now)
        record = state["agents"].get(agent_id)
        if record is None:
            raise AdmissionDenied("agent has no live registry entry to heartbeat")
        lease = ACTIVE_LEASE if record["status"] == "active" else RESERVATION_LEASE
        record["heartbeat_at_utc"] = _format_time(now)
        record["expires_at_utc"] = _format_time(now + lease)
        _save(directory, registry_path, state, now)
        return {"agent": record, "registry_path": str(registry_path)}


def release_agent(
    registry_dir: Path,
    agent_id: str,
    reservation_id: Optional[str] = None,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    now = now or _utc_now()
    agent_id = _validate_id(agent_id, "agent id") or ""
    with _locked_registry(registry_dir) as (directory, registry_path):
        state = _read_state(registry_path)
        _prune_expired(state, now)
        record = state["agents"].get(agent_id)
        if record is None:
            raise AdmissionDenied("agent has no live registry entry to release")
        if record["status"] == "reserved" and (
            reservation_id is None
            or not secrets.compare_digest(record["reservation_id"], reservation_id)
        ):
            raise AdmissionDenied("reservation id is required to cancel this reservation")
        if record["status"] == "active" and reservation_id is not None:
            raise RegistryError("reservation id cannot be used to release an active agent")
        del state["agents"][agent_id]
        _save(directory, registry_path, state, now)
        return {"released_agent_id": agent_id, "registry_path": str(registry_path)}


def get_status(
    registry_dir: Path,
    *,
    observed_session_ids: Optional[Iterable[str]] = None,
    metrics: Optional[HostMetrics] = None,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    now = now or _utc_now()
    metrics = metrics or read_host_metrics()
    if observed_session_ids is not None:
        observe_sessions(registry_dir, observed_session_ids, now)
    with _locked_registry(registry_dir) as (directory, registry_path):
        state = _read_state(registry_path)
        _prune_expired(state, now)
        _save(directory, registry_path, state, now)
        return _status_document(registry_path, state, metrics, now)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    status = commands.add_parser("status", help="show capacity and registered agents")
    status.add_argument("--observed-session", action="append")

    observe = commands.add_parser("observe", help="record the current live-agent inventory")
    observe.add_argument("--session-id", action="append", required=True)

    register = commands.add_parser("register", help="register the current agent")
    register.add_argument("--agent-id", required=True)
    register.add_argument("--runtime-id")
    register.add_argument("--parent-id")
    register.add_argument("--role", choices=sorted(ROLES), default="agent")
    register.add_argument("--observed-session", action="append", required=True)

    reserve = commands.add_parser("reserve", help="reserve a slot before spawning an agent")
    reserve.add_argument("--agent-id", required=True)
    reserve.add_argument("--parent-id", required=True)
    reserve.add_argument("--role", choices=sorted(ROLES), default="subagent")
    reserve.add_argument("--observed-session", action="append", required=True)

    activate = commands.add_parser("activate", help="claim a parent's reservation")
    activate.add_argument("--agent-id", required=True)
    activate.add_argument("--reservation-id", required=True)
    activate.add_argument("--runtime-id", required=True)

    heartbeat = commands.add_parser("heartbeat", help="extend an agent's local lease")
    heartbeat.add_argument("--agent-id", required=True)

    release = commands.add_parser("release", help="release an agent or cancel a reservation")
    release.add_argument("--agent-id", required=True)
    release.add_argument("--reservation-id")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    registry_dir = default_registry_dir()
    try:
        if args.command == "status":
            result = get_status(
                registry_dir,
                observed_session_ids=args.observed_session,
            )
        elif args.command == "observe":
            result = observe_sessions(registry_dir, args.session_id)
        elif args.command == "register":
            result = register_agent(
                registry_dir,
                args.agent_id,
                role=args.role,
                runtime_id=args.runtime_id,
                parent_id=args.parent_id,
                observed_session_ids=args.observed_session,
            )
        elif args.command == "reserve":
            result = reserve_agent(
                registry_dir,
                args.agent_id,
                role=args.role,
                parent_id=args.parent_id,
                observed_session_ids=args.observed_session,
            )
        elif args.command == "activate":
            result = activate_agent(
                registry_dir,
                args.agent_id,
                args.reservation_id,
                args.runtime_id,
            )
        elif args.command == "heartbeat":
            result = heartbeat_agent(registry_dir, args.agent_id)
        else:
            result = release_agent(
                registry_dir,
                args.agent_id,
                args.reservation_id,
            )
    except ResourceManagerError as exc:
        print(f"resource-manager: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
