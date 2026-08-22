from __future__ import annotations

import json
from typing import Any

from apparatus.canonical import compact_json
from apparatus.environment import ActionRejected, validate_action
from apparatus.modelio import HttpRecord


ACQUISITION_ACTIONS = {
    "tree", "search", "read", "read_lines", "read_region", "repo_list",
    "repo_catalog", "repo_read_lines", "continue_lines", "repo_search",
    "repo_read", "repo_history",
}


def parse_bare_action(content: str) -> dict[str, Any]:
    stripped = content.strip()
    value, end = json.JSONDecoder().raw_decode(stripped)
    if stripped[end:].strip():
        raise ValueError("assistant response contains trailing content")
    if not isinstance(value, dict):
        raise ValueError("assistant response is not a JSON object")
    return value


def parse_response(response: HttpRecord, cell: str) -> dict[str, Any]:
    if not response.success:
        return {"valid": False, "error": "provider_http_failure", "details": {"status_code": response.status_code, "transport_error": response.transport_error}}
    try:
        payload = json.loads(response.body)
    except Exception as exc:
        return {"valid": False, "error": "invalid_provider_json", "details": str(exc)}
    choices = payload.get("choices") if isinstance(payload, dict) else None
    if not isinstance(choices, list) or len(choices) != 1 or not isinstance(choices[0], dict):
        return {"valid": False, "error": "invalid_choice_count", "details": None}
    choice = choices[0]
    message = choice.get("message")
    if choice.get("finish_reason") != "stop" or not isinstance(message, dict) or message.get("role") != "assistant":
        return {"valid": False, "error": "invalid_assistant_turn", "details": {"finish_reason": choice.get("finish_reason"), "message": message}}
    if message.get("reasoning_content") not in (None, "") or message.get("tool_calls") not in (None, []):
        return {"valid": False, "error": "unexpected_reasoning_or_native_tools", "details": message}
    content = message.get("content")
    if not isinstance(content, str):
        return {"valid": False, "error": "missing_action_content", "details": message}
    try:
        action = validate_action(cell, parse_bare_action(content))
    except (ValueError, json.JSONDecodeError, ActionRejected) as exc:
        return {"valid": False, "error": "invalid_schema_action", "details": f"{type(exc).__name__}: {exc}", "raw_content": content}
    return {
        "valid": True,
        "payload": payload,
        "assistant_message": {"role": "assistant", "content": content},
        "action": action,
        "usage": payload.get("usage"),
        "finish_reason": "stop",
    }


def classify_action(action: dict[str, Any], result: dict[str, Any], messages: list[dict[str, Any]]) -> dict[str, Any]:
    action_name = action.get("action")
    model_visible = "\n".join(str(message.get("content") or "") for message in messages)
    content = result.get("content")
    exact_content_resident = False
    resident_encoding = None
    if isinstance(content, str) and content:
        if content in model_visible:
            exact_content_resident = True
            resident_encoding = "literal_message_content"
        else:
            escaped = json.dumps(content, ensure_ascii=False)[1:-1]
            if escaped in model_visible:
                exact_content_resident = True
                resident_encoding = "json_string_field"
    if action_name in {"patch", "replace_file"}:
        category = "mutation"
    elif action_name == "submit":
        category = "submission"
    elif result.get("accepted") is not True:
        category = "rejected_action"
    elif action_name in ACQUISITION_ACTIONS and exact_content_resident:
        category = "resident_exact_rerequest"
    elif action_name in ACQUISITION_ACTIONS:
        category = "novel_or_nonresident_acquisition"
    else:
        category = "other"
    return {
        "action_key": compact_json(action),
        "category": category,
        "result_content_present": isinstance(content, str),
        "result_content_exactly_resident_before_call": exact_content_resident,
        "resident_encoding": resident_encoding,
        "result_content_size_bytes": len(content.encode("utf-8")) if isinstance(content, str) else None,
    }
