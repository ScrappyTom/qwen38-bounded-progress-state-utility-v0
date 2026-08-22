from __future__ import annotations

import copy
import hashlib
from pathlib import Path
from typing import Any

from apparatus.canonical import load_json, sha256_bytes
from apparatus.constants import CELL, PARENT_EVIDENCE, SOURCE_COMMIT, SOURCE_PATHS, endpoint_root


def imported_request(cell: str = CELL) -> dict[str, Any]:
    return load_json(endpoint_root(cell) / "actor-request.json")


def imported_action(cell: str = CELL) -> dict[str, Any]:
    return load_json(endpoint_root(cell) / "actor-action.json")["action"]


def imported_result_record(cell: str = CELL) -> dict[str, Any]:
    return load_json(endpoint_root(cell) / "actor-result.json")


def action_schema(cell: str = CELL) -> dict[str, Any]:
    return copy.deepcopy(imported_request(cell)["response_format"]["json_schema"]["schema"])


def source_file(path: str) -> Path:
    if path not in SOURCE_PATHS:
        raise ValueError(f"source path is outside the frozen surface: {path}")
    return PARENT_EVIDENCE / "source" / Path(*path.split("/"))


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def source_record(path: str) -> dict[str, Any]:
    local = source_file(path)
    data = local.read_bytes()
    return {
        "path": path,
        "local_path": local,
        "data": data,
        "size_bytes": len(data),
        "sha256": sha256_bytes(data),
        "git_blob_sha": git_blob_sha(data),
        "source_commit": SOURCE_COMMIT,
    }
