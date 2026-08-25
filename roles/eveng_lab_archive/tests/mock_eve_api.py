#!/usr/bin/env python3

from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import unquote, urlparse


class Handler(BaseHTTPRequestHandler):
    labs_root = Path("/")

    def log_message(self, _format: str, *_args: object) -> None:
        return

    def _reply(self, code: int, payload: dict[str, object], *, cookie: bool = False) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        if cookie:
            self.send_header("Set-Cookie", "unetlab_session=test; Path=/")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        if self.path != "/api/auth/login":
            self._reply(404, {"status": "fail", "message": "not found"})
            return
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length) or b"{}")
        if not payload.get("username") or not payload.get("password"):
            self._reply(401, {"status": "fail", "message": "unauthorised"})
            return
        self._reply(200, {"status": "success", "code": 200}, cookie=True)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/auth/logout":
            self._reply(200, {"status": "success", "code": 200})
            return
        self._reply(405, {"status": "fail", "message": "method not allowed"})

    def do_PUT(self) -> None:
        parsed = urlparse(self.path)
        prefix = "/api/labs/"
        suffix = "/nodes/export"
        if not parsed.path.startswith(prefix) or not parsed.path.endswith(suffix):
            self._reply(404, {"status": "fail", "message": "not found"})
            return
        if "unetlab_session=test" not in self.headers.get("Cookie", ""):
            self._reply(401, {"status": "fail", "message": "unauthorised"})
            return
        relative = unquote(parsed.path[len(prefix) : -len(suffix)])
        lab = (self.labs_root / relative).resolve()
        if self.labs_root.resolve() not in lab.parents or not lab.is_file():
            self._reply(404, {"status": "fail", "message": "lab not found"})
            return
        marker = '<configs captured="true"/>\n'
        content = lab.read_text(encoding="utf-8")
        if marker not in content:
            lab.write_text(content + marker, encoding="utf-8")
        self._reply(200, {"status": "success", "code": 200})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--labs-root", required=True)
    parser.add_argument("--port", required=True, type=int)
    args = parser.parse_args()
    Handler.labs_root = Path(args.labs_root).resolve()
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
