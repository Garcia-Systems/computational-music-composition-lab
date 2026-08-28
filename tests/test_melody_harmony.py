import tempfile
import unittest
from pathlib import Path

from composition_lab.cli import CHAPTER_12_FILENAMES, chapter_12_spans, run_chapter_12
from composition_lab.events import NoteEvent
from composition_lab.melody_harmony import (
    HarmonicSpan, active_harmony_at, analyze_melody,
    chord_tone_duration_percentage, chord_tone_percentage,
    harmonies_during_event, is_approach_tone, is_chord_tone,
    is_neighbor_tone, is_passing_tone, is_suspension_like,
)


class MelodyHarmonyTests(unittest.TestCase):
    def setUp(self):
        self.c = (60, 64, 67)
        self.span = HarmonicSpan(0, 4, self.c, 1)

    def event(self, pitch, start=0, duration=1):
        return NoteEvent(pitch, start, duration)

    def test_active_harmony_and_boundary(self):
        spans = (HarmonicSpan(0, 2, self.c), HarmonicSpan(2, 2, (65, 69, 72)))
        self.assertIs(active_harmony_at(1.999, spans), spans[0])
        self.assertIs(active_harmony_at(2, spans), spans[1])
        self.assertIsNone(active_harmony_at(4, spans))

    def test_pitch_class_membership(self):
        self.assertTrue(is_chord_tone(72, self.c))
        self.assertTrue(is_chord_tone(76, self.c))
        self.assertFalse(is_chord_tone(62, self.c))

    def test_strict_passing_neighbor_and_approach(self):
        c, d, e, f = map(self.event, (60, 62, 64, 65))
        self.assertTrue(is_passing_tone(c, d, e, self.c))
        self.assertFalse(is_passing_tone(c, d, c, self.c))
        self.assertTrue(is_neighbor_tone(e, f, e, self.c))
        self.assertFalse(is_neighbor_tone(c, d, e, self.c))
        self.assertTrue(is_approach_tone(d, e, self.c))

    def test_overlap_uses_positive_duration(self):
        spans = (HarmonicSpan(0, 2, self.c), HarmonicSpan(2, 2, (65, 69, 72)))
        self.assertEqual(harmonies_during_event(self.event(67, 1, 2), spans), spans)
        self.assertEqual(harmonies_during_event(self.event(67, 0, 2), spans), spans[:1])

    def test_suspension_like_structure(self):
        spans = (HarmonicSpan(0, 2, self.c), HarmonicSpan(2, 2, (65, 69, 72)))
        self.assertTrue(is_suspension_like(self.event(67, 1, 2), self.event(65, 3), spans))

    def test_analysis_and_ambiguous_fallback(self):
        events = (self.event(60, 0), self.event(62, 1), self.event(64, 2))
        relations = analyze_melody(events, (self.span,))
        self.assertEqual([r.relation for r in relations], ["chord-tone", "passing", "chord-tone"])
        ambiguous = analyze_melody((self.event(61, 0),), (self.span,))
        self.assertEqual(ambiguous[0].relation, "other-non-chord-tone")

    def test_context_changes_same_pitch(self):
        event = (self.event(64),)
        c = analyze_melody(event, (HarmonicSpan(0, 1, self.c),))[0]
        d_minor = analyze_melody(event, (HarmonicSpan(0, 1, (62, 65, 69)),))[0]
        self.assertTrue(c.chord_tone)
        self.assertFalse(d_minor.chord_tone)

    def test_alignment_percentages(self):
        relations = analyze_melody(
            (self.event(60, 0, 3), self.event(61, 1, 1)), (self.span,))
        self.assertEqual(chord_tone_percentage(relations), 50)
        self.assertEqual(chord_tone_duration_percentage(relations), 75)

    def test_progression_adapter(self):
        spans = chapter_12_spans()
        self.assertEqual([span.degree for span in spans], [1, 4, 5, 1])
        self.assertEqual(spans[-1].end, 8)

    def test_expected_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = run_chapter_12(Path(directory))
            self.assertEqual(tuple(path.name for path in paths), CHAPTER_12_FILENAMES)
            self.assertTrue(all(path.stat().st_size > 44 for path in paths))


if __name__ == "__main__":
    unittest.main()
