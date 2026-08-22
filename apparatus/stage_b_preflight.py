from __future__ import annotations

from typing import Any

from apparatus.canonical import load_json, sha256_bytes, write_json
from apparatus.constants import (
    EXPECTED_CONTROL_HEADROOM,
    EXPECTED_CONTROL_PROMPT_TOKENS,
    PROGRESS_PACKAGE_MAXIMUM_INCREMENT,
    PROGRESS_STATE_MAXIMUM_TOKENS,
    PROGRESS_TREATED_MINIMUM_HEADROOM,
    ROOT,
    STUDY_ID,
)
from apparatus.modelio import ParentTokenEndpoint
from apparatus.progress import control_request, progress_package_message, treated_request


STAGE_A_RUN_ID = "2026-08-21-sealed-progress-stage-a-v0"


def run_stage_b_preflight(base_url: str) -> dict[str, Any]:
    run_root = ROOT / "runs" / STAGE_A_RUN_ID
    maintenance = load_json(run_root / "analysis" / "MAINTENANCE_MECHANICAL_AUDIT.json")
    direct = load_json(ROOT / "STAGE_A_DIRECT_AUDIT.json")
    boundary = load_json(ROOT / "BOUNDARY_AUDIT.json")
    if not maintenance["mechanically_qualified"] or not direct["stage_b_semantically_eligible"]:
        raise RuntimeError("Stage A qualification gate did not pass")

    content = maintenance["content"]
    donor_hash = boundary["donor_request_sha256"]
    response_hash = maintenance["provider_response_sha256"]
    package = progress_package_message(content, donor_hash, response_hash)
    treated = treated_request(content, donor_hash, response_hash)
    control = control_request()

    endpoint = ParentTokenEndpoint(base_url)
    control_capacity = endpoint.count(control["messages"], control["chat_template_kwargs"])
    treated_capacity = endpoint.count(treated["messages"], treated["chat_template_kwargs"])
    state_tokens = endpoint.count_text(content)
    package_content_tokens = endpoint.count_text(package["content"])
    increment = treated_capacity.prompt_tokens - control_capacity.prompt_tokens
    checks = {
        "control_prompt_tokens_exact": control_capacity.prompt_tokens == EXPECTED_CONTROL_PROMPT_TOKENS,
        "control_headroom_exact": control_capacity.headroom_after_reserve == EXPECTED_CONTROL_HEADROOM,
        "state_tokens_match_stage_a": state_tokens == maintenance["content_tokens"],
        "state_within_256": 0 < state_tokens <= PROGRESS_STATE_MAXIMUM_TOKENS,
        "all_original_messages_preserved": treated["messages"][:-1] == control["messages"],
        "exactly_one_package_message_appended": len(treated["messages"]) == len(control["messages"]) + 1,
        "package_increment_within_700": increment <= PROGRESS_PACKAGE_MAXIMUM_INCREMENT,
        "treated_headroom_at_least_193": treated_capacity.headroom_after_reserve >= PROGRESS_TREATED_MINIMUM_HEADROOM,
        "treated_request_fits": treated_capacity.fits,
    }
    receipt = {
        "schema_version": "bounded-progress-state-stage-b-package-preflight-v0",
        "study_id": STUDY_ID,
        "stage_a_run_id": STAGE_A_RUN_ID,
        "state": {
            "content_sha256": maintenance["content_sha256"],
            "content_tokens": state_tokens,
            "provider_response_sha256": response_hash,
        },
        "package": {
            "message": package,
            "content_sha256": sha256_bytes(package["content"].encode("utf-8")),
            "content_tokens": package_content_tokens,
            "marginal_prompt_tokens": increment,
            "payload_to_prompt_increment_ratio": state_tokens / increment,
        },
        "control_capacity": control_capacity.as_dict(),
        "treated_capacity": treated_capacity.as_dict(),
        "checks": checks,
        "verification_passed": all(checks.values()),
        "tokenizer_calls": {"apply_template": endpoint.apply_calls, "tokenize": endpoint.tokenize_calls},
        "chat_completions_called": False,
    }
    write_json(ROOT / "PROGRESS_STATE_PACKAGE.json", {
        "schema_version": "bounded-progress-state-frozen-package-v0",
        "study_id": STUDY_ID,
        "stage_a_run_id": STAGE_A_RUN_ID,
        "message": package,
        "state_content_sha256": maintenance["content_sha256"],
        "maintenance_provider_response_sha256": response_hash,
        "semantic_repair_performed": False,
    })
    write_json(ROOT / "STAGE_B_TREATED_REQUEST.json", treated)
    write_json(ROOT / "STAGE_B_PACKAGE_PREFLIGHT.json", receipt)
    rendered = ROOT / "preflight" / "stage-b-treated.rendered-prompt.txt"
    rendered.parent.mkdir(parents=True, exist_ok=True)
    rendered.write_bytes(treated_capacity.rendered_prompt.encode("utf-8"))
    return receipt
