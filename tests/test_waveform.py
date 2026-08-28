from pathlib import Path
import tempfile
import unittest
import wave

from composition_lab.cli import CHAPTER_00_FILENAME, run_chapter_00
from composition_lab.waveform import SAMPLE_RATE, sine_wave, write_wav


class SineWaveTests(unittest.TestCase):
    def test_samples_are_bounded_and_have_requested_length(self) -> None:
        samples = sine_wave(440.0, 0.1, amplitude=0.4)
        self.assertEqual(len(samples), 4_410)
        self.assertLessEqual(max(samples), 0.4)
        self.assertGreaterEqual(min(samples), -0.4)
        self.assertEqual(samples[0], 0.0)
        self.assertEqual(samples[-1], 0.0)

    def test_invalid_musical_inputs_are_rejected(self) -> None:
        for frequency, duration in ((0, 1), (-440, 1), (440, 0), (440, -1)):
            with self.subTest(frequency=frequency, duration=duration):
                with self.assertRaises(ValueError):
                    sine_wave(frequency, duration)
        with self.assertRaises(ValueError):
            sine_wave(440, 1, amplitude=1.1)

    def test_wav_has_expected_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = write_wav(Path(directory) / "tone.wav", sine_wave(440, 0.1))
            with wave.open(str(path), "rb") as wav_file:
                self.assertEqual(wav_file.getnchannels(), 1)
                self.assertEqual(wav_file.getsampwidth(), 2)
                self.assertEqual(wav_file.getframerate(), SAMPLE_RATE)
                self.assertEqual(wav_file.getnframes(), 4_410)

    def test_chapter_experiment_creates_complete_composition(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = run_chapter_00(Path(directory))
            self.assertEqual(path.name, CHAPTER_00_FILENAME)
            self.assertTrue(path.is_file())
            with wave.open(str(path), "rb") as wav_file:
                self.assertEqual(wav_file.getnframes(), round(1.8 * SAMPLE_RATE))


if __name__ == "__main__":
    unittest.main()
