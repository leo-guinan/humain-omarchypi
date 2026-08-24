"""Bounded, LAN-scoped OmarchyPi health receipts.

This is an observation format, not an authentication or remote-control protocol.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from typing import Any

SCHEMA = "omarchypi.health.v1"
_ALLOWED_HEALTH = {"context_service", "desktop", "version"}
_ALLOWED_TOP = {"schema", "receipt_id", "observed_at", "node_id", "role", "capabilities", "network_scope", "health"}


def canonical_bytes(value: dict[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def _stamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def build_receipt(node: dict[str, Any], *, context_service: str, desktop: str, version: str, observed_at: str | None = None) -> dict[str, Any]:
    if node.get("network_scope") != "lan-only":
        raise ValueError("health receipts require lan-only node scope")
    body = {
        "schema": SCHEMA,
        "observed_at": observed_at or _stamp(),
        "node_id": node["node_id"],
        "role": node["role"],
        "capabilities": sorted(set(node.get("capabilities", []))),
        "network_scope": "lan-only",
        "health": {
            "context_service": context_service,
            "desktop": desktop,
            "version": version,
        },
    }
    body["receipt_id"] = hashlib.sha256(canonical_bytes(body)).hexdigest()
    return body


def validate_receipt(value: object) -> bool:
    if not isinstance(value, dict) or set(value) != _ALLOWED_TOP:
        return False
    if value.get("schema") != SCHEMA or value.get("network_scope") != "lan-only":
        return False
    if not isinstance(value.get("receipt_id"), str) or len(value["receipt_id"]) != 64:
        return False
    if not isinstance(value.get("node_id"), str) or not value["node_id"].startswith("omarchypi-"):
        return False
    if not isinstance(value.get("role"), str) or not isinstance(value.get("observed_at"), str):
        return False
    if not isinstance(value.get("capabilities"), list) or not all(isinstance(x, str) for x in value["capabilities"]):
        return False
    health = value.get("health")
    if not isinstance(health, dict) or set(health) != _ALLOWED_HEALTH:
        return False
    if not all(isinstance(health[k], str) and health[k] for k in _ALLOWED_HEALTH):
        return False
    unsigned = dict(value)
    unsigned.pop("receipt_id")
    return hashlib.sha256(canonical_bytes(unsigned)).hexdigest() == value["receipt_id"]
