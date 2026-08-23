#!/usr/bin/env python3
"""Create the node identity once during first boot."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from node_identity import ensure_identity  # noqa: E402

STATE = Path(os.environ.get("OMARCHYPI_STATE_DIR", "/var/lib/omarchypi"))
ROLE = os.environ.get("OMARCHYPI_ROLE", "edge-display")


def main() -> int:
    identity = ensure_identity(STATE / "node.json", role=ROLE)
    node_id = identity["node_id"]
    hostname_file = Path("/etc/hostname")
    current = hostname_file.read_text().strip() if hostname_file.exists() else ""
    if current in {"omarchypi", "omarchypi-baseline", ""}:
        hostname_file.write_text(node_id + "\n")
        if shutil_which("hostnamectl"):
            subprocess.run(["hostnamectl", "set-hostname", node_id], check=False)
    (STATE / "initialized").write_text(identity["created_at"] + "\n")
    print(f"initialized {node_id}")
    return 0


def shutil_which(command: str) -> str | None:
    import shutil
    return shutil.which(command)


if __name__ == "__main__":
    raise SystemExit(main())
