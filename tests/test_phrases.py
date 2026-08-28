from pathlib import Path
import tempfile
import unittest
import wave

from composition_lab.cli import (
    CHAPTER_06_MOTIF, CHAPTER_07_FILENAMES, chapter_07_material, run_chapter_07,
)
from composition_lab.events import NoteEvent, composition_duration
from composition_lab.phrases import (
    build_complete_phrase, build_question, ending_variant, fragment_motif,
    phrase_span, place_after,
)
from composition_lab.waveform import SAMPLE_RATE


class PhraseTests(unittest.TestCase):
    def test_fragment_is_extracted_normalized_without_mutation(self) -> None:
        source = CHAPTER_06_MOTIF
        result = fragment_motif(source, 1, 2)
        self.assertEqual([event.pitch for event in result], [62, 64])
        self.assertEqual([event.start for event in result], [0, .5])
        self.assertEqual(source, CHAPTER_06_MOTIF)
        with self.assertRaises(ValueError):
            fragment_motif(source, -1, 2)

    def test_place_after_orders_material_and_honors_real_gap(self) -> None:
        first = (NoteEvent(60, 2, 1), NoteEvent(62, 3, .5))
        second = (NoteEvent(64, 9, .5), NoteEvent(65, 9.5, .5))
        result = place_after(first, second, 1.5)
        self.assertEqual([event.start for event in result], [2, 3, 5, 5.5])
        self.assertEqual([event.pitch for event in result], [60, 62, 64, 65])
        with self.assertRaises(ValueError):
            place_after(first, second, -.5)

    def test_phrase_span_uses_timeline_not_duration_sum(self) -> None:
        events = (NoteEvent(60, 2, 1), NoteEvent(64, 5, 2))
        self.assertEqual(phrase_span(events), 5)
        self.assertEqual(phrase_span(()), 0)

    def test_complete_phrase_sections_and_designed_climax(self) -> None:
        score, sections = build_complete_phrase(CHAPTER_06_MOTIF)
        self.assertEqual([section.label for section in sections],
                         ["opening", "continuation", "climax", "closing"])
        self.assertEqual([section.start for section in sections], [0, 4, 8, 10])
        self.assertEqual([section.end for section in sections], [3.8, 7.92, 9.8, 16])
        self.assertGreater(max(e.pitch for e in sections[2].events),
                           max(e.pitch for e in sections[0].events))
        self.assertEqual(composition_duration(score), 16)

    def test_question_answer_and_duration_variants_change_only_end(self) -> None:
        question, answer = build_question(), build_question(True)
        self.assertEqual(question[:-1], answer[:-1])
        self.assertEqual(question[-1].pitch, 62)
        self.assertEqual(answer[-1].pitch, 60)
        short, long = ending_variant(final_duration=.5), ending_variant(final_duration=2)
        self.assertEqual(short[:-1], long[:-1])
        self.assertEqual((short[-1].pitch, long[-1].pitch), (60, 60))
        self.assertEqual((short[-1].duration, long[-1].duration), (.5, 2))

    def test_phrase_pair_duration_includes_silence(self) -> None:
        capstone = chapter_07_material()[-1]
        self.assertEqual(composition_duration(capstone), 34)
        self.assertEqual((capstone[len(capstone) // 2 - 1].pitch, capstone[-1].pitch),
                         (62, 60))

    def test_audio_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = run_chapter_07(Path(directory))
            self.assertEqual(tuple(path.name for path in paths), CHAPTER_07_FILENAMES)
            for path in paths:
                with wave.open(str(path), "rb") as wav_file:
                    self.assertEqual(wav_file.getframerate(), SAMPLE_RATE)
                    self.assertGreater(wav_file.getnframes(), 0)


if __name__ == "__main__":
    unittest.main()
