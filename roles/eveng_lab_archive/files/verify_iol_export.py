#!/usr/bin/env python3

"""Check that EVE-NG exported configurations for IOL nodes with NVRAM."""

from __future__ import annotations

import argparse
import base64
import binascii
from pathlib import Path
import sys
import uuid
from xml.etree import ElementTree


def verify(lab: Path, node_state_root: Path) -> tuple[int, int]:
    root = ElementTree.parse(lab).getroot()
    nodes = root.findall("./topology/nodes/node")
    iol_nodes = [node for node in nodes if node.get("type") == "iol"]
    if not iol_nodes:
        return 0, 0

    lab_id = root.attrib["id"]
    uuid.UUID(lab_id)
    configs = {
        config.get("id"): config
        for config in root.findall("./objects/configs/config")
    }
    missing = []
    expected = 0

    for node in iol_nodes:
        node_id = node.attrib["id"]
        if not node_id.isdecimal():
            raise ValueError(f"invalid IOL node ID: {node_id}")

        nvram_files = []
        for tenant in node_state_root.iterdir():
            if not tenant.name.isdecimal() or not tenant.is_dir() or tenant.is_symlink():
                continue
            node_dir = tenant / lab_id / node_id
            if node_dir.is_symlink() or not node_dir.is_dir():
                continue
            nvram_files.extend(
                path for path in node_dir.glob("nvram_*") if path.is_file()
            )

        if not nvram_files:
            continue
        expected += 1
        if any(path.stat().st_size == 0 for path in nvram_files):
            missing.append(f"{node.get('name', node_id)} (id {node_id}: empty NVRAM)")
            continue

        config = configs.get(node_id)
        try:
            encoded = "".join((config.text or "").split()) if config is not None else ""
            content = base64.b64decode(encoded, validate=True)
        except (ValueError, binascii.Error):
            content = b""
        if not content.strip():
            missing.append(f"{node.get('name', node_id)} (id {node_id})")

    if missing:
        raise ValueError("IOL configuration export missing: " + ", ".join(missing))
    return expected, len(iol_nodes)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lab", type=Path, required=True)
    parser.add_argument("--node-state-root", type=Path, required=True)
    args = parser.parse_args()
    try:
        expected, total = verify(args.lab, args.node_state_root)
    except (OSError, KeyError, ValueError, ElementTree.ParseError) as exc:
        print(f"EVE-NG IOL export verification failed: {exc}", file=sys.stderr)
        return 1
    print(f"IOL configurations verified: {expected} with NVRAM, {total} nodes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
