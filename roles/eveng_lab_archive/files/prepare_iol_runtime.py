#!/usr/bin/env python3
"""Let EVE-NG prepare IOL runtime paths before restoring saved node state."""

import argparse
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


MEMBER = re.compile(
    r"^(?P<tenant>[0-9]+)/(?P<lab>[0-9a-fA-F-]+)/(?P<node>[0-9]+)/"
    r"(?:nvram_[0-9]+|vlan\.dat-[0-9]+)$"
)


def lab_index(root: Path) -> dict[str, tuple[Path, ET.Element]]:
    labs: dict[str, tuple[Path, ET.Element]] = {}
    for path in root.rglob("*.unl"):
        if not path.is_file() or path.is_symlink():
            continue
        if path.stat().st_size > 32 * 1024 * 1024:
            raise ValueError(f"EVE-NG lab definition is too large: {path}")
        lab = ET.parse(path).getroot()
        lab_id = lab.get("id", "")
        if not lab_id:
            continue
        if lab_id in labs:
            raise ValueError(f"Duplicate EVE-NG lab ID: {lab_id}")
        labs[lab_id] = (path, lab)
    return labs


def prepare(
    *, labs_root: Path, state_root: Path, wrapper: Path, members: list[str], overwrite: bool
) -> None:
    labs = lab_index(labs_root)
    nodes: set[tuple[str, str, str]] = set()
    for member in members:
        match = MEMBER.fullmatch(member)
        if match is None:
            raise ValueError(f"Invalid IOL node-state member: {member}")
        nodes.add((match["tenant"], match["lab"], match["node"]))

    operations: list[tuple[str, str, Path, Path, str]] = []
    for tenant, lab_id, node_id in sorted(nodes):
        if lab_id not in labs:
            raise ValueError(f"EVE-NG lab is missing for IOL state: {lab_id}")
        lab_path, lab = labs[lab_id]
        node = next(
            (
                item
                for item in lab.findall("./topology/nodes/node")
                if item.get("id") == node_id
            ),
            None,
        )
        if node is None or node.get("type") != "iol":
            raise ValueError(f"IOL node is missing from lab {lab_id}: {node_id}")
        node_dir = state_root / tenant / lab_id / node_id
        if node_dir.is_symlink():
            raise ValueError(f"EVE-NG node runtime is a link: {node_dir}")
        if node_dir.exists() and not overwrite:
            raise ValueError(f"EVE-NG node runtime already exists: {node_dir}")
        image = node.get("image", "")
        if image and (Path(image).name != image or image in {".", ".."}):
            raise ValueError(f"Invalid IOL image name in lab {lab_id}: {image}")
        operations.append((tenant, node_id, lab_path, node_dir, image))

    for tenant, node_id, lab_path, node_dir, image in operations:
        args = ["-T", tenant, "-D", node_id, "-F", str(lab_path)]
        if node_dir.exists():
            subprocess.run(
                [str(wrapper), "-a", "wipe", *args],
                check=True,
                stdout=subprocess.DEVNULL,
                timeout=60,
            )
        try:
            subprocess.run(
                [str(wrapper), "-a", "start", *args],
                check=True,
                stdout=subprocess.DEVNULL,
                timeout=60,
            )
        finally:
            subprocess.run(
                [str(wrapper), "-a", "stop", *args],
                check=True,
                stdout=subprocess.DEVNULL,
                timeout=60,
            )
        if not (node_dir / "iourc").is_symlink():
            raise ValueError(f"EVE-NG did not prepare IOL licence path: {node_dir}")
        if image and not (node_dir / image).is_symlink():
            raise ValueError(f"EVE-NG did not prepare IOL image path: {node_dir}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--labs-root", type=Path, required=True)
    parser.add_argument("--state-root", type=Path, required=True)
    parser.add_argument("--wrapper", type=Path, required=True)
    parser.add_argument("--members-json", required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    try:
        members = json.loads(args.members_json)
        if not isinstance(members, list) or any(not isinstance(item, str) for item in members):
            raise ValueError("IOL node-state members must be a list of paths")
        prepare(
            labs_root=args.labs_root,
            state_root=args.state_root,
            wrapper=args.wrapper,
            members=members,
            overwrite=args.overwrite,
        )
    except (OSError, ValueError, ET.ParseError, subprocess.SubprocessError) as exc:
        print(f"IOL runtime preparation failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
