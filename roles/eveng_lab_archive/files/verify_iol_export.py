#!/usr/bin/env python3

"""Recover stopped IOL startup configurations and verify the lab export."""

from __future__ import annotations

import argparse
import base64
import binascii
import json
import os
from pathlib import Path
import ssl
import subprocess
import sys
from urllib.parse import quote
from urllib.request import HTTPSHandler, ProxyHandler, Request, build_opener
import uuid
from xml.etree import ElementTree


def _lab_state(lab: Path):
    root = ElementTree.parse(lab).getroot()
    nodes = [
        node
        for node in root.findall("./topology/nodes/node")
        if node.get("type") == "iol"
    ]
    lab_id = root.attrib["id"] if nodes else ""
    if nodes:
        uuid.UUID(lab_id)
    configs = {
        config.get("id"): config
        for config in root.findall("./objects/configs/config")
    }
    return lab_id, nodes, configs


def _node_state(node_state_root: Path, lab_id: str, node_id: str):
    if not node_id.isdecimal():
        raise ValueError(f"invalid IOL node ID: {node_id}")

    directories = []
    nvram_files = []
    for tenant in node_state_root.iterdir():
        if not tenant.name.isdecimal() or not tenant.is_dir() or tenant.is_symlink():
            continue
        node_dir = tenant / lab_id / node_id
        if node_dir.is_symlink() or not node_dir.is_dir():
            continue
        directories.append(node_dir)
        nvram_files.extend(
            path
            for path in node_dir.glob("nvram_*")
            if path.is_file() and not path.is_symlink()
        )
    return directories, nvram_files


def _config_bytes(config) -> bytes | None:
    try:
        encoded = "".join((config.text or "").split()) if config is not None else ""
        content = base64.b64decode(encoded, validate=True)
    except (ValueError, binascii.Error):
        return None
    return content if content.strip() else None


def _valid_config(config) -> bool:
    return _config_bytes(config) is not None


def verify(
    lab: Path, node_state_root: Path, unconfigured_ids: set[str] | None = None
) -> tuple[int, int]:
    lab_id, nodes, configs = _lab_state(lab)
    unconfigured_ids = unconfigured_ids or set()
    missing = []
    expected = 0

    for node in nodes:
        node_id = node.attrib["id"]
        directories, nvram_files = _node_state(node_state_root, lab_id, node_id)
        if not directories:
            continue
        if node_id in unconfigured_ids:
            continue
        expected += 1
        label = f"{node.get('name', node_id)} (id {node_id})"
        if not nvram_files:
            missing.append(f"{label}: NVRAM missing")
        elif len(nvram_files) != 1:
            missing.append(f"{label}: expected one NVRAM file")
        elif nvram_files[0].stat().st_size == 0:
            missing.append(f"{label}: empty NVRAM")
        elif not _valid_config(configs.get(node_id)):
            missing.append(label)

    if missing:
        raise ValueError("IOL configuration export missing: " + ", ".join(missing))
    return expected, len(nodes)


def recover(
    lab: Path,
    node_state_root: Path,
    *,
    api_base_url: str,
    api_lab: str,
    cookie: str,
    iou_export: Path,
    timeout: int,
    validate_certs: bool,
) -> tuple[int, set[str]]:
    if not cookie:
        raise ValueError("EVE-NG API session is unavailable")
    if not api_lab or api_lab.startswith("/") or ".." in Path(api_lab).parts:
        raise ValueError("EVE-NG API lab path is invalid")

    context = ssl.create_default_context()
    if not validate_certs:
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
    opener = build_opener(ProxyHandler({}), HTTPSHandler(context=context))
    lab_id, nodes, configs = _lab_state(lab)
    recovered = 0
    unconfigured_ids = set()

    for node in nodes:
        node_id = node.attrib["id"]
        directories, nvram_files = _node_state(node_state_root, lab_id, node_id)
        if not directories:
            continue
        label = f"{node.get('name', node_id)} (id {node_id})"
        if len(nvram_files) != 1 or nvram_files[0].stat().st_size == 0:
            raise ValueError(f"{label}: saved NVRAM is unavailable")

        result = subprocess.run(
            [str(iou_export), str(nvram_files[0]), "/dev/stdout"],
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        if (
            result.returncode == 3
            and not result.stdout.strip()
            and b"no startup config" in result.stderr.lower()
        ):
            if not _valid_config(configs.get(node_id)):
                unconfigured_ids.add(node_id)
            continue
        if result.returncode != 0 or not result.stdout.strip():
            raise ValueError(f"{label}: saved NVRAM could not be exported")
        try:
            config = result.stdout.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(f"{label}: exported configuration is not UTF-8") from exc

        if _config_bytes(configs.get(node_id)) == result.stdout:
            continue

        url = (
            api_base_url.rstrip("/")
            + "/api/labs/"
            + quote(api_lab, safe="/")
            + "/configs/"
            + node_id
        )
        request = Request(
            url,
            data=json.dumps({"data": config}).encode("utf-8"),
            headers={"Content-Type": "application/json", "Cookie": cookie},
            method="PUT",
        )
        try:
            with opener.open(request, timeout=timeout) as response:
                payload = json.load(response)
        except (OSError, ValueError) as exc:
            raise ValueError(f"{label}: EVE-NG config API update failed") from exc
        if not isinstance(payload, dict) or payload.get("status") != "success":
            raise ValueError(f"{label}: EVE-NG config API rejected the update")
        _, _, updated_configs = _lab_state(lab)
        if _config_bytes(updated_configs.get(node_id)) != result.stdout:
            raise ValueError(f"{label}: EVE-NG config API update was not persisted")
        recovered += 1

    return recovered, unconfigured_ids


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lab", type=Path, required=True)
    parser.add_argument("--node-state-root", type=Path, required=True)
    parser.add_argument("--recover", action="store_true")
    parser.add_argument("--api-base-url", default="")
    parser.add_argument("--api-lab", default="")
    parser.add_argument("--iou-export", type=Path, default=Path("/opt/unetlab/scripts/iou_export"))
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--validate-certs", choices=("true", "false"), default="true")
    args = parser.parse_args()
    try:
        recovered = 0
        unconfigured_ids = set()
        if args.recover:
            recovered, unconfigured_ids = recover(
                args.lab,
                args.node_state_root,
                api_base_url=args.api_base_url,
                api_lab=args.api_lab,
                cookie=os.environ.get("HYOPS_EVE_API_COOKIE", ""),
                iou_export=args.iou_export,
                timeout=args.timeout,
                validate_certs=args.validate_certs == "true",
            )
        expected, total = verify(args.lab, args.node_state_root, unconfigured_ids)
    except (
        OSError,
        KeyError,
        ValueError,
        subprocess.TimeoutExpired,
        ElementTree.ParseError,
    ) as exc:
        print(f"EVE-NG IOL export verification failed: {exc}", file=sys.stderr)
        return 1
    print(
        f"IOL configurations verified: {expected} with archived configurations, "
        f"{total} nodes; recovered={recovered}; "
        f"unconfigured={len(unconfigured_ids)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
