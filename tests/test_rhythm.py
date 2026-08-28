from pathlib import Path
import tempfile
import unittest
import wave

from composition_lab.cli import CHAPTER_02_FILENAMES, run_chapter_02
from composition_lab.rhythm import (
    beats_to_seconds,
    render_beat_sequence,
    sequential_starts,
    total_beats,
)
from composition_lab.waveform import SAMPLE_RATE


class RhythmTests(unittest.TestCase):
    def test_beats_to_seconds(self) -> None:
        self.assertEqual(beats_to_seconds(1, 60), 1)
        self.assertEqual(beats_to_seconds(1, 120), 0.5)
        self.assertEqual(beats_to_seconds(2, 120), 1)

    def test_totals_and_sequential_starts(self) -> None:
        durations = [1.0, 0.5, 0.5, 2.0]
        self.assertEqual(total_beats(durations), 4.0)
        self.assertEqual(sequential_starts(durations), [0.0, 1.0, 1.5, 2.0])

    def test_invalid_tempo_durations_and_alignment(self) -> None:
        for beats, bpm in ((0, 120), (-1, 120), (1, 0), (1, -60)):
            with self.subTest(beats=beats, bpm=bpm):
                with self.assertRaises(ValueError):
                    beats_to_seconds(beats, bpm)
        with self.assertRaises(ValueError):
            total_beats([1, 0])
        with self.assertRaises(ValueError):
            render_beat_sequence([60], [1, 1], 120)

    def test_rest_is_silent_and_preserves_time(self) -> None:
        samples = render_beat_sequence([60, None], [0.5, 0.5], 60)
        self.assertEqual(len(samples), SAMPLE_RATE)
        self.assertTrue(any(sample != 0 for sample in samples[: SAMPLE_RATE // 2]))
        self.assertTrue(all(sample == 0 for sample in samples[SAMPLE_RATE // 2 :]))

    def test_chapter_02_creates_expected_wavs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = run_chapter_02(Path(directory))
            self.assertEqual(tuple(path.name for path in paths), CHAPTER_02_FILENAMES)
            for path in paths:
                self.assertTrue(path.is_file())
                with wave.open(str(path), "rb") as wav_file:
                    self.assertEqual(wav_file.getframerate(), SAMPLE_RATE)
                    self.assertGreater(wav_file.getnframes(), 0)


if __name__ == "__main__":
    unittest.main()
