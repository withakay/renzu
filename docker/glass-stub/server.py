#!/usr/bin/env python3

import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, payload: dict) -> None:
        body = (json.dumps(payload, separators=(",", ":")) + "\n").encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path in ("/", "/healthz"):
            self._send_json(200, {"status": "ok", "service": "glass-stub"})
            return

        self._send_json(404, {"error": "not found"})

    def do_POST(self) -> None:
        if self.path.startswith("/v1/glass/"):
            self._send_json(
                501,
                {
                    "error": "not implemented",
                    "service": "glass-stub",
                    "hint": "Replace glass-stub with a real Glass server implementation.",
                },
            )
            return

        self._send_json(404, {"error": "not found"})

    def log_message(self, format: str, *args) -> None:
        # Keep container logs quiet; only show errors.
        return


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=12346)
    args = parser.parse_args()

    httpd = HTTPServer((args.host, args.port), Handler)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
