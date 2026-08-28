import tempfile
import unittest
from pathlib import Path

from composition_lab.cli import CHAPTER_10_FILENAMES, chapter_10_material, run_chapter_10
from composition_lab.events import composition_duration
from composition_lab.harmonic_function import (
    abbreviated_functional_path, functional_path, harmonic_function,
)


class HarmonicFunctionTests(unittest.TestCase):
    def test_major_key_mapping(self):
        self.assertEqual(
            tuple(harmonic_function(degree) for degree in range(1, 8)),
            ("tonic", "predominant", "tonic-like", "predominant", "dominant", "tonic-like", "dominant"),
        )

    def test_invalid_degrees(self):
        for degree in (0, 8):
            with self.assertRaises(ValueError):
                harmonic_function(degree)
        for degree in (True, 1.0, "1"):
            with self.assertRaises(TypeError):
                harmonic_function(degree)

    def test_functional_paths_preserve_each_position(self):
        self.assertEqual(functional_path((1, 4, 5, 1)), ("tonic", "predominant", "dominant", "tonic"))
        self.assertEqual(abbreviated_functional_path((1, 4, 5, 1)), ("T", "P", "D", "T"))

    def test_controlled_experiment_structures(self):
        scores = chapter_10_material()
        roots = lambda score: tuple(event.pitch for event in score[::3])
        self.assertEqual(roots(scores[1]), (60, 65, 67, 60))
        self.assertEqual(roots(scores[2]), (60, 62, 67, 60))
        self.assertEqual(roots(scores[3]), (60, 65, 67, 60))
        self.assertEqual(roots(scores[4]), (60, 65, 71, 60))
        self.assertEqual(roots(scores[8]), (67, 69))  # V -> vi
        self.assertEqual(roots(scores[12])[-1], roots(scores[13])[-1])  # same A-minor destination

    def test_duration_is_preserved_or_deliberately_varied(self):
        scores = chapter_10_material()
        self.assertEqual(composition_duration(scores[1]), composition_duration(scores[2]))
        self.assertEqual(composition_duration(scores[3]), composition_duration(scores[4]))
        self.assertEqual(composition_duration(scores[16]), 7)
        self.assertEqual(composition_duration(scores[17]), 10)

    def test_chapter_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = run_chapter_10(Path(directory))
            self.assertEqual(tuple(path.name for path in paths), CHAPTER_10_FILENAMES)
            self.assertTrue(all(path.exists() and path.stat().st_size > 44 for path in paths))


if __name__ == "__main__":
    unittest.main()
