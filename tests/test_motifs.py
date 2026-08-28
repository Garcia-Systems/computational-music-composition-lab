from pathlib import Path
import tempfile
import unittest
import wave

from composition_lab.cli import CHAPTER_06_FILENAMES, CHAPTER_06_MOTIF, run_chapter_06
from composition_lab.events import NoteEvent, composition_duration
from composition_lab.melody import interval_sequence, pitches_from_events
from composition_lab.motifs import (
    augment_motif, build_development_study, diminish_motif, displace_motif,
    invert_motif, motif_duration, normalize_events, repeat_motif,
    retrograde_motif, sequence_motif, transpose_motif,
)
from composition_lab.waveform import SAMPLE_RATE


class MotifTests(unittest.TestCase):
    def setUp(self) -> None:
        self.motif = CHAPTER_06_MOTIF

    def test_normalization_and_span_do_not_assume_zero(self) -> None:
        source = (NoteEvent(60, 4, .5, 70), NoteEvent(62, 5, 1, 80))
        result = normalize_events(source)
        self.assertEqual([event.start for event in result], [0, 1])
        self.assertEqual(motif_duration(source), 2)
        self.assertEqual((result[0].pitch, result[0].duration, result[0].velocity), (60, .5, 70))
        self.assertEqual(source[0].start, 4)
        self.assertEqual(motif_duration([]), 0)

    def test_repetition_and_sequence_placement(self) -> None:
        repeated = repeat_motif(self.motif, 3)
        self.assertEqual([repeated[index].start for index in (0, 4, 8)], [0, 3, 6])
        sequence = sequence_motif(self.motif, (0, 2, 4))
        self.assertEqual([sequence[index].pitch for index in (0, 4, 8)], [60, 62, 64])
        self.assertEqual([sequence[index].start for index in (0, 4, 8)], [0, 3, 6])

    def test_transposition_preserves_intervals_and_original(self) -> None:
        transformed = transpose_motif(self.motif, 5)
        self.assertEqual([event.pitch for event in transformed], [65, 67, 69, 72])
        self.assertEqual(interval_sequence(pitches_from_events(transformed)), (2, 2, 3))
        self.assertEqual(self.motif, CHAPTER_06_MOTIF)
        self.assertTrue(all(new is not old for new, old in zip(transformed, self.motif)))

    def test_retrograde_reverses_pitch_and_asymmetric_time(self) -> None:
        asymmetric = (
            NoteEvent(60, 2, .25), NoteEvent(62, 2.25, .75),
            NoteEvent(64, 3, .5), NoteEvent(67, 3.5, 1.5),
        )
        result = retrograde_motif(asymmetric)
        self.assertEqual([event.pitch for event in result], [67, 64, 62, 60])
        self.assertEqual([event.start for event in result], [0, 1.5, 2, 2.75])
        self.assertEqual([event.duration for event in result], [1.5, .5, .75, .25])

    def test_inversion_reverses_signed_intervals(self) -> None:
        inverted = invert_motif(self.motif, 60)
        self.assertEqual([event.pitch for event in inverted], [60, 58, 56, 53])
        self.assertEqual(interval_sequence(pitches_from_events(inverted)), (-2, -2, -3))
        self.assertEqual([event.start for event in inverted], [event.start for event in self.motif])

    def test_augmentation_diminution_and_displacement(self) -> None:
        augmented = augment_motif(self.motif)
        diminished = diminish_motif(self.motif)
        displaced = displace_motif(self.motif)
        self.assertEqual([event.start for event in augmented], [0, 1, 2, 4])
        self.assertEqual([event.duration for event in augmented], [1, 1, 2, 2])
        self.assertEqual([event.start for event in diminished], [0, .25, .5, 1])
        self.assertEqual([event.duration for event in diminished], [.25, .25, .5, .5])
        self.assertEqual([event.start for event in displaced], [.5, 1, 1.5, 2.5])
        self.assertEqual([event.pitch for event in displaced], [event.pitch for event in self.motif])

    def test_development_structure_is_ordered_and_eight_measures_long(self) -> None:
        score, sections = build_development_study(self.motif)
        self.assertEqual([section.label for section in sections], [
            "original", "repeat", "sequence 0, +2, +4, +5",
            "retrograde twice", "augmentation ×2", "return",
        ])
        self.assertEqual([section.start for section in sections], [0, 3, 6, 18, 24, 30])
        self.assertEqual(composition_duration(score), 33)

    def test_audio_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = run_chapter_06(Path(directory))
            self.assertEqual(tuple(path.name for path in paths), CHAPTER_06_FILENAMES)
            for path in paths:
                with wave.open(str(path), "rb") as wav_file:
                    self.assertEqual(wav_file.getframerate(), SAMPLE_RATE)
                    self.assertGreater(wav_file.getnframes(), 0)


if __name__ == "__main__":
    unittest.main()
