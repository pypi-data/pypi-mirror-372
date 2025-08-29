from __future__ import annotations
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Tuple


class EchoHandler(BaseHTTPRequestHandler):
    def _send(self, code: int, payload: dict):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):  # noqa: N802 (http server API)
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(body.decode("utf-8"))
        except Exception:
            data = {"raw": body.decode("utf-8", errors="ignore")}
        # emulate register endpoint returning ids
        if self.path.endswith("/register"):
            payload = {
                "detectorId": "echo-detector",
                "sessionToken": "echo-session",
                "echo": data,
            }
        else:
            payload = {"ok": True, "path": self.path, "echo": data}
        self._send(200, payload)


def run_echo_server(host: str = "127.0.0.1", port: int = 8080) -> None:
    HTTPServer((host, port), EchoHandler).serve_forever()


