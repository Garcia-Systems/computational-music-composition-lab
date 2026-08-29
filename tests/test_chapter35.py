import json
from pathlib import Path
import tempfile
import unittest
from composition_lab.chapter34 import RECORDED_B_SELECTION, build_complete_piece
from composition_lab.chapter35 import (DECISION_CATEGORIES, MATERIAL_CATEGORIES,
    build_authorship_audit, render_authorship_report, write_authorship_artifacts)

class Chapter35Tests(unittest.TestCase):
    def test_audit_is_deterministic_canonical_and_non_mutating(self):
        piece=build_complete_piece(); before=piece.flattened()
        self.assertEqual(build_authorship_audit(piece),build_authorship_audit(piece))
        audit=build_authorship_audit(piece)
        self.assertEqual(piece.flattened(),before)
        self.assertEqual(audit["canonical_identity"]["selected_b"],RECORDED_B_SELECTION)
        self.assertLessEqual(set(audit["decision_counts"]),DECISION_CATEGORIES)
        self.assertEqual(set(audit["valid_material_classifications"]),MATERIAL_CATEGORIES)

    def test_generation_selection_revision_rejection_and_lineage(self):
        audit=build_authorship_audit()
        self.assertEqual(audit["candidate_generation"]["selected"],RECORDED_B_SELECTION)
        self.assertNotIn(RECORDED_B_SELECTION,audit["rejected_material"]["b"]["rejected"])
        self.assertEqual(len(audit["rejected_material"]["b"]["rejected"]),5)
        self.assertEqual(audit["revision_records"][0]["requested_by"],"human")
        self.assertIn("motif-a",audit["lineages"]["transformation"][0])

    def test_counterfactuals_and_playback_independence(self):
        c=build_authorship_audit()["counterfactuals"]
        self.assertEqual(c["alternate_b_selection"]["changed_sections"],["b"])
        self.assertTrue(c["alternate_b_selection"]["candidate_pool_unchanged"])
        self.assertTrue(c["without_revision"]["restores_selected_candidate_exactly"])
        self.assertTrue(c["alternate_playback"]["symbolic_score_unchanged"])

    def test_artifacts_are_deterministic_and_avoid_authorship_percentages(self):
        audit=build_authorship_audit()
        with tempfile.TemporaryDirectory() as directory:
            paths=write_authorship_artifacts(audit,Path(directory)); first=[p.read_text() for p in paths]
            write_authorship_artifacts(audit,Path(directory))
            self.assertEqual(first,[p.read_text() for p in paths])
            self.assertEqual(json.loads(paths[0].read_text())["composition_title"],"Converging Paths")
            combined=(paths[0].read_text()+render_authorship_report(audit)).lower()
            self.assertTrue(all(x not in combined for x in ("human_percent","ai_percent","creativity_percent")))
