import tempfile
import unittest
from pathlib import Path

from composition_lab.cli import CHAPTER_05_FILENAMES, run_chapter_05
from composition_lab.events import NoteEvent
from composition_lab.melody import (
    average_interval_size,
    classify_motion,
    contour_directions,
    interval_between,
    interval_sequence,
    interval_size,
    melodic_profile,
    melodic_range,
    motion_direction,
    pitches_from_events,
)


class MelodicMotionTests(unittest.TestCase):
    def test_signed_interval_sequences(self):
        self.assertEqual(interval_sequence([60, 62, 64]), (2, 2))
        self.assertEqual(interval_sequence([64, 62, 60]), (-2, -2))
        self.assertEqual(interval_sequence([60, 60, 62]), (0, 2))
        self.assertEqual(interval_between(60, 64), 4)
        self.assertEqual(interval_size(-5), 5)

    def test_motion_and_direction_are_separate(self):
        self.assertEqual([classify_motion(i) for i in (0, 1, -2, 3, -12)],
                         ["repeat", "step", "step", "leap", "leap"])
        self.assertEqual([motion_direction(i) for i in (2, -2, 0)],
                         ["ascending", "descending", "stationary"])

    def test_range_contour_and_average(self):
        pitches = [60, 62, 64, 67, 64, 62, 60]
        self.assertEqual(melodic_range(pitches), 7)
        self.assertEqual(contour_directions(pitches), (
            "ascending", "ascending", "ascending",
            "descending", "descending", "descending",
        ))
        self.assertAlmostEqual(average_interval_size([2, 2, 5, -2, -2]), 2.6)

    def test_profile_counts_and_percentages(self):
        profile = melodic_profile([60, 60, 62, 67])
        self.assertEqual((profile.repeats, profile.steps, profile.leaps), (1, 1, 1))
        self.assertEqual((profile.ascending, profile.descending, profile.stationary), (2, 0, 1))
        self.assertAlmostEqual(profile.stepwise_percentage, 100 / 3)
        self.assertAlmostEqual(profile.leap_percentage, 100 / 3)
        self.assertAlmostEqual(profile.repeat_percentage, 100 / 3)
        self.assertAlmostEqual(profile.average_interval_size, 7 / 3)

    def test_empty_and_one_note_contract(self):
        empty = melodic_profile([])
        one = melodic_profile([60])
        self.assertEqual((empty.lowest, empty.highest, empty.range_semitones), (None, None, 0))
        self.assertEqual((one.lowest, one.highest, one.range_semitones), (60, 60, 0))
        for profile in (empty, one):
            self.assertEqual(profile.movements, 0)
            self.assertEqual(profile.stepwise_percentage, 0.0)
            self.assertEqual(profile.average_interval_size, 0.0)

    def test_events_are_analyzed_in_supplied_order(self):
        events = (NoteEvent(64, 1, 1), NoteEvent(60, 0, 1))
        self.assertEqual(pitches_from_events(events), (64, 60))
        self.assertEqual(interval_sequence(pitches_from_events(events)), (-4,))

    def test_chapter_05_writes_all_expected_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = run_chapter_05(Path(directory))
            self.assertEqual(tuple(path.name for path in paths), CHAPTER_05_FILENAMES)
            for path in paths:
                self.assertTrue(path.is_file())
                self.assertGreater(path.stat().st_size, 44)


if __name__ == "__main__":
    unittest.main()
