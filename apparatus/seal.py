from __future__ import annotations

import argparse
from pathlib import Path

from apparatus.canonical import sha256_bytes, sha256_file, write_json
from apparatus.constants import ROOT, STUDY_ID


def build_seal(run_root: Path) -> dict[str, object]:
    if not run_root.is_dir():
        raise RuntimeError(f"missing run: {run_root}")
    files = {
        path.relative_to(run_root).as_posix(): {
            "sha256": sha256_file(path),
            "size_bytes": path.stat().st_size,
        }
        for path in sorted(run_root.rglob("*"), key=lambda item: item.relative_to(run_root).as_posix())
        if path.is_file() and path.name != "SEAL.json"
    }
    digest_input = "\n".join(
        f"{name}\0{record['sha256']}\0{record['size_bytes']}" for name, record in files.items()
    ).encode("utf-8")
    return {
        "schema_version": "bounded-progress-state-run-seal-v0",
        "study_id": STUDY_ID,
        "run_id": run_root.name,
        "file_count": len(files),
        "total_size_bytes": sum(int(record["size_bytes"]) for record in files.values()),
        "content_manifest_sha256": sha256_bytes(digest_input),
        "files": files,
    }


def verify_seal(run_root: Path) -> dict[str, object]:
    from apparatus.canonical import load_json

    stored = load_json(run_root / "SEAL.json")
    rebuilt = build_seal(run_root)
    return {
        "stored_content_manifest_sha256": stored.get("content_manifest_sha256"),
        "rebuilt_content_manifest_sha256": rebuilt["content_manifest_sha256"],
        "stored_file_count": stored.get("file_count"),
        "rebuilt_file_count": rebuilt["file_count"],
        "passed": stored == rebuilt,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_id")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    run_root = ROOT / "runs" / args.run_id
    if args.verify:
        result = verify_seal(run_root)
        print(result)
        return 0 if result["passed"] else 1
    write_json(run_root / "SEAL.json", build_seal(run_root))
    print(run_root / "SEAL.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
