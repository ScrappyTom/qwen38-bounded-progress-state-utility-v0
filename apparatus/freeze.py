from __future__ import annotations

from pathlib import Path

from apparatus.canonical import sha256_bytes, sha256_file, write_json
from apparatus.constants import ROOT, STUDY_ID


EXCLUDED_PARTS = {".git", ".cache", "execution", "runs", "__pycache__"}
EXCLUDED_FILES = {
    "AUTHORIZATION_REQUEST.json",
    "provenance/SOURCE_LOCK.json",
}


def eligible(path: Path) -> bool:
    relative = path.relative_to(ROOT).as_posix()
    if relative in EXCLUDED_FILES:
        return False
    if any(part in EXCLUDED_PARTS for part in path.relative_to(ROOT).parts):
        return False
    return path.is_file() and path.suffix != ".pyc"


def build_source_lock() -> dict[str, object]:
    locked = {
        path.relative_to(ROOT).as_posix(): sha256_file(path)
        for path in sorted(ROOT.rglob("*"), key=lambda item: item.relative_to(ROOT).as_posix())
        if eligible(path)
    }
    digest_input = "\n".join(f"{name}\0{digest}" for name, digest in locked.items()).encode("utf-8")
    return {
        "schema_version": "bounded-progress-state-source-lock-v0",
        "study_id": STUDY_ID,
        "locked_artifact_count": len(locked),
        "locked_content_sha256": sha256_bytes(digest_input),
        "excluded_mutable_roots": [".cache", "execution", "runs"],
        "locked_artifacts": locked,
    }


def main() -> int:
    output = ROOT / "provenance" / "SOURCE_LOCK.json"
    write_json(output, build_source_lock())
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
