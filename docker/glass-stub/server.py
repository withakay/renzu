#!/usr/bin/env python3

import argparse
import ast
import json
import re
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer

WORKSPACE_ROOT = Path("/workspace")
SYMBOL_PATTERN = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\b")
SYMBOL_CACHE: dict[str, dict] = {}


def _repo_file_path(path: str) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return WORKSPACE_ROOT / candidate


def _load_json(handler: BaseHTTPRequestHandler) -> dict:
    length = int(handler.headers.get("Content-Length", "0"))
    if length <= 0:
        return {}
    raw = handler.rfile.read(length)
    payload = json.loads(raw.decode("utf-8"))
    if isinstance(payload, dict):
        return payload
    return {}


def _python_symbols(repo_id: str, rel_path: str, source: str) -> list[dict]:
    symbols: list[dict] = []
    try:
        module = ast.parse(source)
    except SyntaxError:
        return symbols

    for node in ast.walk(module):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            kind = "function"
            name = node.name
            line = int(node.lineno)
        elif isinstance(node, ast.ClassDef):
            kind = "class"
            name = node.name
            line = int(node.lineno)
        else:
            continue

        symbol_id = f"{repo_id}:{rel_path}:{name}:{line}"
        symbol = {
            "symbol_id": symbol_id,
            "name": name,
            "kind": kind,
            "location": {"repo_id": repo_id, "path": rel_path, "line": line, "column": 1},
        }
        symbols.append(symbol)
        SYMBOL_CACHE[symbol_id] = symbol

    return symbols


def _generic_symbols(repo_id: str, rel_path: str, source: str) -> list[dict]:
    symbols: list[dict] = []
    for line_no, line in enumerate(source.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("def "):
            name = stripped.split("def ", 1)[1].split("(", 1)[0].strip()
            kind = "function"
        elif stripped.startswith("class "):
            name = stripped.split("class ", 1)[1].split("(", 1)[0].split(":", 1)[0].strip()
            kind = "class"
        else:
            continue

        if not name:
            continue

        symbol_id = f"{repo_id}:{rel_path}:{name}:{line_no}"
        symbol = {
            "symbol_id": symbol_id,
            "name": name,
            "kind": kind,
            "location": {"repo_id": repo_id, "path": rel_path, "line": line_no, "column": 1},
        }
        symbols.append(symbol)
        SYMBOL_CACHE[symbol_id] = symbol

    return symbols


def _scan_references(repo_id: str, symbol_name: str, limit: int = 100) -> list[dict]:
    references: list[dict] = []
    if not WORKSPACE_ROOT.exists():
        return references

    pattern = re.compile(rf"\b{re.escape(symbol_name)}\b")
    for path in WORKSPACE_ROOT.rglob("*.py"):
        if "/.venv/" in str(path) or "/.git/" in str(path):
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        rel_path = str(path.relative_to(WORKSPACE_ROOT))
        for line_no, line in enumerate(content.splitlines(), start=1):
            match = pattern.search(line)
            if not match:
                continue
            references.append(
                {
                    "repo_id": repo_id,
                    "path": rel_path,
                    "line": line_no,
                    "column": match.start() + 1,
                }
            )
            if len(references) >= limit:
                return references

    return references


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
        if self.path == "/v1/glass/list_symbols":
            payload = _load_json(self)
            repo_id = str(payload.get("repo_id", "repo"))
            rel_path = str(payload.get("path", ""))
            file_path = _repo_file_path(rel_path)
            if not rel_path or not file_path.exists():
                self._send_json(200, {"symbols": []})
                return

            try:
                source = file_path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                self._send_json(200, {"symbols": []})
                return

            if file_path.suffix == ".py":
                symbols = _python_symbols(repo_id, rel_path, source)
            else:
                symbols = _generic_symbols(repo_id, rel_path, source)
            self._send_json(200, {"symbols": symbols})
            return

        if self.path == "/v1/glass/describe_symbol":
            payload = _load_json(self)
            symbol_id = str(payload.get("symbol_id", ""))
            symbol = SYMBOL_CACHE.get(symbol_id)
            if symbol is None:
                self._send_json(200, {"definition": None})
                return
            self._send_json(200, {"definition": symbol})
            return

        if self.path == "/v1/glass/find_references":
            payload = _load_json(self)
            symbol_id = str(payload.get("symbol_id", ""))
            symbol = SYMBOL_CACHE.get(symbol_id)
            if symbol is None:
                self._send_json(200, {"references": []})
                return
            name = str(symbol.get("name", ""))
            repo_id = str(symbol.get("location", {}).get("repo_id", "repo"))
            references = _scan_references(repo_id, name)
            self._send_json(200, {"references": references})
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
