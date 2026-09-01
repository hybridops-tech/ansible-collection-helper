#!/usr/bin/env python3
"""Promote staged EVE-NG image paths with rollback support."""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path, PurePosixPath


def _safe_relative(value: str) -> Path:
    relative = PurePosixPath(value)
    if not value or relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"unsafe image path: {value}")
    return Path(*relative.parts)


def _remove(path: Path) -> None:
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink(missing_ok=True)


def _transaction_path(staging: Path) -> Path:
    return staging / "transaction.json"


def _require_safe_parent(root: Path, relative: Path) -> None:
    parent = root
    for part in relative.parts[:-1]:
        parent /= part
        if parent.is_symlink():
            raise ValueError(f"image destination has a symbolic-link parent: {relative}")


def _rollback(staging: Path, root: Path) -> None:
    transaction_path = _transaction_path(staging)
    if not transaction_path.is_file():
        return
    transaction = json.loads(transaction_path.read_text(encoding="utf-8"))
    for entry in reversed(transaction):
        relative = _safe_relative(str(entry["path"]))
        _require_safe_parent(root, relative)
        destination = root / relative
        backup = staging / "backup" / relative
        _remove(destination)
        if bool(entry["replaced"]):
            destination.parent.mkdir(parents=True, exist_ok=True)
            os.replace(backup, destination)
    transaction_path.unlink(missing_ok=True)


def _apply(staging: Path, root: Path, values: list[str], overwrite: bool) -> None:
    transaction: list[dict[str, object]] = []
    transaction_path = _transaction_path(staging)
    try:
        for value in values:
            relative = _safe_relative(value)
            _require_safe_parent(root, relative)
            source = staging / "payload" / relative
            destination = root / relative
            backup = staging / "backup" / relative
            if not source.exists() or source.is_symlink():
                raise ValueError(f"staged image path is missing or unsafe: {value}")
            replaced = destination.exists() or destination.is_symlink()
            if replaced and not overwrite:
                raise FileExistsError(
                    f"EVE-NG image content already exists at {value}; "
                    "use --overwrite-images only when replacement is intended"
                )
            if replaced:
                backup.parent.mkdir(parents=True, exist_ok=True)
                os.replace(destination, backup)
            destination.parent.mkdir(parents=True, exist_ok=True)
            os.replace(source, destination)
            transaction.append({"path": value, "replaced": replaced})
            transaction_path.write_text(json.dumps(transaction), encoding="utf-8")
    except Exception:
        _rollback(staging, root)
        raise


def main() -> int:
    if len(sys.argv) != 6 or sys.argv[1] not in {"apply", "rollback"}:
        print(
            "usage: restore_images_transaction.py apply|rollback "
            "STAGING ROOT PATHS_JSON OVERWRITE",
            file=sys.stderr,
        )
        return 2
    mode = sys.argv[1]
    staging = Path(sys.argv[2]).resolve()
    root = Path(sys.argv[3]).resolve()
    values = json.loads(sys.argv[4])
    overwrite = sys.argv[5].lower() == "true"
    if not isinstance(values, list) or not all(
        isinstance(value, str) for value in values
    ):
        raise ValueError("image path list is invalid")
    if mode == "apply":
        _apply(staging, root, values, overwrite)
    else:
        _rollback(staging, root)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from None
