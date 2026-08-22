from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

from apparatus.canonical import canonical_json_bytes, load_json, sha256_bytes, sha256_file, write_json
from apparatus.constants import CELL, EXPECTED_CANDIDATE_ID, ROOT, STUDY_ID
from apparatus.environment import make_environment
from apparatus.modelio import HttpRecord
from apparatus.progress import control_request, extract_provider_message, maintenance_request, mechanical_note_audit
from apparatus.protocol import parse_response


def replay(run_id: str) -> dict[str, Any]:
    run_root = ROOT / "runs" / run_id
    checks: dict[str, bool] = {}

    saved_control = load_json(run_root / "requests" / "control.json")
    saved_maintenance = load_json(run_root / "requests" / "maintenance.json")
    checks["control_request_reconstructed"] = saved_control == control_request()
    checks["maintenance_request_reconstructed"] = saved_maintenance == maintenance_request()

    for name in ("control", "maintenance"):
        raw = (run_root / "raw" / f"{name}.body").read_bytes()
        saved = load_json(run_root / "responses" / f"{name}.json")
        checks[f"{name}_raw_response_matches_saved_json"] = json.loads(raw) == saved
        http = load_json(run_root / "raw" / f"{name}-http.json")
        checks[f"{name}_raw_response_hash"] = sha256_bytes(raw) == http["response_body_sha256"]
        checks[f"{name}_request_hash"] = sha256_bytes(canonical_json_bytes(load_json(run_root / "requests" / f"{name}.json"))) == http["request_sha256"]

    raw_control = (run_root / "raw" / "control.body").read_bytes()
    parsed = parse_response(HttpRecord(200, {}, raw_control, 0, None), CELL)
    saved_action = load_json(run_root / "actions" / "control.json")["action"]
    checks["control_response_reparsed"] = parsed.get("valid") is True and parsed.get("action") == saved_action
    with tempfile.TemporaryDirectory() as temp:
        env = make_environment(CELL, Path(temp) / "world")
        checks["initial_candidate_identity"] = env.snapshot()["candidate_id"] == EXPECTED_CANDIDATE_ID
        result = env.execute(saved_action)
        saved_result = load_json(run_root / "results" / "control.json")["result"]
        checks["control_result_reexecuted"] = result == saved_result

    maintenance_payload = load_json(run_root / "responses" / "maintenance.json")
    content, finish_reason, usage = extract_provider_message(maintenance_payload)
    stored_audit = load_json(run_root / "analysis" / "MAINTENANCE_MECHANICAL_AUDIT.json")
    checks["maintenance_content_reextracted"] = content == stored_audit["content"]
    checks["maintenance_finish_reextracted"] = finish_reason == stored_audit["finish_reason"]
    checks["maintenance_usage_reextracted"] = usage == stored_audit["usage"]
    checks["maintenance_mechanical_audit_replayed"] = mechanical_note_audit(content) == stored_audit["mechanical_audit"]
    checks["maintenance_content_hash"] = sha256_bytes(content.encode("utf-8")) == stored_audit["content_sha256"]

    for name in ("control", "maintenance"):
        rendered = run_root / "requests" / f"{name}.rendered-prompt.txt"
        budget = load_json(run_root / "analysis" / "MAINTENANCE_MECHANICAL_AUDIT.json")["capacity"] if name == "maintenance" else load_json(run_root / "budget" / "control.json")["capacity"]
        checks[f"{name}_rendered_prompt_hash"] = sha256_file(rendered) == budget["rendered_prompt_sha256"]

    receipt = {
        "schema_version": "bounded-progress-state-stage-a-replay-v0",
        "study_id": STUDY_ID,
        "run_id": run_id,
        "checks": checks,
        "passed": all(checks.values()),
    }
    write_json(run_root / "replay" / "REPLAY.json", receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_id")
    args = parser.parse_args()
    result = replay(args.run_id)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
