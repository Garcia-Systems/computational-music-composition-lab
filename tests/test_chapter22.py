import json
from pathlib import Path
import tempfile
import unittest
import wave

from composition_lab.chapter22 import (
    CHAPTER_22_EVENTS, chapter_22_capstone, render_chapter_22,
)
from composition_lab.events import NoteEvent
from composition_lab.export import events_as_records, write_events_json
from composition_lab.pitch import pitch_to_frequency


class EventExportTests(unittest.TestCase):
    def test_export_preserves_fields_frequency_and_simultaneous_starts(self):
        events = (
            NoteEvent(69, 5, .5, 70),
            NoteEvent(60, 4, 2, 80),
            NoteEvent(64, 4, 2, 81),
            NoteEvent(67, 4, 2, 82),
        )
        records = events_as_records(events)
        self.assertEqual(len(records), len(events))
        self.assertEqual([record["start"] for record in records[:3]], [4.0] * 3)
        self.assertEqual([record["duration"] for record in records[:3]], [2.0] * 3)
        self.assertEqual([record["velocity"] for record in records[:3]], [80, 81, 82])
        self.assertAlmostEqual(records[0]["frequency"], pitch_to_frequency(60))
        self.assertEqual(records[-1]["frequency"], 440.0)

    def test_json_is_deterministic_and_creates_parent(self):
        events = (NoteEvent(64, 1, 1), NoteEvent(60, 0, 1))
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "nested" / "first.json"
            second = Path(directory) / "second.json"
            write_events_json(events, first)
            write_events_json(events, second)
            self.assertEqual(first.read_text(), second.read_text())
            self.assertEqual([row["pitch"] for row in json.loads(first.read_text())], [60, 64])

    def test_layer_metadata_follows_events_through_sort(self):
        records = events_as_records(
            (NoteEvent(64, 1, 1), NoteEvent(60, 0, 1)),
            layers=("melody", "bass"),
        )
        self.assertEqual([row["layer"] for row in records], ["bass", "melody"])
        with self.assertRaises(ValueError):
            events_as_records((NoteEvent(60, 0, 1),), layers=())


class Chapter22Tests(unittest.TestCase):
    def test_fixture_contains_melody_and_polyphonic_chord(self):
        self.assertEqual(len(CHAPTER_22_EVENTS), 7)
        self.assertEqual([event.start for event in CHAPTER_22_EVENTS[-3:]], [4, 4, 4])

    def test_capstone_layers_and_count(self):
        events, layers = chapter_22_capstone()
        self.assertEqual(len(events), 24)
        self.assertEqual(len(layers), len(events))
        self.assertEqual(set(layers), {"melody", "harmony", "bass"})

    def test_render_creates_all_artifacts_without_supercollider(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = render_chapter_22(Path(directory))
            self.assertEqual(len(paths), 4)
            self.assertTrue(all(path.exists() for path in paths))
            self.assertEqual(len(json.loads(paths[0].read_text())), 7)
            self.assertEqual(len(json.loads(paths[2].read_text())), 24)
            for path in (paths[1], paths[3]):
                with wave.open(str(path), "rb") as wav_file:
                    self.assertGreater(wav_file.getnframes(), 0)

    def test_supercollider_sources_contain_signal_path(self):
        source = Path("supercollider/chapter_22_first_sound.scd").read_text()
        for term in ("SynthDef", "simpleSine", "SinOsc", "EnvGen", "TempoClock"):
            self.assertIn(term, source)


if __name__ == "__main__":
    unittest.main()
