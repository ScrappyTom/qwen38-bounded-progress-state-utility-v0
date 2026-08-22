from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from apparatus.canonical import load_json, sha256_file
from apparatus.constants import (
    CELL,
    EXPECTED_CANDIDATE_ID,
    EXPECTED_CANDIDATE_SHA256,
    HISTORICAL_ACTION,
    ROOT,
    SOURCE_PATHS,
)
from apparatus.custody import donor_receipt
from apparatus.environment import make_environment
from apparatus.evidence import imported_request, source_file
from apparatus.progress import HEADINGS, control_request, maintenance_request, mechanical_note_audit, treated_request


GOOD_NOTE = """CURRENT OBJECTIVE: Update the working model from the two navigation studies.
COMPLETED OR ESTABLISHED: The governing studies and current candidate material have been inspected.
UNRESOLVED: The candidate still needs a grounded integrated update.
NEXT PROGRESS EVENT: An admitted candidate mutation would constitute the next progress event.
DO NOT REPEAT: Do not reread the exact focus that was just delivered."""


class ApparatusTests(unittest.TestCase):
    def test_materialization_is_exact(self) -> None:
        receipt = donor_receipt()
        self.assertTrue(receipt["all_byte_equivalent"])
        self.assertGreaterEqual(receipt["file_count"], 20)

    def test_control_is_exact_import(self) -> None:
        self.assertEqual(control_request(), imported_request(CELL))
        self.assertEqual(len(control_request()["messages"]), 8)

    def test_boundary_has_no_pending_update(self) -> None:
        messages = control_request()["messages"]
        self.assertEqual(messages[-1]["role"], "user")
        self.assertIn("EXACT FOCUS RESULT", messages[-1]["content"])
        self.assertEqual(messages[-2]["role"], "assistant")

    def test_maintenance_delta_is_narrow(self) -> None:
        control = control_request()
        maintenance = maintenance_request()
        self.assertEqual(maintenance["messages"][1:-1], control["messages"][1:])
        self.assertNotEqual(maintenance["messages"][0], control["messages"][0])
        self.assertNotIn("response_format", maintenance)
        for key in (set(control) & set(maintenance)) - {"messages", "max_tokens", "response_format"}:
            self.assertEqual(control[key], maintenance[key])

    def test_note_mechanical_contract(self) -> None:
        audit = mechanical_note_audit(GOOD_NOTE)
        self.assertTrue(audit["headings_exactly_once"])
        self.assertTrue(audit["headings_in_order"])
        self.assertTrue(audit["fields_nonempty"])
        self.assertTrue(audit["forbidden_surface_absent"])
        self.assertEqual(tuple(audit["heading_counts"]), HEADINGS)

    def test_package_preserves_all_actor_messages(self) -> None:
        control = control_request()
        treated = treated_request(GOOD_NOTE, "a" * 64, "b" * 64)
        self.assertEqual(treated["messages"][:-1], control["messages"])
        self.assertEqual(treated["messages"][-1]["role"], "user")
        self.assertIn("bounded-progress-state-package-v0", treated["messages"][-1]["content"])

    def test_environment_replays_historical_action(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            env = make_environment(CELL, Path(temp) / "world")
            self.assertEqual(env.snapshot()["candidate_id"], EXPECTED_CANDIDATE_ID)
            self.assertEqual(sha256_file(env.candidate_root / "QWEN_RELATION_ACTION_WORKING_MODEL.md"), EXPECTED_CANDIDATE_SHA256)
            result = env.execute(HISTORICAL_ACTION)
            donor = load_json(ROOT / "parent_evidence" / "boundary" / "actor-result.json")["result"]
            self.assertEqual(result, donor)

    def test_all_governing_sources_are_materialized(self) -> None:
        for path in SOURCE_PATHS:
            self.assertTrue(source_file(path).is_file(), path)


if __name__ == "__main__":
    unittest.main()
