import tempfile
import unittest
import wave
from pathlib import Path

from composition_lab.cli import CHAPTER_15_FILENAMES, run_chapter_15
from composition_lab.events import NoteEvent
from composition_lab.event_rendering import render_events
from composition_lab.texture import (
    MusicalLayer, arpeggiate_voicing, arrangement_timeline, attack_density,
    attack_overlap, combine_event_layers, layer_metrics, repeated_chord_events,
    shift_layer,
)


class TextureTests(unittest.TestCase):
    def test_combination_is_deterministic_and_does_not_mutate_sources(self):
        a = MusicalLayer("melody", (NoteEvent(67, 1, 1), NoteEvent(64, 0, 1)))
        b = MusicalLayer("bass", (NoteEvent(36, 0, 1),))
        before = (a.events, b.events)
        combined = combine_event_layers(a, b)
        self.assertEqual([(e.start, e.pitch) for e in combined], [(0, 36), (0, 64), (1, 67)])
        self.assertEqual((a.events, b.events), before)
        self.assertIs(combined[0], b.events[0])

    def test_shift_layer_returns_new_timeline(self):
        source = MusicalLayer("harmony", (NoteEvent(60, 1, 2),))
        shifted = shift_layer(source, 3)
        self.assertEqual(shifted.events[0].start, 4)
        self.assertEqual(source.events[0].start, 1)

    def test_explicit_arpeggiation_pattern(self):
        events = arpeggiate_voicing((60, 64, 67), 0, 4, (0, 1, 2, 1), 4, 65)
        self.assertEqual(tuple(e.pitch for e in events), (60, 64, 67, 64))
        self.assertEqual(tuple(e.start for e in events), (0, 1, 2, 3))
        self.assertEqual(tuple(e.duration for e in events), (1, 1, 1, 1))

    def test_block_and_repeated_chord_contracts(self):
        block = tuple(NoteEvent(p, 0, 4) for p in (60, 64, 67))
        repeated = repeated_chord_events((60, 64, 67), 0, 4, 1)
        self.assertEqual({e.start for e in block}, {0})
        self.assertEqual(len(block), 3)
        self.assertEqual(len(repeated), 12)
        self.assertEqual(sorted({e.start for e in repeated}), [0, 1, 2, 3])

    def test_metrics_register_density_and_overlap(self):
        melody = MusicalLayer("melody", (NoteEvent(60, 0, 1, 80), NoteEvent(72, 1, 1, 100)))
        chords = (NoteEvent(48, 0, 2), NoteEvent(52, 0, 2))
        metrics = layer_metrics(melody)
        self.assertEqual(metrics["register"], ("C4", "C5"))
        self.assertEqual(metrics["average_velocity"], 90)
        self.assertEqual(attack_density(chords, 2), .5)
        self.assertEqual(attack_overlap(melody.events, chords), (1, 2))

    def test_timeline_uses_sounding_activity(self):
        layers = (MusicalLayer("melody", (NoteEvent(60, 0, 8),)),
                  MusicalLayer("harmony", (NoteEvent(48, 4, 4),)))
        text = arrangement_timeline(layers, (0, 4, 8))
        self.assertIn("Melody      X     X", text)
        self.assertIn("Harmony     .     X", text)

    def test_rendering_stays_in_float_pcm_range(self):
        dense = tuple(NoteEvent(60 + i, 0, 1, 127) for i in range(12))
        samples = render_events(dense, 120, sample_rate=1000)
        self.assertLessEqual(max(map(abs, samples)), 1.0)

    def test_expected_artifacts_are_rendered(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = run_chapter_15(Path(directory))
            self.assertEqual(tuple(path.name for path in paths), CHAPTER_15_FILENAMES)
            self.assertTrue(all(path.exists() for path in paths))
            with wave.open(str(paths[-1]), "rb") as audio:
                self.assertEqual(audio.getsampwidth(), 2)


if __name__ == "__main__":
    unittest.main()
