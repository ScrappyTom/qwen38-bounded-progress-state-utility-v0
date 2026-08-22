from __future__ import annotations

import argparse
import copy
import json
import tempfile
from pathlib import Path
from typing import Any

from apparatus.canonical import canonical_json_bytes, load_json, sha256_bytes, sha256_file, write_json
from apparatus.constants import CELL, ROOT, STUDY_ID, TARGET
from apparatus.environment import make_environment
from apparatus.modelio import HttpRecord
from apparatus.protocol import parse_response


def replay(run_id: str) -> dict[str, Any]:
    run_root = ROOT / "runs" / run_id
    result = load_json(run_root / "RUN_RESULT.json")
    checks: dict[str, bool] = {}
    request = load_json(ROOT / "STAGE_B_TREATED_REQUEST.json")
    checks["first_request_matches_frozen_treatment"] = load_json(run_root / "requests" / "call-01.json") == request
    with tempfile.TemporaryDirectory() as temp:
        env = make_environment(CELL, Path(temp) / "world")
        for call in range(1, result["model_calls"] + 1):
            name = f"call-{call:02d}"
            saved_request = load_json(run_root / "requests" / f"{name}.json")
            checks[f"{name}_request_reconstructed"] = saved_request == request
            raw = (run_root / "raw" / f"{name}.body").read_bytes()
            http = load_json(run_root / "raw" / f"{name}-http.json")
            checks[f"{name}_raw_hash"] = sha256_bytes(raw) == http["response_body_sha256"]
            checks[f"{name}_request_hash"] = sha256_bytes(canonical_json_bytes(saved_request)) == http["request_sha256"]
            parsed = parse_response(HttpRecord(200, {}, raw, 0, None), CELL)
            saved_action_record = load_json(run_root / "actions" / f"{name}.json")
            if not result["calls"][call - 1].get("valid_action"):
                checks[f"{name}_invalid_response_replayed"] = parsed.get("valid") is False
                break
            checks[f"{name}_raw_json"] = json.loads(raw) == load_json(run_root / "responses" / f"{name}.json")
            saved_action = saved_action_record["action"]
            checks[f"{name}_action_reparsed"] = parsed.get("valid") is True and parsed.get("action") == saved_action
            replayed_result = env.execute(saved_action)
            saved_result = load_json(run_root / "results" / f"{name}.json")["result"]
            checks[f"{name}_result_reexecuted"] = replayed_result == saved_result
            checks[f"{name}_candidate_hash"] = sha256_file(env.candidate_root / TARGET) == load_json(run_root / "candidates" / f"after-{name}.json")["target_sha256"]
            if call < result["model_calls"]:
                result_message = env.result_message(saved_action, f"h05-treated-{call:03d}", replayed_result)
                request = copy.deepcopy(request)
                request["messages"] = copy.deepcopy(request["messages"]) + [parsed["assistant_message"], result_message]
        checks["terminal_candidate_exact"] = (env.candidate_root / TARGET).read_bytes() == (run_root / "candidates" / TARGET).read_bytes()
    receipt = {"schema_version": "bounded-progress-state-stage-b-replay-v0", "study_id": STUDY_ID, "run_id": run_id, "checks": checks, "passed": all(checks.values())}
    write_json(run_root / "replay" / "REPLAY.json", receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("run_id"); args = parser.parse_args()
    result = replay(args.run_id); print(json.dumps(result, sort_keys=True)); return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
