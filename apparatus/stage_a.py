from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apparatus.canonical import canonical_json_bytes, load_json, sha256_bytes, sha256_file, write_json
from apparatus.constants import (
    CELL,
    EXPECTED_CANDIDATE_ID,
    EXPECTED_CONTROL_HEADROOM,
    EXPECTED_CONTROL_PROMPT_TOKENS,
    HISTORICAL_ACTION,
    MAINTENANCE_MAXIMUM_TOKENS,
    PROGRESS_STATE_MAXIMUM_TOKENS,
    ROOT,
    SEED,
    STAGE_A_MAXIMUM_CALLS,
    STUDY_ID,
    TARGET,
)
from apparatus.custody import require_authorization, require_clean_head
from apparatus.environment import make_environment
from apparatus.modelio import ParentTokenEndpoint, post_chat
from apparatus.progress import control_request, extract_provider_message, maintenance_request, mechanical_note_audit
from apparatus.protocol import parse_response


def _candidate(env: Any) -> dict[str, Any]:
    snapshot = env.snapshot()
    target = env.candidate_root / TARGET
    return {
        "candidate_id": snapshot["candidate_id"],
        "target_sha256": sha256_file(target),
        "target_size_bytes": target.stat().st_size,
        "snapshot": snapshot,
    }


def _call(base_url: str, request: dict[str, Any], root: Path, name: str) -> tuple[bytes, dict[str, Any], int]:
    body = canonical_json_bytes(request)
    write_json(root / "requests" / f"{name}.json", request)
    response = post_chat(base_url, body)
    (root / "raw" / f"{name}.body").write_bytes(response.body)
    write_json(root / "raw" / f"{name}-http.json", {
        "request_sha256": sha256_bytes(body),
        "status_code": response.status_code,
        "headers": response.headers,
        "duration_ms": response.duration_ms,
        "transport_error": response.transport_error,
        "response_body_sha256": sha256_bytes(response.body),
        "response_body_size_bytes": len(response.body),
    })
    if not response.success:
        raise RuntimeError(f"provider call failed: {name}: {response.status_code} {response.transport_error}")
    payload = json.loads(response.body)
    if not isinstance(payload, dict):
        raise RuntimeError(f"provider returned non-object: {name}")
    write_json(root / "responses" / f"{name}.json", payload)
    return body, payload, response.duration_ms


def run_stage_a(run_id: str, base_url: str, runtime_custody: dict[str, Any]) -> dict[str, Any]:
    authorization = require_authorization("stage-a", STAGE_A_MAXIMUM_CALLS)
    head = require_clean_head()
    run_root = ROOT / "runs" / run_id
    if run_root.exists():
        raise RuntimeError(f"run already exists: {run_root}")
    for name in ("requests", "responses", "raw", "actions", "results", "candidates", "budget", "analysis", "model", "world"):
        (run_root / name).mkdir(parents=True, exist_ok=True)
    write_json(run_root / "model" / "AUTHORIZATION.json", authorization["authorization"])
    write_json(run_root / "model" / "runtime-custody.json", runtime_custody)

    endpoint = ParentTokenEndpoint(base_url)
    control = control_request()
    control_capacity = endpoint.count(control["messages"], control["chat_template_kwargs"])
    frozen = load_json(ROOT / "parent_evidence" / "boundary" / "actor-budget.json")["pre_call"]
    if control_capacity.as_dict() != frozen:
        raise RuntimeError("contemporaneous control packet differs from exact donor receipt")
    if control_capacity.prompt_tokens != EXPECTED_CONTROL_PROMPT_TOKENS or control_capacity.headroom_after_reserve != EXPECTED_CONTROL_HEADROOM:
        raise RuntimeError("control capacity constants differ from exact tokenizer")
    (run_root / "requests" / "control.rendered-prompt.txt").write_bytes(control_capacity.rendered_prompt.encode("utf-8"))

    env = make_environment(CELL, run_root / "world" / "control")
    initial = _candidate(env)
    if initial["candidate_id"] != EXPECTED_CANDIDATE_ID:
        raise RuntimeError("control candidate identity differs from frozen boundary")
    write_json(run_root / "candidates" / "control-initial.json", initial)
    control_body, control_payload, control_ms = _call(base_url, control, run_root, "control")
    parsed = parse_response(type("R", (), {"success": True, "body": canonical_json_bytes(control_payload), "status_code": 200, "transport_error": None})(), CELL)
    if not parsed["valid"]:
        raise RuntimeError(f"control response invalid: {parsed}")
    control_action = parsed["action"]
    control_match = control_action == HISTORICAL_ACTION
    control_result = env.execute(control_action)
    write_json(run_root / "actions" / "control.json", {
        "action": control_action,
        "historical_action": HISTORICAL_ACTION,
        "exact_historical_match": control_match,
        "admitted": control_result.get("accepted") is True,
    })
    write_json(run_root / "results" / "control.json", {
        "action": control_action,
        "result": control_result,
        "result_message": env.result_message(control_action, "h05-control-001", control_result),
    })
    write_json(run_root / "candidates" / "control-terminal.json", _candidate(env))
    write_json(run_root / "budget" / "control.json", {
        "capacity": control_capacity.as_dict(),
        "provider_request_sha256": sha256_bytes(control_body),
        "provider_response_sha256": sha256_bytes(canonical_json_bytes(control_payload)),
    })

    calls = 1
    maintenance_record: dict[str, Any] | None = None
    if control_match:
        maintenance = maintenance_request()
        maintenance_capacity = endpoint.count(
            maintenance["messages"], maintenance["chat_template_kwargs"], MAINTENANCE_MAXIMUM_TOKENS
        )
        if not maintenance_capacity.fits:
            raise RuntimeError("maintenance request does not fit its frozen generation reserve")
        (run_root / "requests" / "maintenance.rendered-prompt.txt").write_bytes(maintenance_capacity.rendered_prompt.encode("utf-8"))
        maintenance_body, maintenance_payload, maintenance_ms = _call(base_url, maintenance, run_root, "maintenance")
        calls += 1
        content, finish_reason, usage = extract_provider_message(maintenance_payload)
        note_tokens = endpoint.count_text(content)
        audit = mechanical_note_audit(content)
        mechanically_qualified = (
            finish_reason == "stop"
            and 0 < note_tokens <= PROGRESS_STATE_MAXIMUM_TOKENS
            and audit["nonempty"]
            and audit["headings_exactly_once"]
            and audit["headings_in_order"]
            and audit["fields_nonempty"]
            and audit["forbidden_surface_absent"]
        )
        maintenance_record = {
            "finish_reason": finish_reason,
            "usage": usage,
            "content": content,
            "content_sha256": sha256_bytes(content.encode("utf-8")),
            "content_size_bytes": len(content.encode("utf-8")),
            "content_tokens": note_tokens,
            "mechanical_audit": audit,
            "mechanically_qualified": mechanically_qualified,
            "direct_safety_audit_required": True,
            "http_duration_ms": maintenance_ms,
            "capacity": maintenance_capacity.as_dict(),
            "provider_request_sha256": sha256_bytes(maintenance_body),
            "provider_response_sha256": sha256_bytes(canonical_json_bytes(maintenance_payload)),
        }
        write_json(run_root / "analysis" / "MAINTENANCE_MECHANICAL_AUDIT.json", maintenance_record)

    result = {
        "schema_version": "bounded-progress-state-stage-a-result-v0",
        "study_id": STUDY_ID,
        "run_id": run_id,
        "standalone_commit": head,
        "source_lock_sha256": authorization["source_lock_sha256"],
        "seed": SEED,
        "model_calls": calls,
        "maximum_model_calls": STAGE_A_MAXIMUM_CALLS,
        "retries": 0,
        "control_exact_historical_match": control_match,
        "control_action": control_action,
        "maintenance_executed": maintenance_record is not None,
        "maintenance_mechanically_qualified": bool(maintenance_record and maintenance_record["mechanically_qualified"]),
        "stage_b_requires_direct_audit_and_new_freeze": True,
        "passed_apparatus_integrity": calls <= STAGE_A_MAXIMUM_CALLS,
    }
    write_json(run_root / "RUN_RESULT.json", result)
    return result
