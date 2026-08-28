import json
from pathlib import Path
import tempfile
import unittest

from composition_lab.chapter22 import chapter_22_capstone
from composition_lab.chapter23 import (
    ALL_SINE_INSTRUMENT_MAP, COLORED_INSTRUMENT_MAP, SUPPORTED_INSTRUMENTS,
    instrument_metadata, render_chapter_23, validate_instrument,
    write_instrument_map,
)
from composition_lab.events import NoteEvent
from composition_lab.export import events_as_records


class Chapter23Tests(unittest.TestCase):
    def test_supported_names_and_unknown_rejection(self):
        expected = {"sine", "saw", "pulse", "two_partial", "detuned_saw"}
        self.assertEqual(SUPPORTED_INSTRUMENTS, expected)
        self.assertEqual([validate_instrument(name) for name in sorted(expected)], sorted(expected))
        with self.assertRaises(ValueError):
            validate_instrument("SinOsc.ar(440)")

    def test_instrument_metadata_is_optional_and_does_not_change_events(self):
        events = (NoteEvent(60, 0, 1), NoteEvent(64, 1, 1))
        before = tuple((e.pitch, e.start, e.duration, e.velocity) for e in events)
        self.assertNotIn("instrument", events_as_records(events)[0])
        metadata = instrument_metadata(events)  # backward-compatible default
        records = events_as_records(events, instruments=metadata)
        self.assertEqual([row["instrument"] for row in records], ["sine", "sine"])
        self.assertEqual(before, tuple((e.pitch, e.start, e.duration, e.velocity) for e in events))

    def test_layer_maps_are_explicit_and_composition_is_identical(self):
        self.assertEqual(set(ALL_SINE_INSTRUMENT_MAP), {"melody", "harmony", "bass"})
        self.assertEqual(set(COLORED_INSTRUMENT_MAP), set(ALL_SINE_INSTRUMENT_MAP))
        events, layers = chapter_22_capstone()
        musical_tuples = tuple((e.pitch, e.start, e.duration, e.velocity, layer)
                               for e, layer in zip(events, layers, strict=True))
        self.assertEqual(musical_tuples, tuple((e.pitch, e.start, e.duration, e.velocity, layer)
                         for e, layer in zip(events, layers, strict=True)))

    def test_maps_and_artifacts_are_deterministic(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = write_instrument_map(COLORED_INSTRUMENT_MAP, root / "first.json")
            second = write_instrument_map(COLORED_INSTRUMENT_MAP, root / "second.json")
            self.assertEqual(first.read_text(), second.read_text())
            paths = render_chapter_23(root / "a")
            copies = render_chapter_23(root / "b")
            self.assertEqual(len(paths), 4)
            self.assertTrue(all(path.exists() for path in paths))
            self.assertEqual([p.read_text() for p in paths], [p.read_text() for p in copies])
            self.assertEqual(len(json.loads(paths[0].read_text())), 4)
            self.assertEqual(len(json.loads(paths[1].read_text())), 24)

    def test_supercollider_library_and_lesson_have_required_models(self):
        library = Path("supercollider/synthdefs/basic_instruments.scd").read_text()
        lesson = Path("supercollider/chapter_23_synthesizers_as_instruments.scd").read_text()
        for term in ("SynthDef", "SinOsc", "Saw", "Pulse", "twoPartial", "detunedSaw"):
            self.assertIn(term, library)
        self.assertIn("instrumentDefs", lesson)
        for forbidden in ("LPF", "HPF", "RLPF", "WhiteNoise", "FreeVerb"):
            self.assertNotIn(forbidden, library)


if __name__ == "__main__":
    unittest.main()
