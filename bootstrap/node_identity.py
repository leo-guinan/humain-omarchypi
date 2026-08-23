"""First-boot identity primitives for an OmarchyPi node."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import secrets
import tempfile

SCHEMA = "omarchypi.node.v1"
DEFAULT_CAPABILITIES = ["public-pointer", "quickshell-bar", "health"]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def validate_identity(value: object) -> bool:
    if not isinstance(value, dict):
        return False
    if value.get("schema") != SCHEMA:
        return False
    node_id = value.get("node_id")
    role = value.get("role")
    if not isinstance(node_id, str) or not node_id.startswith("omarchypi-") or len(node_id) < 16:
        return False
    if not isinstance(role, str) or not role or len(role) > 64:
        return False
    if value.get("network_scope") != "lan-only":
        return False
    if not isinstance(value.get("capabilities"), list):
        return False
    return True


def ensure_identity(path: Path, *, role: str = "edge-display") -> dict:
    path = Path(path)
    if path.exists():
        existing = json.loads(path.read_text())
        if not validate_identity(existing):
            raise ValueError(f"invalid node identity at {path}")
        return existing

    identity = {
        "schema": SCHEMA,
        "node_id": "omarchypi-" + secrets.token_hex(8),
        "role": role,
        "capabilities": list(DEFAULT_CAPABILITIES),
        "created_at": _now(),
        "network_scope": "lan-only",
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temp_path = Path(temp_name)
    try:
        temp_path.write_text(json.dumps(identity, indent=2) + "\n")
        temp_path.chmod(0o644)
        temp_path.replace(path)
    finally:
        temp_path.unlink(missing_ok=True)
    return identity
