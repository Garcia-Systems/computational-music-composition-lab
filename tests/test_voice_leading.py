import tempfile
import unittest
from pathlib import Path

from composition_lab.chords import chord_pitch_classes
from composition_lab.cli import CHAPTER_11_FILENAMES, run_chapter_11
from composition_lab.progressions import progression_chords, root_sequence
from composition_lab.scales import MAJOR
from composition_lab.voice_leading import (
    bass_sequence, choose_nearest_inversion, common_pitch_classes,
    extract_voice_lines, inversion_candidates, maximum_voice_motion,
    progression_motion, smooth_progression_voicings, stationary_common_tones,
    total_voice_motion, voice_movements, within_motion_budget,
)


class VoiceLeadingTests(unittest.TestCase):
    def test_movement_measurements(self):
        self.assertEqual(voice_movements((60, 64, 67), (60, 65, 69)), (0, 1, 2))
        self.assertEqual(total_voice_motion((60, 64, 67), (60, 65, 69)), 3)
        self.assertEqual(maximum_voice_motion((60, 64, 67), (60, 65, 74)), 7)
        self.assertTrue(within_motion_budget((60, 64, 67), (60, 65, 69), 5))

    def test_pitch_class_and_stationary_common_tones_are_distinct(self):
        self.assertEqual(common_pitch_classes((60, 64, 67), (69, 72, 76)), (0, 4))
        self.assertEqual(common_pitch_classes((67,), (79,)), (7,))
        self.assertEqual(stationary_common_tones((60, 64, 67), (60, 65, 69)), (60,))
        self.assertEqual(stationary_common_tones((67,), (79,)), ())

    def test_candidates_are_finite_ordered_and_range_limited(self):
        candidates = inversion_candidates((65, 69, 72))
        self.assertEqual(len(candidates), 7)
        self.assertTrue(all(48 <= chord[0] <= chord[-1] <= 84 for chord in candidates))
        self.assertEqual(inversion_candidates((65, 69, 72)), candidates)
        self.assertEqual(inversion_candidates((65, 69, 72), (60, 64)), ())
        with self.assertRaises(ValueError):
            choose_nearest_inversion((60, 64, 67), (65, 69, 72), (60, 64))

    def test_nearest_inversion_and_stable_tie_break(self):
        self.assertEqual(choose_nearest_inversion((60, 64, 67), (65, 69, 72)), (60, 65, 69))
        self.assertEqual(
            choose_nearest_inversion((60, 64, 67), (65, 69, 72)),
            choose_nearest_inversion((60, 64, 67), (65, 69, 72)),
        )

    def test_progression_smoothing_preserves_identity_and_sources(self):
        roots = progression_chords(60, MAJOR, (1, 4, 5, 1))
        snapshot = tuple(roots)
        smooth = smooth_progression_voicings(roots)
        self.assertEqual(roots, snapshot)
        self.assertEqual(smooth, ((60, 64, 67), (60, 65, 69), (62, 67, 71), (64, 67, 72)))
        self.assertEqual(progression_motion(roots), ((15, 6, 21), 42))
        self.assertEqual(progression_motion(smooth), ((3, 6, 3), 12))
        for intended, selected in zip(roots, smooth, strict=True):
            self.assertEqual(chord_pitch_classes(intended), chord_pitch_classes(selected))

    def test_voice_lines_and_root_versus_bass(self):
        voicings = ((60, 64, 67), (60, 65, 69), (59, 62, 67))
        self.assertEqual(extract_voice_lines(voicings), ((60, 60, 59), (64, 65, 62), (67, 69, 67)))
        roots = progression_chords(60, MAJOR, (1, 4, 5, 1))
        smooth = smooth_progression_voicings(roots)
        self.assertEqual(root_sequence(60, MAJOR, (1, 4, 5, 1)), (60, 65, 67, 60))
        self.assertEqual(bass_sequence(smooth), (60, 60, 62, 64))

    def test_chapter_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = run_chapter_11(Path(directory))
            self.assertEqual(tuple(path.name for path in paths), CHAPTER_11_FILENAMES)
            self.assertTrue(all(path.exists() and path.stat().st_size > 44 for path in paths))


if __name__ == "__main__":
    unittest.main()
