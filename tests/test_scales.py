import tempfile
import unittest
from pathlib import Path

from composition_lab.cli import CHAPTER_04_FILENAMES, run_chapter_04
from composition_lab.events import NoteEvent
from composition_lab.scales import (
    MAJOR,
    NATURAL_MINOR,
    build_scale,
    events_from_degrees,
    major_scale,
    natural_minor_scale,
    pitch_from_degree,
    pitch_in_scale,
    scale_degree,
)


class ScaleTests(unittest.TestCase):
    def test_c_scales(self):
        self.assertEqual(major_scale(60), (60, 62, 64, 65, 67, 69, 71, 72))
        self.assertEqual(
            natural_minor_scale(60), (60, 62, 63, 65, 67, 68, 70, 72)
        )

    def test_other_tonics_preserve_interval_pattern(self):
        self.assertEqual(major_scale(62), (62, 64, 66, 67, 69, 71, 73, 74))
        self.assertEqual(major_scale(65), (65, 67, 69, 70, 72, 74, 76, 77))
        self.assertEqual(
            natural_minor_scale(69), (69, 71, 72, 74, 76, 77, 79, 81)
        )

    def test_build_scale_is_transparent_addition(self):
        self.assertEqual(build_scale(10, (0, 1, 4)), (10, 11, 14))

    def test_scale_degree_uses_one_based_musical_degrees(self):
        scale = major_scale(60)
        self.assertEqual(scale_degree(scale, 1), 60)
        self.assertEqual(scale_degree(scale, 8), 72)
        self.assertEqual(pitch_from_degree(65, MAJOR, 5), 72)

    def test_invalid_degrees_are_rejected(self):
        for degree in (0, 9, -1):
            with self.subTest(degree=degree):
                with self.assertRaises(ValueError):
                    scale_degree(major_scale(60), degree)
        with self.assertRaises(TypeError):
            scale_degree(major_scale(60), 1.5)

    def test_membership_wraps_pitch_classes_across_octaves(self):
        for pitch in (48, 60, 72, 84):
            self.assertTrue(pitch_in_scale(pitch, 60, MAJOR))
        for pitch in (61, 66, 73):
            self.assertFalse(pitch_in_scale(pitch, 60, MAJOR))
        self.assertTrue(pitch_in_scale(63, 60, NATURAL_MINOR))

    def test_degree_melody_becomes_sequential_events(self):
        events = events_from_degrees(
            (1, 2, 3, 5, 3, 2, 1), 60, MAJOR, (0.5,) * 7, velocity=80
        )
        self.assertEqual([event.pitch for event in events], [60, 62, 64, 67, 64, 62, 60])
        self.assertEqual([event.start for event in events], [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0])
        self.assertTrue(all(isinstance(event, NoteEvent) for event in events))
        self.assertTrue(all(event.velocity == 80 for event in events))

    def test_degree_melody_requires_matching_rhythm(self):
        with self.assertRaises(ValueError):
            events_from_degrees((1, 2), 60, MAJOR, (1.0,))

    def test_chapter_04_writes_all_expected_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = run_chapter_04(Path(directory))
            self.assertEqual(tuple(path.name for path in paths), CHAPTER_04_FILENAMES)
            for path in paths:
                self.assertTrue(path.is_file())
                self.assertGreater(path.stat().st_size, 44)


if __name__ == "__main__":
    unittest.main()
