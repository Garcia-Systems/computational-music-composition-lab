import tempfile
import unittest
from pathlib import Path

from composition_lab.chapter18 import (
    CHAPTER_18_FILENAMES, PITCH_POOL, build_chapter_18_study,
    capstone_constraints, pitch_constraints, render_chapter_18,
)
from composition_lab.constraints import (
    Constraint, all_pitches_in_scale, candidate_is_valid,
    contains_interval_pattern, contains_pitch_pattern, ends_on_pitch_class,
    enumerate_pitch_candidates, evaluate_candidate, find_valid_candidates,
    maximum_leap_at_most, melodic_range_at_most,
    melody_from_pitches_and_durations, no_immediate_repeated_pitches,
    starts_on_pitch_class, strong_beat_chord_tones, total_duration_equals,
    within_pitch_range,
)
from composition_lab.melody_harmony import HarmonicSpan
from composition_lab.scales import MAJOR


class ConstraintTests(unittest.TestCase):
    def test_individual_pitch_constraints_and_details(self):
        self.assertTrue(within_pitch_range((60, 72), 60, 72).passed)
        failure = within_pitch_range((60, 74), 60, 72)
        self.assertFalse(failure.passed)
        self.assertIn("74 exceeds maximum 72", failure.detail)
        self.assertTrue(all_pitches_in_scale((60, 62, 64), 60, MAJOR).passed)
        self.assertFalse(all_pitches_in_scale((60, 66), 60, MAJOR).passed)
        self.assertTrue(maximum_leap_at_most((60, 62, 64, 60), 5).passed)
        leap = maximum_leap_at_most((60, 67, 62, 60), 5)
        self.assertFalse(leap.passed)
        self.assertIn("7 semitones", leap.detail)

    def test_start_end_repeat_range_and_motifs(self):
        pitches = (60, 62, 64, 60)
        self.assertTrue(starts_on_pitch_class(pitches, 0).passed)
        self.assertTrue(ends_on_pitch_class(pitches, 0).passed)
        self.assertTrue(no_immediate_repeated_pitches(pitches).passed)
        self.assertFalse(no_immediate_repeated_pitches((60, 62, 62, 60)).passed)
        self.assertTrue(melodic_range_at_most(pitches, 5).passed)
        self.assertTrue(contains_pitch_pattern(pitches, (60, 62)).passed)
        self.assertTrue(contains_interval_pattern((65, 67, 69), (2, 2)).passed)

    def test_evaluation_keeps_each_result(self):
        results = evaluate_candidate((60, 62, 64, 60), pitch_constraints())
        self.assertEqual(len(results), 7)
        self.assertTrue(candidate_is_valid(results))

    def test_enumeration_count_order_filter_and_empty_search(self):
        candidates = enumerate_pitch_candidates(PITCH_POOL, 4)
        self.assertEqual(len(candidates), 625)
        self.assertEqual(candidates[0], (60, 60, 60, 60))
        self.assertEqual(candidates[-1], (67, 67, 67, 67))
        result = find_valid_candidates(candidates, pitch_constraints())
        self.assertGreater(len(result.valid), 0)
        impossible = pitch_constraints() + (
            Constraint("end G", lambda p: ends_on_pitch_class(p, 7)),
        )
        self.assertEqual(find_valid_candidates(candidates, impossible).valid, ())

    def test_search_limit_prevents_explosion(self):
        with self.assertRaisesRegex(ValueError, "search space"):
            enumerate_pitch_candidates(tuple(range(12)), 16)

    def test_rhythm_and_event_conversion(self):
        self.assertTrue(total_duration_equals((.5, 1, .5, 2), 4).passed)
        events = melody_from_pitches_and_durations((60, 62), (1, .5), start=2)
        self.assertEqual(tuple(event.start for event in events), (2, 3))
        self.assertEqual(tuple(event.duration for event in events), (1, .5))
        with self.assertRaises(ValueError):
            melody_from_pitches_and_durations((60,), (1, 1))

    def test_strong_beat_harmony_constraint(self):
        harmony = (HarmonicSpan(0, 2, (60, 64, 67)),)
        passing = melody_from_pitches_and_durations((60, 64), (1, 1))
        failing = melody_from_pitches_and_durations((60, 62), (1, 1))
        self.assertTrue(strong_beat_chord_tones(passing, harmony).passed)
        self.assertFalse(strong_beat_chord_tones(failing, harmony).passed)

    def test_chapter_study_and_artifacts(self):
        study = build_chapter_18_study()
        self.assertEqual(study.pitch_funnel[0], ("All candidates", 625))
        self.assertEqual(study.impossible_funnel[-1][1], 0)
        self.assertGreater(len(study.rhythm_candidates), 2)
        self.assertGreater(len(study.capstone_candidates), 2)
        with tempfile.TemporaryDirectory() as directory:
            paths = render_chapter_18(Path(directory))
            self.assertEqual(tuple(path.name for path in paths), CHAPTER_18_FILENAMES)
            self.assertTrue(all(path.exists() and path.stat().st_size > 44 for path in paths))


if __name__ == "__main__":
    unittest.main()
