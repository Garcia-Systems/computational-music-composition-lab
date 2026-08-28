from pathlib import Path
import tempfile
import unittest
import wave

from composition_lab.cli import CHAPTER_01_FILENAMES, run_chapter_01
from composition_lab.pitch import (
    interval_semitones,
    name_to_pitch,
    pitch_to_frequency,
    pitch_to_name,
    transpose_pitch,
)
from composition_lab.waveform import SAMPLE_RATE


class PitchTests(unittest.TestCase):
    def test_reference_names_and_numbers(self) -> None:
        for name, pitch in (("A4", 69), ("C4", 60), ("C5", 72), ("C#4", 61)):
            with self.subTest(name=name):
                self.assertEqual(name_to_pitch(name), pitch)
                self.assertEqual(pitch_to_name(pitch), name)

    def test_reference_frequencies(self) -> None:
        self.assertAlmostEqual(pitch_to_frequency(69), 440.0)
        self.assertAlmostEqual(pitch_to_frequency(60), 261.63, places=2)
        self.assertAlmostEqual(pitch_to_frequency(72), 523.25, places=2)

    def test_transposition_and_intervals(self) -> None:
        self.assertEqual(transpose_pitch(60, 12), 72)
        self.assertEqual(transpose_pitch(60, 7), 67)
        self.assertEqual(interval_semitones(60, 64), 4)
        self.assertEqual(interval_semitones(72, 67), -5)

    def test_boundary_names_round_trip(self) -> None:
        for pitch in (0, 1, 60, 126, 127):
            self.assertEqual(name_to_pitch(pitch_to_name(pitch)), pitch)

    def test_invalid_inputs_are_rejected(self) -> None:
        for pitch in (-1, 128):
            with self.assertRaises(ValueError):
                pitch_to_name(pitch)
        for name in ("Db4", "c4", "H4", "C#", "C10"):
            with self.assertRaises(ValueError):
                name_to_pitch(name)
        with self.assertRaises(TypeError):
            pitch_to_frequency(60.0)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            transpose_pitch(127, 1)

    def test_chapter_01_creates_three_complete_wavs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = run_chapter_01(Path(directory))
            self.assertEqual(tuple(path.name for path in paths), CHAPTER_01_FILENAMES)
            for path in paths:
                with wave.open(str(path), "rb") as wav_file:
                    self.assertEqual(wav_file.getnframes(), round(1.8 * SAMPLE_RATE))


if __name__ == "__main__":
    unittest.main()
