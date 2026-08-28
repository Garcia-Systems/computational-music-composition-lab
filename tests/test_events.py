from dataclasses import FrozenInstanceError
from pathlib import Path
import tempfile
import unittest
import wave

from composition_lab.cli import CHAPTER_03_FILENAMES, run_chapter_03
from composition_lab.event_rendering import render_events
from composition_lab.events import (
    NoteEvent, composition_duration, shift_event, transpose_event, transpose_events,
)
from composition_lab.waveform import SAMPLE_RATE


class NoteEventTests(unittest.TestCase):
    def test_valid_event_is_frozen(self) -> None:
        event = NoteEvent(60, 0.0, 1.0)
        self.assertEqual(event.velocity, 90)
        with self.assertRaises(FrozenInstanceError):
            event.pitch = 61  # type: ignore[misc]

    def test_invalid_fields(self) -> None:
        invalid = [(-1, 0, 1, 90), (128, 0, 1, 90), (60, -1, 1, 90),
                   (60, 0, 0, 90), (60, 0, -1, 90), (60, 0, 1, -1),
                   (60, 0, 1, 128)]
        for values in invalid:
            with self.subTest(values=values), self.assertRaises(ValueError):
                NoteEvent(*values)

    def test_transformations_make_new_events(self) -> None:
        original = NoteEvent(60, 1.0, 0.5)
        transposed = transpose_event(original, 5)
        shifted = shift_event(original, 2)
        self.assertEqual((transposed.pitch, shifted.start), (65, 3.0))
        self.assertEqual(original, NoteEvent(60, 1.0, 0.5))
        self.assertIsNot(original, transposed)
        self.assertEqual(transpose_events([original], 5), [transposed])

    def test_duration_uses_latest_end_for_sequence_overlap_and_gap(self) -> None:
        self.assertEqual(composition_duration([NoteEvent(60, 0, 1), NoteEvent(62, 1, 2)]), 3)
        self.assertEqual(composition_duration([NoteEvent(60, 0, 4), NoteEvent(62, 1, 1)]), 4)
        self.assertEqual(composition_duration([NoteEvent(60, 0, 1), NoteEvent(62, 3, 1)]), 4)
        self.assertEqual(composition_duration([]), 0)

    def test_polyphonic_renderer_places_overlap_and_silence(self) -> None:
        events = [NoteEvent(60, 0, 1), NoteEvent(64, 0.5, 1)]
        samples = render_events(events, 60, sample_rate=1000)
        self.assertEqual(len(samples), 1500)
        self.assertTrue(any(samples[500:1000]))
        gap = render_events([NoteEvent(60, 1, 1)], 60, sample_rate=1000)
        self.assertTrue(all(sample == 0 for sample in gap[:1000]))

    def test_chapter_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = run_chapter_03(Path(directory))
            self.assertEqual(tuple(path.name for path in paths), CHAPTER_03_FILENAMES)
            for path in paths:
                with wave.open(str(path), "rb") as wav_file:
                    self.assertEqual(wav_file.getframerate(), SAMPLE_RATE)
                    self.assertGreater(wav_file.getnframes(), 0)


if __name__ == "__main__":
    unittest.main()
