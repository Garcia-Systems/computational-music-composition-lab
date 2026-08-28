import tempfile
import unittest
from pathlib import Path

from composition_lab.chords import (
    MAJOR_TRIAD, arpeggiate_chord, build_chord, chord_events,
    chord_pitch_classes, diminished_triad, invert_chord, major_triad,
    minor_triad, triad_from_scale_degree, triad_quality,
)
from composition_lab.cli import CHAPTER_08_FILENAMES, run_chapter_08
from composition_lab.scales import MAJOR


class ChordTests(unittest.TestCase):
    def test_triads_apply_interval_patterns(self):
        self.assertEqual(major_triad(60), (60, 64, 67))
        self.assertEqual(minor_triad(60), (60, 63, 67))
        self.assertEqual(diminished_triad(60), (60, 63, 66))
        self.assertEqual(build_chord(65, MAJOR_TRIAD), (65, 69, 72))

    def test_invalid_pitch_and_root_position_contract(self):
        with self.assertRaises(ValueError):
            major_triad(125)
        with self.assertRaises(ValueError):
            build_chord(60, (0, 7, 4))
        with self.assertRaises(ValueError):
            invert_chord((64, 60, 67), 1)

    def test_inversions_and_pitch_classes(self):
        root = major_triad(60)
        self.assertEqual(invert_chord(root, 0), root)
        self.assertEqual(invert_chord(root, 1), (64, 67, 72))
        self.assertEqual(invert_chord(root, 2), (67, 72, 76))
        self.assertEqual(chord_pitch_classes(root), chord_pitch_classes(invert_chord(root, 1)))
        with self.assertRaises(ValueError):
            invert_chord(root, 3)

    def test_quality_has_narrow_root_position_contract(self):
        self.assertEqual(triad_quality((60, 64, 67)), "major")
        self.assertEqual(triad_quality((60, 63, 67)), "minor")
        self.assertEqual(triad_quality((60, 63, 66)), "diminished")
        self.assertEqual(triad_quality((60, 65, 67)), "unknown")
        self.assertEqual(triad_quality((60, 64, 67, 72)), "unknown")

    def test_chord_events_share_onset_and_duration(self):
        events = chord_events((60, 64, 67), start=1, duration=2, velocity=80)
        self.assertEqual({event.start for event in events}, {1})
        self.assertEqual({event.duration for event in events}, {2})
        self.assertEqual(tuple(event.pitch for event in events), (60, 64, 67))

    def test_arpeggio_places_same_pitches_sequentially(self):
        block = chord_events((60, 64, 67))
        broken = arpeggiate_chord((60, 64, 67), start=1, step=.5)
        self.assertEqual(tuple(event.pitch for event in block), tuple(event.pitch for event in broken))
        self.assertEqual(tuple(event.start for event in block), (0, 0, 0))
        self.assertEqual(tuple(event.start for event in broken), (1, 1.5, 2))

    def test_diatonic_triad_construction_wraps_upward(self):
        expected = {
            1: (60, 64, 67), 2: (62, 65, 69),
            5: (67, 71, 74), 7: (71, 74, 77),
        }
        for degree, pitches in expected.items():
            self.assertEqual(triad_from_scale_degree(60, MAJOR, degree), pitches)

    def test_chapter_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = run_chapter_08(Path(directory))
            self.assertEqual(tuple(path.name for path in paths), CHAPTER_08_FILENAMES)
            self.assertTrue(all(path.exists() and path.stat().st_size > 44 for path in paths))


if __name__ == "__main__":
    unittest.main()
