#!/usr/bin/env python3
"""Loopback-only HTTP adapter for the HumAIn Omarchy browser lens."""
from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from humain_api.omarchy_context import PointerError, resolve_public_pointer


class Handler(BaseHTTPRequestHandler):
    server_version = "HumAIn-Omarchy/0.1"

    def _send(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        # This adapter returns only public pointer metadata and never accepts credentials.
        # Wildcard CORS is therefore bounded to this non-sensitive local projection.
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):  # noqa: N802
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):  # noqa: N802
        if self.path == "/healthz":
            self._send(200, {"ok": True, "service": "humain-omarchy-context", "protocol": "0.1"})
        else:
            self._send(404, {"error": "not_found"})

    def do_POST(self):  # noqa: N802
        if self.path != "/v1/context":
            self._send(404, {"error": "not_found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length > 8192:
                self._send(413, {"error": "request_too_large"})
                return
            data = json.loads(self.rfile.read(length))
            response = resolve_public_pointer(data["pointer"], requester=str(data.get("requester", "omarchy-browser")))
            self._send(200, response)
        except (KeyError, TypeError, json.JSONDecodeError):
            self._send(400, {"error": "invalid_request"})
        except PointerError as exc:
            self._send(422, {"error": "invalid_pointer", "detail": str(exc)})

    def log_message(self, *_args):
        return


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 8787), Handler)
    print("HumAIn Omarchy context adapter listening on http://127.0.0.1:8787", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
