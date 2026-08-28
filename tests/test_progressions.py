import tempfile
import unittest
from pathlib import Path

from composition_lab.cli import CHAPTER_09_FILENAMES, run_chapter_09
from composition_lab.progressions import (
    progression_chords, progression_duration, progression_events,
    progression_roman_numerals, progression_starts, repeat_progression,
    roman_numeral_for_degree, root_sequence,
)
from composition_lab.scales import MAJOR


class ProgressionTests(unittest.TestCase):
    def test_validation_rejects_bad_degrees_and_durations(self):
        for degrees in ((), (0,), (8,)):
            with self.assertRaises(ValueError):
                progression_events(60, MAJOR, degrees, (1.0,) * len(degrees))
        with self.assertRaises(ValueError):
            progression_events(60, MAJOR, (1, 4), (1.0,))
        with self.assertRaises(ValueError):
            progression_events(60, MAJOR, (1,), (0.0,))
        with self.assertRaises(TypeError):
            progression_events(60, MAJOR, (True,), (1.0,))

    def test_starts_and_total_span_follow_durations(self):
        durations = (2, 2, 4, 2)
        self.assertEqual(progression_starts(durations), (0, 2, 4, 8))
        self.assertEqual(progression_duration(durations), 10)

    def test_diatonic_resolution_and_roman_mapping(self):
        self.assertEqual(
            progression_chords(60, MAJOR, (1, 5, 6, 4)),
            ((60, 64, 67), (67, 71, 74), (69, 72, 76), (65, 69, 72)),
        )
        self.assertEqual(
            progression_roman_numerals(60, MAJOR, range(1, 8)),
            ("I", "ii", "iii", "IV", "V", "vi", "vii°"),
        )
        self.assertEqual(roman_numeral_for_degree(7, "diminished"), "vii°")

    def test_transposition_preserves_degrees_and_changes_roots(self):
        degrees = (1, 4, 5, 1)
        self.assertEqual(root_sequence(60, MAJOR, degrees), (60, 65, 67, 60))
        self.assertEqual(root_sequence(65, MAJOR, degrees), (65, 70, 72, 65))
        self.assertEqual(root_sequence(67, MAJOR, degrees), (67, 72, 74, 67))

    def test_chord_events_share_each_change_onset(self):
        events = progression_events(60, MAJOR, (1, 4, 5, 1), (2, 2, 4, 2))
        self.assertEqual(len(events), 12)
        self.assertEqual(tuple(events[index].start for index in range(0, 12, 3)), (0, 2, 4, 8))
        self.assertEqual({event.start for event in events[3:6]}, {2})
        self.assertEqual({event.duration for event in events[6:9]}, {4})

    def test_harmonic_rhythm_changes_timing_not_pitch_pattern(self):
        slow = progression_events(60, MAJOR, (1, 4, 5, 1), (4,) * 4)
        fast = progression_events(60, MAJOR, (1, 4, 5, 1), (1,) * 4)
        self.assertEqual(tuple(e.pitch for e in slow), tuple(e.pitch for e in fast))
        self.assertEqual(progression_duration((4,) * 4), 16)
        self.assertEqual(progression_duration((1,) * 4), 4)

    def test_repetition_repeats_structure_and_rhythm(self):
        degrees, durations = repeat_progression((1, 5, 6, 4), (2,) * 4, 2)
        self.assertEqual(degrees, (1, 5, 6, 4) * 2)
        self.assertEqual(durations, (2,) * 8)
        self.assertEqual(progression_duration(durations), 16)
        with self.assertRaises(ValueError):
            repeat_progression((1,), (1,), 0)

    def test_chapter_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = run_chapter_09(Path(directory))
            self.assertEqual(tuple(path.name for path in paths), CHAPTER_09_FILENAMES)
            self.assertTrue(all(path.exists() and path.stat().st_size > 44 for path in paths))


if __name__ == "__main__":
    unittest.main()
