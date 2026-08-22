from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STUDY_ID = "qwen38-bounded-progress-state-utility-v0"
BRANCH = "codex/qwen38-bounded-progress-state-utility-v0"

DONOR_ROOT = Path(r"E:\qwen38-accumulated-exact-focus-v0")
DONOR_REPOSITORY = "ScrappyTom/qwen38-accumulated-exact-focus-v0"
DONOR_COMMIT = "6bed7b208174646b803405fdce1a83a9432fba88"
DONOR_RUN = "runs/2026-08-21-sealed-accumulated-exact-focus-v0"
PROGRAM_ROOT = Path(r"E:\bounded-context-experimental-program")
PROGRAM_REPOSITORY = "ScrappyTom/bounded-context-experimental-program"
PROGRAM_COMMIT = "5ee502ada15e9a1abc012fa1ea3b1ff59a251c38"
SOURCE_COMMIT = "f8c93e5ad33c8dd235c418df6561ba022d9077fb"

CELL = "effect-patch-s42"
SEED = 42
TARGET = "QWEN_RELATION_ACTION_WORKING_MODEL.md"
CONTEXT_TOKENS = 25_088
RESPONSE_RESERVE = 4_096
MAXIMUM_PROMPT_TOKENS = CONTEXT_TOKENS - RESPONSE_RESERVE
MAINTENANCE_MAXIMUM_TOKENS = 384
PROGRESS_STATE_MAXIMUM_TOKENS = 256
PROGRESS_PACKAGE_MAXIMUM_INCREMENT = 700
PROGRESS_TREATED_MINIMUM_HEADROOM = 193
STAGE_A_MAXIMUM_CALLS = 2
STAGE_B_MAXIMUM_CALLS = 3

CELLS = {
    CELL: {
        "ordinal": 1,
        "seed": SEED,
        "endpoint_type": "accepted_adjacent_resident_line_read",
        "endpoint_directory": CELL,
        "inherited_prompt_tokens": 20_099,
    }
}

HISTORICAL_ACTION = {
    "action": "read_lines",
    "path": TARGET,
    "start_line": 860,
    "end_line": 937,
}
EXPECTED_CONTROL_PROMPT_TOKENS = 20_099
EXPECTED_CONTROL_HEADROOM = 893
EXPECTED_CANDIDATE_ID = "38893b4df5afc252a356ff5ab79a1dcda6330b7934a252a67d2759499eb4aac6"
EXPECTED_CANDIDATE_SHA256 = "888c142abcad4c3bd9081960bdb18b7402be6415c03b456033ed3c7aed134d39"

SOURCE_PATHS = (
    "experiments/large-world-source-navigation-v0/runs/2026-08-18-sealed-bank-v0/RESULTS.md",
    "experiments/large-world-source-navigation-v0/runs/2026-08-18-sealed-bank-v0/DIRECT_TRANSCRIPT_AUDIT.md",
    "experiments/large-world-navigation-continuity-v0/runs/2026-08-18-sealed-bank-v0/RESULTS.md",
    "experiments/large-world-navigation-continuity-v0/runs/2026-08-18-sealed-bank-v0/DIRECT_TRANSCRIPT_AUDIT.md",
)

EXPECTED_SERVER_SHA256 = "5f1f831bc21dcbff4ca40e05cb59dbcbc0802d20b2046540bbbf3bd45cd61610"
EXPECTED_MODEL_SHA256 = "d416fa422c9035605c778f60d90a94b288c38b4f9ec2126b58ef938ce8d5f716"
EXPECTED_MODEL_SIZE = 11_141_912_032
TOKENIZER_PROJECTION_SHA256 = "7047272e809b62b5c68b6427a349cba78b2f45109de04350d48f0338db68eef3"
MODEL_ALIAS = "qwen38-ad25q8-world-join"
LLAMA_BUILD = "b10434-7e4c0a968"

PARENT_EVIDENCE = ROOT / "parent_evidence"


def endpoint_root(cell: str) -> Path:
    if cell != CELL:
        raise ValueError(f"unknown cell: {cell}")
    return PARENT_EVIDENCE / "boundary"


def parent_candidate_path(cell: str) -> Path:
    if cell != CELL:
        raise ValueError(f"unknown cell: {cell}")
    return PARENT_EVIDENCE / "candidate" / TARGET


DONOR_IMPORTED_FILES = {
    "parent_evidence/boundary/actor-request.json": f"{DONOR_RUN}/cells/02-effect-patch-s42/requests/call-01.json",
    "parent_evidence/boundary/actor-rendered-prompt.txt": f"{DONOR_RUN}/cells/02-effect-patch-s42/requests/call-01.rendered-prompt.txt",
    "parent_evidence/boundary/actor-response.json": f"{DONOR_RUN}/cells/02-effect-patch-s42/responses/call-01.json",
    "parent_evidence/boundary/actor-action.json": f"{DONOR_RUN}/cells/02-effect-patch-s42/actions/call-01.json",
    "parent_evidence/boundary/actor-result.json": f"{DONOR_RUN}/cells/02-effect-patch-s42/results/call-01.json",
    "parent_evidence/boundary/actor-budget.json": f"{DONOR_RUN}/cells/02-effect-patch-s42/budget/call-01.json",
    "parent_evidence/boundary/donor-SEAL.json": f"{DONOR_RUN}/SEAL.json",
    "parent_evidence/boundary/donor-REPLAY.json": f"{DONOR_RUN}/replay/REPLAY.json",
    "parent_evidence/boundary/RESULTS.md": "RESULTS.md",
    "parent_evidence/boundary/DIRECT_TRANSCRIPT_AUDIT.md": "DIRECT_TRANSCRIPT_AUDIT.md",
    "parent_evidence/boundary/VERIFICATION.json": "VERIFICATION.json",
    "parent_evidence/candidate/QWEN_RELATION_ACTION_WORKING_MODEL.md": f"{DONOR_RUN}/cells/02-effect-patch-s42/world/candidate/QWEN_RELATION_ACTION_WORKING_MODEL.md",
    "parent_evidence/runtime/MODEL_PROFILE_LOCK.json": "provenance/MODEL_PROFILE_LOCK.json",
    "parent_evidence/runtime/runtime-custody.json": f"{DONOR_RUN}/model/runtime-custody.json",
}
for _path in SOURCE_PATHS:
    DONOR_IMPORTED_FILES[f"parent_evidence/source/{_path}"] = f"parent_evidence/source/{_path}"

PROGRAM_IMPORTED_FILES = {
    "parent_evidence/program/HANDOFF.md": "NEXT_EXPERIMENT_H05_BOUNDED_PROGRESS_STATE_UTILITY.md",
    "parent_evidence/program/ELIGIBILITY.md": "audits/H05_PROGRESS_STATE_ELIGIBILITY.md",
    "parent_evidence/program/ELIGIBILITY.json": "audits/H05_PROGRESS_STATE_ELIGIBILITY.json",
}
