import tempfile
import unittest
from pathlib import Path

from composition_lab.bass import (
    bass_chord_role, bass_from_progression, connect_bass_targets,
    harmonic_root_pitch_classes, nearest_bass_pitch, pitches_for_class,
    root_in_register,
)
from composition_lab.cli import CHAPTER_14_FILENAMES, run_chapter_14
from composition_lab.groove import GroovePattern
from composition_lab.melody import melodic_profile
from composition_lab.scales import MAJOR


class BassTests(unittest.TestCase):
    def test_roots_come_from_degree_metadata(self):
        self.assertEqual(harmonic_root_pitch_classes(60, MAJOR, (1, 4, 5, 1)), (0, 5, 7, 0))

    def test_register_placement_and_validation(self):
        self.assertEqual(root_in_register(0, 28, 60, 36), 36)
        self.assertEqual(pitches_for_class(0, 28, 60), (36, 48, 60))
        with self.assertRaises(ValueError):
            root_in_register(0, 61, 60)
        with self.assertRaises(ValueError):
            root_in_register(1, 60, 60)

    def test_nearest_selection_is_deterministic_and_in_range(self):
        self.assertEqual(nearest_bass_pitch(7, 36, 28, 60), 31)
        line = [36]
        for pc in (7, 9, 5):
            line.append(nearest_bass_pitch(pc, line[-1], 28, 60))
        self.assertEqual(line, [36, 31, 33, 29])
        self.assertTrue(all(28 <= pitch <= 60 for pitch in line))

    def test_triad_roles(self):
        chord = (60, 64, 67)
        self.assertEqual([bass_chord_role(p, chord, 0) for p in (36, 40, 43, 38)],
                         ["root", "third", "fifth", "non-chord-tone"])

    def test_onsets_repetition_and_strategies(self):
        pattern = GroovePattern(4, 2, (0, 2, 4, 6))
        roots = bass_from_progression(60, MAJOR, (1,), (4,), pattern)
        varied = bass_from_progression(60, MAJOR, (1,), (4,), pattern,
                                       strategy="roots_and_fifths")
        self.assertEqual(tuple(e.start for e in roots), (0, 1, 2, 3))
        self.assertEqual(tuple(e.pitch % 12 for e in roots), (0, 0, 0, 0))
        self.assertEqual(tuple(e.pitch % 12 for e in varied), (0, 7, 0, 7))

    def test_passing_pedal_and_profile(self):
        self.assertEqual(connect_bass_targets(36, 41, (0, 2, 4, 5, 7, 9, 11)),
                         (36, 38, 40, 41))
        pedal = bass_from_progression(60, MAJOR, (1, 4, 5, 1), (4, 4, 4, 4))
        held = tuple(type(e)(36, e.start, e.duration, e.velocity) for e in pedal)
        self.assertEqual(tuple(e.pitch for e in held), (36,) * 4)
        self.assertEqual(melodic_profile(tuple(e.pitch for e in held)).repeats, 3)

    def test_expected_audio_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = run_chapter_14(Path(directory))
            self.assertEqual(tuple(path.name for path in paths), CHAPTER_14_FILENAMES)
            self.assertTrue(all(path.exists() and path.stat().st_size > 44 for path in paths))


if __name__ == "__main__":
    unittest.main()
