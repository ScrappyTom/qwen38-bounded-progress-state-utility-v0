from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from apparatus.canonical import load_json, sha256_bytes
from apparatus.constants import ROOT


def verify_commit_lock(lock_path: Path, commit: str) -> dict[str, Any]:
    lock = load_json(lock_path)
    checks: dict[str, bool] = {}
    for relative, expected in lock["locked_artifacts"].items():
        result = subprocess.run(
            ["git", "show", f"{commit}:{relative}"],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        checks[relative] = result.returncode == 0 and sha256_bytes(result.stdout) == expected
    ancestry = subprocess.run(
        ["git", "cat-file", "-e", f"{commit}^{{commit}}"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return {
        "schema_version": "bounded-progress-state-commit-lock-verification-v0",
        "commit": commit,
        "lock_path": lock_path.relative_to(ROOT).as_posix(),
        "commit_exists": ancestry.returncode == 0,
        "artifact_count": len(checks),
        "checks": checks,
        "passed": ancestry.returncode == 0 and all(checks.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("lock", type=Path)
    parser.add_argument("commit")
    args = parser.parse_args()
    lock = args.lock if args.lock.is_absolute() else ROOT / args.lock
    result = verify_commit_lock(lock, args.commit)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
