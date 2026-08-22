from __future__ import annotations

import copy
import json
from typing import Any

from apparatus.canonical import compact_json, sha256_bytes
from apparatus.constants import (
    CELL,
    EXPECTED_CANDIDATE_ID,
    EXPECTED_CANDIDATE_SHA256,
    MAINTENANCE_MAXIMUM_TOKENS,
)
from apparatus.evidence import imported_request


HEADINGS = (
    "CURRENT OBJECTIVE:",
    "COMPLETED OR ESTABLISHED:",
    "UNRESOLVED:",
    "NEXT PROGRESS EVENT:",
    "DO NOT REPEAT:",
)

MAINTENANCE_SYSTEM = """You are in a dedicated bounded progress-state maintenance mode.
Do not take a repository, candidate, mutation, check, or submission action.
Produce only the requested plain-text state for a future actor. The exact task,
source evidence, candidate bytes, and tool results remain authoritative. Your
state is lossy, non-authoritative continuity, not a replacement for exact truth.
Do not output JSON, a code fence, analysis, or commentary outside the five
required fields."""

MAINTENANCE_INSTRUCTION = """Rewrite your current task-control state using exactly these five headings,
each exactly once and each followed by one concise complete sentence:

CURRENT OBJECTIVE:
COMPLETED OR ESTABLISHED:
UNRESOLVED:
NEXT PROGRESS EVENT:
DO NOT REPEAT:

State what task progress has actually occurred and what one observable event
would count as the next progress event. Do not invent source, candidate, check,
or submission facts. Do not take an action. Keep the complete output within 256
tokens."""


def control_request() -> dict[str, Any]:
    return copy.deepcopy(imported_request(CELL))


def maintenance_request() -> dict[str, Any]:
    request = control_request()
    messages = copy.deepcopy(request["messages"])
    if not messages or messages[0].get("role") != "system":
        raise RuntimeError("donor request lacks initial system message")
    messages[0] = {"role": "system", "content": MAINTENANCE_SYSTEM}
    messages.append({"role": "user", "content": MAINTENANCE_INSTRUCTION})
    request["messages"] = messages
    request["max_tokens"] = MAINTENANCE_MAXIMUM_TOKENS
    request.pop("response_format", None)
    return request


def extract_provider_message(payload: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
    choices = payload.get("choices")
    if not isinstance(choices, list) or len(choices) != 1 or not isinstance(choices[0], dict):
        raise ValueError("provider response must contain exactly one choice")
    choice = choices[0]
    message = choice.get("message")
    if not isinstance(message, dict) or message.get("role") != "assistant":
        raise ValueError("provider response lacks one assistant message")
    if message.get("reasoning_content") not in (None, "") or message.get("tool_calls") not in (None, []):
        raise ValueError("maintenance response contains reasoning or tool calls")
    content = message.get("content")
    if not isinstance(content, str):
        raise ValueError("maintenance response lacks text content")
    return content, str(choice.get("finish_reason")), payload.get("usage") or {}


def mechanical_note_audit(content: str) -> dict[str, Any]:
    stripped = content.strip()
    heading_counts = {heading: stripped.count(heading) for heading in HEADINGS}
    positions = [stripped.find(heading) for heading in HEADINGS]
    fields: dict[str, str] = {}
    ordered = all(position >= 0 for position in positions) and positions == sorted(positions)
    if ordered:
        for index, heading in enumerate(HEADINGS):
            start = positions[index] + len(heading)
            end = positions[index + 1] if index + 1 < len(positions) else len(stripped)
            fields[heading] = stripped[start:end].strip()
    forbidden = {
        "json_object": stripped.startswith("{") or stripped.endswith("}"),
        "code_fence": "```" in stripped,
        "action_json": '"action"' in stripped,
    }
    return {
        "nonempty": bool(stripped),
        "heading_counts": heading_counts,
        "headings_exactly_once": all(count == 1 for count in heading_counts.values()),
        "headings_in_order": ordered,
        "fields": fields,
        "fields_nonempty": len(fields) == len(HEADINGS) and all(bool(value) for value in fields.values()),
        "forbidden_surface": forbidden,
        "forbidden_surface_absent": not any(forbidden.values()),
    }


def progress_package_message(content: str, donor_request_sha256: str, maintenance_response_sha256: str) -> dict[str, str]:
    package = {
        "schema_version": "bounded-progress-state-package-v0",
        "lossy_non_authoritative": True,
        "basis": {
            "donor_request_sha256": donor_request_sha256,
            "candidate_id": EXPECTED_CANDIDATE_ID,
            "candidate_file_sha256": EXPECTED_CANDIDATE_SHA256,
            "maintenance_response_sha256": maintenance_response_sha256,
        },
        "progress_state": content.strip(),
        "authority_notice": "Exact task, evidence, candidate, and literal tool results remain authoritative.",
    }
    return {"role": "user", "content": compact_json(package)}


def treated_request(content: str, donor_request_sha256: str, maintenance_response_sha256: str) -> dict[str, Any]:
    request = control_request()
    request["messages"] = copy.deepcopy(request["messages"]) + [
        progress_package_message(content, donor_request_sha256, maintenance_response_sha256)
    ]
    return request


def request_sha256(request: dict[str, Any]) -> str:
    return sha256_bytes(compact_json(request).encode("utf-8"))


def parse_json_bytes(data: bytes) -> dict[str, Any]:
    value = json.loads(data)
    if not isinstance(value, dict):
        raise ValueError("expected JSON object")
    return value
