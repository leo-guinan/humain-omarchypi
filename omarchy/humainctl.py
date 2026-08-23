#!/usr/bin/env python3
"""CLI and Waybar adapter for the local HumAIn public-pointer lens."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from humain_api.omarchy_context import PointerError, resolve_public_pointer


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="humainctl")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("context", "waybar"):
        command = sub.add_parser(name)
        command.add_argument("pointer")
        command.add_argument("--json", action="store_true", dest="as_json")
    return parser


def _waybar(response: dict) -> dict:
    host = response["payload"].get("host", "pointer")
    state = response["resolution_state"]
    return {
        "text": f"◉ {host}",
        "alt": state,
        "class": "public-only" if state == "public_only" else "unavailable",
        "tooltip": f"HumAIn: {state}\\nPointer: {response['pointer']}\\nNo private context or actions available.",
    }


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        response = resolve_public_pointer(args.pointer)
    except PointerError as exc:
        print(json.dumps({"error": "invalid_pointer", "detail": str(exc)}), file=sys.stderr)
        return 2
    if args.command == "waybar":
        print(json.dumps(_waybar(response), ensure_ascii=False))
    elif args.as_json:
        print(json.dumps(response, indent=2, sort_keys=True))
    else:
        print(f"HumAIn: {response['resolution_state']}")
        print(f"Pointer: {response['pointer']}")
        print("Private context: unavailable")
        print("Actions: none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
