from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from apparatus.canonical import load_json, sha256_file
from apparatus.constants import (
    BRANCH,
    DONOR_COMMIT,
    DONOR_IMPORTED_FILES,
    DONOR_REPOSITORY,
    DONOR_ROOT,
    EXPECTED_MODEL_SHA256,
    EXPECTED_MODEL_SIZE,
    EXPECTED_SERVER_SHA256,
    PROGRAM_COMMIT,
    PROGRAM_IMPORTED_FILES,
    PROGRAM_REPOSITORY,
    PROGRAM_ROOT,
    ROOT,
    STUDY_ID,
)


def git_output(root: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, text=True)
    if result.returncode:
        raise RuntimeError(f"git {' '.join(args)} failed in {root}: {result.stderr.strip()}")
    return result.stdout.strip()


def current_head() -> str:
    return git_output(ROOT, "rev-parse", "HEAD")


def require_clean_head() -> str:
    head = current_head()
    if git_output(ROOT, "status", "--porcelain=v1", "--untracked-files=all"):
        raise RuntimeError("measured execution requires a clean committed standalone HEAD")
    if git_output(ROOT, "branch", "--show-current") != BRANCH:
        raise RuntimeError("measured execution is on the wrong branch")
    return head


def _rows(root: Path, repository: str, commit: str, mapping: dict[str, str]) -> list[dict[str, Any]]:
    rows = []
    for copied, original in sorted(mapping.items()):
        copied_path = ROOT / copied
        original_path = root / original
        if not copied_path.is_file() or not original_path.is_file():
            raise RuntimeError(f"missing materialization: {copied} / {original}")
        copied_hash = sha256_file(copied_path)
        original_hash = sha256_file(original_path)
        rows.append({
            "donor_repository": repository,
            "donor_commit": commit,
            "donor_path": original,
            "copied_path": copied,
            "donor_sha256": original_hash,
            "copied_sha256": copied_hash,
            "size_bytes": copied_path.stat().st_size,
            "byte_equivalent": copied_hash == original_hash and copied_path.read_bytes() == original_path.read_bytes(),
        })
    return rows


def donor_receipt() -> dict[str, Any]:
    for root, commit in ((DONOR_ROOT, DONOR_COMMIT), (PROGRAM_ROOT, PROGRAM_COMMIT)):
        if git_output(root, "rev-parse", "HEAD") != commit:
            raise RuntimeError(f"donor checkout is not pinned: {root}")
        if git_output(root, "status", "--porcelain=v1", "--untracked-files=all"):
            raise RuntimeError(f"donor checkout is not clean: {root}")
    rows = _rows(DONOR_ROOT, DONOR_REPOSITORY, DONOR_COMMIT, DONOR_IMPORTED_FILES)
    rows += _rows(PROGRAM_ROOT, PROGRAM_REPOSITORY, PROGRAM_COMMIT, PROGRAM_IMPORTED_FILES)
    return {
        "schema_version": "bounded-progress-state-parent-materialization-v0",
        "donors": [
            {"repository": DONOR_REPOSITORY, "commit": DONOR_COMMIT, "checkout": str(DONOR_ROOT)},
            {"repository": PROGRAM_REPOSITORY, "commit": PROGRAM_COMMIT, "checkout": str(PROGRAM_ROOT)},
        ],
        "file_count": len(rows),
        "total_size_bytes": sum(row["size_bytes"] for row in rows),
        "all_byte_equivalent": all(row["byte_equivalent"] for row in rows),
        "files": rows,
    }


def verify_source_lock(stage: str = "stage-a") -> tuple[dict[str, Any], str]:
    name = "SOURCE_LOCK-stage-b.json" if stage == "stage-b" else "SOURCE_LOCK.json"
    path = ROOT / "provenance" / name
    lock = load_json(path)
    for relative, expected in lock["locked_artifacts"].items():
        candidate = ROOT / relative
        if not candidate.is_file() or sha256_file(candidate) != expected:
            raise RuntimeError(f"source-lock mismatch: {relative}")
    return lock, sha256_file(path)


def require_authorization(stage: str, maximum_calls: int) -> dict[str, Any]:
    _, lock_hash = verify_source_lock(stage)
    path = ROOT / "execution" / f"AUTHORIZATION-{stage}.json"
    if not path.is_file():
        raise RuntimeError(f"authorization absent: {path.name}")
    authorization = load_json(path)
    required = {
        "schema_version": "measured-inference-authorization-v0",
        "study_id": STUDY_ID,
        "stage": stage,
        "approved": True,
        "source_lock_sha256": lock_hash,
        "maximum_model_calls": maximum_calls,
        "retries": 0,
    }
    errors = [key for key, value in required.items() if authorization.get(key) != value]
    authorized_source_commit = authorization.get("authorized_source_commit")
    if not isinstance(authorized_source_commit, str) or len(authorized_source_commit) != 40:
        errors.append("authorized_source_commit")
    else:
        ancestry = subprocess.run(
            ["git", "merge-base", "--is-ancestor", authorized_source_commit, current_head()],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if ancestry.returncode:
            errors.append("authorized_source_commit_ancestry")
    if errors:
        raise RuntimeError("authorization mismatch: " + ", ".join(errors))
    return {"authorization": authorization, "source_lock_sha256": lock_hash}


def verify_runtime_files(server: Path, model: Path) -> dict[str, Any]:
    if not server.is_file() or sha256_file(server) != EXPECTED_SERVER_SHA256:
        raise RuntimeError("llama-server hash mismatch")
    if not model.is_file() or model.stat().st_size != EXPECTED_MODEL_SIZE or sha256_file(model) != EXPECTED_MODEL_SHA256:
        raise RuntimeError("full model identity mismatch")
    return {
        "server": {"path": str(server), "sha256": EXPECTED_SERVER_SHA256, "size_bytes": server.stat().st_size},
        "model": {"path": str(model), "sha256": EXPECTED_MODEL_SHA256, "size_bytes": model.stat().st_size},
    }
