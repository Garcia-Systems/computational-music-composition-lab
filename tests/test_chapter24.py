import json
from pathlib import Path
import tempfile
import unittest

from composition_lab.chapter22 import chapter_22_capstone
from composition_lab.chapter23 import write_instrument_map, ALL_SINE_INSTRUMENT_MAP
from composition_lab.chapter24 import (
    ARTICULATED_PLAYBACK, ARTICULATIONS, BASIC_PLAYBACK,
    gate_duration_beats, render_chapter_24, validate_gate_ratio,
    velocity_normalized, write_playback_configuration,
)
from composition_lab.events import NoteEvent
from composition_lab.rhythm import beats_to_seconds


class Chapter24Tests(unittest.TestCase):
    def test_gate_validation_and_duration(self):
        event = NoteEvent(60, 0, 2)
        self.assertEqual(gate_duration_beats(event, 0.5), 1)
        for ratio in (0.01, 0.5, 1):
            self.assertEqual(validate_gate_ratio(ratio), float(ratio))
        for ratio in (0, -0.1, 1.01, True, "0.5"):
            with self.assertRaises(ValueError):
                validate_gate_ratio(ratio)

    def test_beat_seconds_and_velocity_reuse(self):
        self.assertEqual(beats_to_seconds(1, 120), 0.5)
        self.assertEqual(beats_to_seconds(gate_duration_beats(NoteEvent(60, 0, 2), 0.5), 120), 0.5)
        self.assertEqual(velocity_normalized(127), 1.0)

    def test_playback_serialization_and_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = write_playback_configuration(ARTICULATED_PLAYBACK, Path(directory) / "playback.json")
            document = json.loads(path.read_text())
            self.assertEqual(document["layers"]["melody"]["articulation"], "short")
            self.assertEqual(document["layers"]["melody"]["gate_ratio"], ARTICULATIONS["short"])
            bad = {"layers": {"melody": {"gate_ratio": 0}}}
            with self.assertRaises(ValueError):
                write_playback_configuration(bad, Path(directory) / "bad.json")

    def test_capstone_events_are_ordered_and_invariant(self):
        events, layers = chapter_22_capstone()
        before = tuple((e.pitch, e.start, e.duration, e.velocity, layer)
                       for e, layer in zip(events, layers, strict=True))
        self.assertEqual(before, tuple((e.pitch, e.start, e.duration, e.velocity, layer)
                                      for e, layer in zip(events, layers, strict=True)))
        self.assertEqual([e.velocity for e in events], [row[3] for row in before])
        with tempfile.TemporaryDirectory() as directory:
            paths = render_chapter_24(Path(directory))
            records = json.loads(paths[0].read_text())
            expected = [row for _, row in sorted(enumerate(before), key=lambda pair: (pair[1][1], pair[0]))]
            self.assertEqual([(r["pitch"], r["start"], r["duration"], r["velocity"], r["layer"])
                              for r in records], expected)
            self.assertEqual([r["start"] for r in records], sorted(r["start"] for r in records))
            self.assertEqual(len(paths), 3)
            self.assertTrue(all(path.exists() for path in paths))
            self.assertNotIn("events", json.loads(paths[1].read_text()))
            self.assertNotIn("events", json.loads(paths[2].read_text()))

    def test_chapter23_maps_remain_backward_compatible(self):
        with tempfile.TemporaryDirectory() as directory:
            data = json.loads(write_instrument_map(
                ALL_SINE_INSTRUMENT_MAP, Path(directory) / "map.json").read_text())
            self.assertEqual(data, ALL_SINE_INSTRUMENT_MAP)
            self.assertEqual(BASIC_PLAYBACK["layers"]["melody"]["instrument"], "simple_saw")

    def test_supercollider_artifacts_and_source_models(self):
        library = Path("supercollider/synthdefs/articulated_instruments.scd")
        lesson = Path("supercollider/chapter_24_envelopes_filters_articulation.scd")
        chapter = Path("chapters/24_envelopes_filters_articulation/README.md")
        self.assertTrue(all(path.exists() for path in (library, lesson, chapter)))
        source = library.read_text()
        for term in ("SynthDef", "\\adsrSaw", "\\filteredSaw", "\\filterEnvSaw",
                     "Saw", "RLPF", "Env.adsr", "EnvGen", "doneAction: 2"):
            self.assertIn(term, source)
        for forbidden in ("FreeVerb", "CombC", "OSCFunc"):
            self.assertNotIn(forbidden, source + lesson.read_text())


if __name__ == "__main__":
    unittest.main()
