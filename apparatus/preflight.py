from __future__ import annotations

from pathlib import Path
from typing import Any

from apparatus.canonical import compact_json, load_json, sha256_bytes, sha256_file, write_json
from apparatus.constants import (
    EXPECTED_CANDIDATE_ID,
    EXPECTED_CANDIDATE_SHA256,
    EXPECTED_CONTROL_HEADROOM,
    EXPECTED_CONTROL_PROMPT_TOKENS,
    HISTORICAL_ACTION,
    MAINTENANCE_MAXIMUM_TOKENS,
    PROGRESS_PACKAGE_MAXIMUM_INCREMENT,
    PROGRESS_STATE_MAXIMUM_TOKENS,
    PROGRESS_TREATED_MINIMUM_HEADROOM,
    ROOT,
)
from apparatus.custody import donor_receipt
from apparatus.modelio import ParentTokenEndpoint
from apparatus.progress import control_request, maintenance_request, mechanical_note_audit, treated_request


REPRESENTATIVE_NOTE = """CURRENT OBJECTIVE: Update the working model from the two navigation studies.
COMPLETED OR ESTABLISHED: The governing studies, current patch effect, and two selected exact focus spans are resident.
UNRESOLVED: The current candidate still requires an integrated grounded continuation.
NEXT PROGRESS EVENT: An admitted candidate mutation would be the next observable progress event.
DO NOT REPEAT: Do not reread the exact second focus that was just delivered."""


def run_preflight(base_url: str, server: Path, tokenizer: Path) -> dict[str, Any]:
    endpoint = ParentTokenEndpoint(base_url)
    materialization = donor_receipt()
    write_json(ROOT / "provenance" / "PARENT_MATERIALIZATION_RECEIPT.json", materialization)

    control = control_request()
    maintenance = maintenance_request()
    control_capacity = endpoint.count(control["messages"], control["chat_template_kwargs"])
    maintenance_capacity = endpoint.count(maintenance["messages"], maintenance["chat_template_kwargs"], MAINTENANCE_MAXIMUM_TOKENS)
    representative_tokens = endpoint.count_text(REPRESENTATIVE_NOTE)
    representative = treated_request(REPRESENTATIVE_NOTE, "a" * 64, "b" * 64)
    representative_capacity = endpoint.count(representative["messages"], representative["chat_template_kwargs"])
    representative_increment = representative_capacity.prompt_tokens - control_capacity.prompt_tokens

    donor_budget = load_json(ROOT / "parent_evidence" / "boundary" / "actor-budget.json")["pre_call"]
    donor_rendered = ROOT / "parent_evidence" / "boundary" / "actor-rendered-prompt.txt"
    control_exact = (
        control_capacity.as_dict() == donor_budget
        and sha256_bytes(control_capacity.rendered_prompt.encode("utf-8")) == sha256_file(donor_rendered)
        and control_capacity.prompt_tokens == EXPECTED_CONTROL_PROMPT_TOKENS
        and control_capacity.headroom_after_reserve == EXPECTED_CONTROL_HEADROOM
    )
    note_audit = mechanical_note_audit(REPRESENTATIVE_NOTE)
    boundary = {
        "schema_version": "bounded-progress-state-boundary-audit-v0",
        "donor_request_sha256": sha256_bytes(compact_json(control).encode("utf-8")),
        "messages": len(control["messages"]),
        "candidate_id": EXPECTED_CANDIDATE_ID,
        "candidate_file_sha256": EXPECTED_CANDIDATE_SHA256,
        "historical_action": HISTORICAL_ACTION,
        "historical_result_delivered": True,
        "pending_update": False,
        "four_governing_sources_resident": True,
        "two_model_selected_focus_results_resident": True,
        "control_exact": control_exact,
    }
    write_json(ROOT / "BOUNDARY_AUDIT.json", boundary)
    write_json(ROOT / "TREATMENT_DELTA.json", {
        "schema_version": "bounded-progress-state-treatment-delta-v0",
        "control": "byte-identical eight-message accumulated-focus actor packet",
        "maintenance": ["replace actor system with dedicated maintenance system", "append one maintenance instruction", "remove actor response grammar", "set maximum completion to 384"],
        "actor_treatment": ["append one complete bound progress-state package"],
        "held_fixed": ["all eight actor messages", "task and exact evidence", "candidate identity and bytes", "action schema and executor", "model/runtime/sampler/seed/reasoning", "context and 4096-token actor response reserve"],
        "causal_unit": "complete progress-state package, not semantic prose alone",
    })
    write_json(ROOT / "CAPACITY_PREFLIGHT.json", {
        "schema_version": "bounded-progress-state-capacity-preflight-v0",
        "control": control_capacity.as_dict(),
        "maintenance": maintenance_capacity.as_dict(),
        "representative_state": {"content_tokens": representative_tokens, "mechanical_contract": note_audit, "treated_capacity": representative_capacity.as_dict(), "marginal_prompt_tokens": representative_increment, "not_a_measured_or_frozen_treatment": True},
        "measured_state_gate": {"maximum_state_tokens": PROGRESS_STATE_MAXIMUM_TOKENS, "maximum_package_increment_tokens": PROGRESS_PACKAGE_MAXIMUM_INCREMENT, "minimum_treated_headroom_tokens": PROGRESS_TREATED_MINIMUM_HEADROOM, "exact_postproduction_preflight_required": True},
    })
    checks = {
        "materialization_exact": materialization["all_byte_equivalent"],
        "control_exact": control_exact,
        "control_fits": control_capacity.fits,
        "maintenance_fits_384_reserve": maintenance_capacity.fits,
        "representative_note_within_256": representative_tokens <= PROGRESS_STATE_MAXIMUM_TOKENS,
        "representative_package_within_700": representative_increment <= PROGRESS_PACKAGE_MAXIMUM_INCREMENT,
        "representative_treated_headroom_sufficient": representative_capacity.headroom_after_reserve >= PROGRESS_TREATED_MINIMUM_HEADROOM,
        "original_actor_messages_preserved": representative["messages"][:-1] == control["messages"],
        "representative_note_contract": all([note_audit["headings_exactly_once"], note_audit["headings_in_order"], note_audit["fields_nonempty"], note_audit["forbidden_surface_absent"]]),
        "no_chat_completion_in_preflight": True,
    }
    result = {
        "schema_version": "bounded-progress-state-offline-preflight-v0",
        "verification_passed": all(checks.values()),
        "checks": checks,
        "tokenizer": {"server": str(server), "projection": str(tokenizer)},
        "tokenizer_calls": {"apply_template": endpoint.apply_calls, "tokenize": endpoint.tokenize_calls},
    }
    write_json(ROOT / "OFFLINE_PREFLIGHT.json", result)
    return result
