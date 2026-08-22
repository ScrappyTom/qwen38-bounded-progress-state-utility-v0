from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from apparatus.canonical import canonical_json_bytes, load_json, sha256_bytes, sha256_file, write_json
from apparatus.constants import CELL, HISTORICAL_ACTION, ROOT, SEED, STAGE_B_MAXIMUM_CALLS, STUDY_ID, TARGET
from apparatus.custody import require_authorization, require_clean_head
from apparatus.environment import make_environment
from apparatus.modelio import HttpRecord, ParentTokenEndpoint, post_chat
from apparatus.protocol import classify_action, parse_response


def _candidate(env: Any) -> dict[str, Any]:
    snapshot = env.snapshot()
    target = env.candidate_root / TARGET
    return {
        "candidate_id": snapshot["candidate_id"],
        "target_sha256": sha256_file(target),
        "target_size_bytes": target.stat().st_size,
        "snapshot": snapshot,
    }


def _provider_call(base_url: str, request: dict[str, Any], run_root: Path, call: int) -> HttpRecord:
    name = f"call-{call:02d}"
    body = canonical_json_bytes(request)
    write_json(run_root / "requests" / f"{name}.json", request)
    response = post_chat(base_url, body)
    (run_root / "raw" / f"{name}.body").write_bytes(response.body)
    write_json(run_root / "raw" / f"{name}-http.json", {
        "request_sha256": sha256_bytes(body),
        "status_code": response.status_code,
        "headers": response.headers,
        "duration_ms": response.duration_ms,
        "transport_error": response.transport_error,
        "response_body_sha256": sha256_bytes(response.body),
        "response_body_size_bytes": len(response.body),
    })
    if response.success:
        payload = json.loads(response.body)
        write_json(run_root / "responses" / f"{name}.json", payload)
    return response


def run_stage_b(run_id: str, base_url: str, runtime_custody: dict[str, Any]) -> dict[str, Any]:
    authorization = require_authorization("stage-b", STAGE_B_MAXIMUM_CALLS)
    head = require_clean_head()
    run_root = ROOT / "runs" / run_id
    if run_root.exists():
        raise RuntimeError(f"run already exists: {run_root}")
    for name in ("requests", "responses", "raw", "actions", "results", "candidates", "budget", "analysis", "model", "world", "replay"):
        (run_root / name).mkdir(parents=True, exist_ok=True)
    write_json(run_root / "model" / "AUTHORIZATION.json", authorization["authorization"])
    write_json(run_root / "model" / "runtime-custody.json", runtime_custody)

    request = load_json(ROOT / "STAGE_B_TREATED_REQUEST.json")
    preflight = load_json(ROOT / "STAGE_B_PACKAGE_PREFLIGHT.json")
    if not preflight["verification_passed"]:
        raise RuntimeError("Stage B package preflight did not pass")
    endpoint = ParentTokenEndpoint(base_url)
    env = make_environment(CELL, run_root / "world" / "treated")
    write_json(run_root / "candidates" / "initial.json", _candidate(env))

    records: list[dict[str, Any]] = []
    endpoint_reason = "call_limit"
    for call in range(1, STAGE_B_MAXIMUM_CALLS + 1):
        name = f"call-{call:02d}"
        capacity = endpoint.count(request["messages"], request["chat_template_kwargs"])
        if not capacity.fits:
            endpoint_reason = "pre_call_capacity_censored"
            break
        if call == 1 and capacity.as_dict() != preflight["treated_capacity"]:
            raise RuntimeError("first treated request differs from frozen exact preflight")
        (run_root / "requests" / f"{name}.rendered-prompt.txt").write_bytes(capacity.rendered_prompt.encode("utf-8"))
        before = _candidate(env)
        response = _provider_call(base_url, request, run_root, call)
        parsed = parse_response(response, CELL)
        if not parsed["valid"]:
            write_json(run_root / "actions" / f"{name}.json", parsed)
            records.append({"call": call, "valid_action": False, "parse": parsed, "capacity": capacity.as_dict()})
            endpoint_reason = "invalid_or_integrity_response"
            break

        action = parsed["action"]
        result = env.execute(action)
        after = _candidate(env)
        classification = classify_action(action, result, request["messages"])
        historical_match = action == HISTORICAL_ACTION
        result_message = env.result_message(action, f"h05-treated-{call:03d}", result)
        next_request = copy.deepcopy(request)
        next_request["messages"] = copy.deepcopy(request["messages"]) + [parsed["assistant_message"], result_message]
        prospective = endpoint.count(next_request["messages"], next_request["chat_template_kwargs"])
        write_json(run_root / "actions" / f"{name}.json", {
            "action": action,
            "admitted": result.get("accepted") is True,
            "classification": classification,
            "exact_historical_focus_reread": historical_match,
            "candidate_before": before["candidate_id"],
            "candidate_after": after["candidate_id"],
            "candidate_changed": before["candidate_id"] != after["candidate_id"],
            "usage": parsed.get("usage"),
        })
        write_json(run_root / "results" / f"{name}.json", {
            "action": action,
            "result": result,
            "result_message": result_message,
            "prospective_next_capacity": prospective.as_dict(),
        })
        write_json(run_root / "candidates" / f"after-{name}.json", after)
        write_json(run_root / "budget" / f"{name}.json", {
            "pre_call": capacity.as_dict(),
            "prospective_next": prospective.as_dict(),
            "provider_request_sha256": sha256_bytes(canonical_json_bytes(request)),
            "provider_response_sha256": sha256_bytes(response.body),
            "http_duration_ms": response.duration_ms,
        })
        records.append({
            "call": call,
            "valid_action": True,
            "action": action,
            "classification": classification,
            "admitted": result.get("accepted") is True,
            "candidate_changed": before["candidate_id"] != after["candidate_id"],
            "exact_historical_focus_reread": historical_match,
            "prospective_next_fits": prospective.fits,
            "result_crossed_later_model_boundary": False,
        })

        if historical_match:
            endpoint_reason = "exact_historical_focus_reread"
            break
        if action.get("action") == "submit" and result.get("accepted") is True:
            endpoint_reason = "admitted_submission"
            break
        if not prospective.fits:
            endpoint_reason = "result_delivery_capacity_censored"
            break
        if call == STAGE_B_MAXIMUM_CALLS:
            endpoint_reason = "call_limit"
            break
        request = next_request
        records[-1]["result_crossed_later_model_boundary"] = True

    final = _candidate(env)
    write_json(run_root / "candidates" / "terminal.json", final)
    (run_root / "candidates" / TARGET).write_bytes((env.candidate_root / TARGET).read_bytes())
    valid_records = [record for record in records if record.get("valid_action")]
    actions = [record["action"] for record in valid_records]
    result = {
        "schema_version": "bounded-progress-state-stage-b-result-v0",
        "study_id": STUDY_ID,
        "run_id": run_id,
        "standalone_commit": head,
        "source_lock_sha256": authorization["source_lock_sha256"],
        "seed": SEED,
        "model_calls": len(records),
        "maximum_model_calls": STAGE_B_MAXIMUM_CALLS,
        "retries": 0,
        "endpoint_reason": endpoint_reason,
        "calls": records,
        "mutation_attempts": sum(action.get("action") in {"patch", "replace_file"} for action in actions),
        "admitted_mutations": sum(record["action"].get("action") in {"patch", "replace_file"} and record.get("admitted") for record in valid_records),
        "submissions": sum(record["action"].get("action") == "submit" and record.get("admitted") for record in valid_records),
        "exact_historical_focus_reread": any(record.get("exact_historical_focus_reread") for record in records),
        "candidate_changed": final["candidate_id"] != load_json(run_root / "candidates" / "initial.json")["candidate_id"],
        "passed_apparatus_integrity": len(records) <= STAGE_B_MAXIMUM_CALLS,
    }
    write_json(run_root / "RUN_RESULT.json", result)
    return result
