import json
import tempfile
import unittest
from pathlib import Path

from composition_lab.chapter33 import (DecisionCategory, RECORDED_B_SELECTION,
    build_chapter_33_study, generate_candidates, write_artifacts)


class Chapter33Tests(unittest.TestCase):
    def test_candidates_are_stable_unique_and_objectively_valid(self):
        first = generate_candidates(2026)
        self.assertEqual(first, generate_candidates(2026))
        self.assertEqual(len({item.id for item in first}), len(first))
        self.assertTrue(all(all(item.constraints.values()) for item in first))
        self.assertNotEqual(first, generate_candidates(2027))

    def test_selection_is_downstream_and_rejected_candidates_remain(self):
        default = build_chapter_33_study()
        alternate = build_chapter_33_study(selected_candidate_id="candidate-02")
        self.assertEqual(default.candidates, alternate.candidates)
        self.assertIn(RECORDED_B_SELECTION, {item.id for item in default.candidates})
        self.assertEqual(len(default.candidates), 4)

    def test_ledger_categories_ids_and_references(self):
        study = build_chapter_33_study()
        self.assertEqual(len({item.id for item in study.ledger}), len(study.ledger))
        self.assertTrue(all(item.category in DecisionCategory for item in study.ledger))
        derived = [item for item in study.ledger if item.id in
                   {"bass-events", "groove-events", "event-placement", "osc-conversion"}]
        self.assertTrue(all(item.category is DecisionCategory.DERIVED for item in derived))
        self.assertEqual(next(item for item in study.ledger if item.id == "b-selection").selection,
                         RECORDED_B_SELECTION)

    def test_revision_changes_only_documented_approach_then_reduces_attacks(self):
        study = build_chapter_33_study()
        before, after = study.selected_before_revision, study.revised_b
        self.assertEqual(before[:-2], after[:-1])
        self.assertEqual(after[-1].pitch, 62)
        self.assertEqual(after[-1].duration, 2)
        self.assertEqual(after[-1].start, 14)

    def test_artifacts_are_deterministic_and_have_no_timestamp(self):
        study = build_chapter_33_study()
        with tempfile.TemporaryDirectory() as left, tempfile.TemporaryDirectory() as right:
            write_artifacts(study, Path(left)); write_artifacts(study, Path(right))
            for name in ("chapter_33_brief.json", "chapter_33_candidates.json",
                         "chapter_33_decision_ledger.json", "chapter_33_manifest.json",
                         "chapter_33_human_algorithm_study.json"):
                a, b = Path(left, name).read_bytes(), Path(right, name).read_bytes()
                self.assertEqual(a, b)
                self.assertNotIn("timestamp", json.loads(a))


if __name__ == "__main__":
    unittest.main()
