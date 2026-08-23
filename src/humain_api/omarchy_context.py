"""Local Omarchy adapter for bounded public-pointer context."""
from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import urlparse
import hashlib
import json


class PointerError(ValueError):
    """Raised when a pointer is not safe for the public-only adapter."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _digest(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def validate_public_pointer(pointer: str) -> str:
    if not isinstance(pointer, str) or len(pointer) > 2048:
        raise PointerError("pointer must be a short absolute HTTPS URL")
    parsed = urlparse(pointer)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise PointerError("only absolute HTTPS pointers are accepted")
    if parsed.query or parsed.fragment:
        raise PointerError("query strings and fragments are not accepted")
    return pointer


def resolve_public_pointer(pointer: str, *, requester: str = "omarchy-local") -> dict:
    pointer = validate_public_pointer(pointer)
    parsed = urlparse(pointer)
    return {
        "schema": "humain.resolve.response.v1",
        "message_id": "response:omarchy:" + hashlib.sha256(pointer.encode()).hexdigest()[:20],
        "message_type": "resolve.response",
        "pointer": pointer,
        "publisher": "omarchy-public-pointer-adapter",
        "audience": requester,
        "resolution_state": "public_only",
        "payload": {
            "visibility": "public",
            "host": parsed.hostname,
            "path": parsed.path or "/",
            "actions": [],
        },
        "provenance": {
            "created_at": _now(),
            "method": "omarchy-local-public-pointer-adapter",
            "parent": _digest({"pointer": pointer, "requester": requester}),
        },
        "permissions": {
            "action": "resolve",
            "capability_checked": False,
            "private_context": False,
            "actions": [],
        },
        "error": None,
        "signature": {
            "algorithm": "demo",
            "key_ref": "omarchy-public-pointer-adapter",
            "value": "demo:unsigned",
        },
    }
