#!/usr/bin/env python3

from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import unquote, urlparse
from xml.etree import ElementTree


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
        prefix = "/api/labs/"
        configs_suffix = "/configs"
        wipe_suffix = "/nodes/wipe"
        if "unetlab_session=test" not in self.headers.get("Cookie", ""):
            self._reply(401, {"status": "fail", "message": "unauthorised"})
            return
        if parsed.path.startswith(prefix) and parsed.path.endswith(configs_suffix):
            lab = self._resolve_lab(parsed.path, configs_suffix)
            if lab is None:
                return
            root = ElementTree.parse(lab).getroot()
            nodes = {node.get("id"): node for node in root.findall("./topology/nodes/node")}
            configs = {
                config.get("id"): config for config in root.findall("./objects/configs/config")
            }
            data = {
                node_id: {
                    "config": node.get("config", "0"),
                    "len": 1 if node_id in configs else 0,
                    "name": node.get("name", "node"),
                }
                for node_id, node in nodes.items()
            }
            self._reply(200, {"status": "success", "code": 200, "data": data})
            return
        if parsed.path.startswith(prefix) and parsed.path.endswith(wipe_suffix):
            lab = self._resolve_lab(parsed.path, wipe_suffix)
            if lab is None:
                return
            lab.with_suffix(lab.suffix + ".wipe-observed").write_text("wiped\n", encoding="utf-8")
            self._reply(200, {"status": "success", "code": 200})
            return
        self._reply(405, {"status": "fail", "message": "method not allowed"})

    def do_PUT(self) -> None:
        parsed = urlparse(self.path)
        prefix = "/api/labs/"
        if "unetlab_session=test" not in self.headers.get("Cookie", ""):
            self._reply(401, {"status": "fail", "message": "unauthorised"})
            return
        export_suffix = "/nodes/export"
        if parsed.path.startswith(prefix) and parsed.path.endswith(export_suffix):
            lab = self._resolve_lab(parsed.path, export_suffix)
            if lab is None:
                return
            tree = ElementTree.parse(lab)
            root = tree.getroot()
            configs = root.find("./objects/configs")
            if configs is None:
                objects = root.find("objects")
                if objects is None:
                    objects = ElementTree.SubElement(root, "objects")
                configs = ElementTree.SubElement(objects, "configs")
            if configs.find("./config[@id='1']") is None:
                config = ElementTree.SubElement(configs, "config", {"id": "1"})
                config.text = "aG9zdG5hbWUgUkVTVE9SRUQK"
                tree.write(lab, encoding="unicode")
            self._reply(200, {"status": "success", "code": 200})
            return
        node_marker = "/nodes/"
        if parsed.path.startswith(prefix) and node_marker in parsed.path:
            lab_path, node_id = parsed.path[len(prefix) :].rsplit(node_marker, 1)
            lab = self._resolve_lab(prefix + lab_path + node_marker, "/nodes/")
            if lab is None:
                return
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length) or b"{}")
            tree = ElementTree.parse(lab)
            node = tree.getroot().find(f"./topology/nodes/node[@id='{unquote(node_id)}']")
            if node is None:
                self._reply(404, {"status": "fail", "message": "node not found"})
                return
            node.set("config", str(payload.get("config", "0")))
            tree.write(lab, encoding="unicode")
            self._reply(201, {"status": "success", "code": 201})
            return
        self._reply(404, {"status": "fail", "message": "not found"})

    def _resolve_lab(self, path: str, suffix: str) -> Path | None:
        prefix = "/api/labs/"
        relative = unquote(path[len(prefix) : -len(suffix)])
        lab = (self.labs_root / relative).resolve()
        if self.labs_root.resolve() not in lab.parents or not lab.is_file():
            self._reply(404, {"status": "fail", "message": "lab not found"})
            return None
        return lab


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--labs-root", required=True)
    parser.add_argument("--port", required=True, type=int)
    args = parser.parse_args()
    Handler.labs_root = Path(args.labs_root).resolve()
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
