import unittest

from composition_lab.chapter16 import chapter_16_passages, chapter_16_scores
from composition_lab.events import NoteEvent
from composition_lab.passages import (
    append_passages, compare_events, passage_duration, place_after,
    repeat_passage, variation_inventory,
)


class PassageTests(unittest.TestCase):
    def test_duration_normalization_and_placement(self):
        source = (NoteEvent(60, 3, 2), NoteEvent(64, 5, 1))
        self.assertEqual(passage_duration(source), 3)
        placed = place_after(source, (NoteEvent(67, 9, 2),))
        self.assertEqual(tuple(e.start for e in placed), (0, 2, 3))
        self.assertEqual(passage_duration(placed), 5)

    def test_literal_repetition_timing_and_immutability(self):
        source = (NoteEvent(60, 2, 8, 77),)
        before = source
        repeated = repeat_passage(source, 2)
        self.assertEqual(tuple(e.start for e in repeated), (0, 8))
        self.assertEqual(passage_duration(repeated), 16)
        self.assertEqual(source, before)

    def test_one_variable_event_facts(self):
        p = chapter_16_passages()
        pitch = compare_events(p["A"].events, p["A_pitch"].events)
        rhythm = compare_events(p["A"].events, p["A_rhythm"].events)
        self.assertFalse(pitch.pitch_sequence_equal)
        self.assertTrue(pitch.onset_sequence_equal and pitch.duration_sequence_equal)
        self.assertTrue(rhythm.pitch_sequence_equal)
        self.assertFalse(rhythm.onset_sequence_equal and rhythm.duration_sequence_equal)

    def test_texture_preserves_core_and_inventory_is_factual(self):
        p = chapter_16_passages()
        self.assertEqual(p["A_thin"].events[:8], p["A_texture"].events[:8])
        facts = variation_inventory(("texture", "register"))
        self.assertTrue(facts["texture"] and facts["register"])
        self.assertFalse(facts["pitch"])

    def test_return_placements_and_capstone(self):
        p = chapter_16_passages()
        aba = append_passages(p["A"], p["B"], p["A"])
        aba_prime = append_passages(p["A"], p["B"], p["A_ending"])
        self.assertEqual(passage_duration(aba), 24)
        self.assertEqual(tuple(e.start for e in aba[16:24]), tuple(range(16, 24)))
        self.assertEqual(tuple(e.start for e in aba_prime[16:24]), tuple(range(16, 24)))
        self.assertEqual(passage_duration(chapter_16_scores()["development_capstone"]), 32)

    def test_expected_artifacts_have_scores(self):
        scores = chapter_16_scores()
        self.assertEqual(len(scores), 25)
        self.assertIn("literal_repetition", scores)
        self.assertIn("A_B_A_prime_study", scores)


if __name__ == "__main__":
    unittest.main()
