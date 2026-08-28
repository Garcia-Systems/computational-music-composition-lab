import json
from pathlib import Path
import tempfile
import unittest

from composition_lab.chapter24 import BASIC_PLAYBACK, write_playback_configuration
from composition_lab.chapter25 import (
    DELAY, DRY_LAYERS, SPATIAL_LAYERS, DelaySettings, LayerPlayback,
    ReverbSettings, chapter_25_capstone, effects_document, playback_document,
    render_chapter_25,
)
from composition_lab.events import NoteEvent
from composition_lab.rhythm import beats_to_seconds


class Chapter25Tests(unittest.TestCase):
    def test_pan_and_send_validation(self):
        for pan in (-1, 0, 1):
            self.assertEqual(LayerPlayback("routed_saw", pan=pan).pan, pan)
        for send in (0, 0.5, 1):
            layer = LayerPlayback("routed_saw", delay_send=send, reverb_send=send)
            self.assertEqual(layer.delay_send, send)
        for pan in (-1.01, 1.01, True):
            with self.assertRaises(ValueError):
                LayerPlayback("routed_saw", pan=pan)
        for send in (-0.01, 1.01):
            with self.assertRaises(ValueError):
                LayerPlayback("routed_saw", delay_send=send)

    def test_feedback_and_effect_validation(self):
        self.assertEqual(DelaySettings(feedback=0.35).feedback, 0.35)
        for feedback in (-0.01, 1, True):
            with self.assertRaises(ValueError):
                DelaySettings(feedback=feedback)
        for value in (-0.1, 1.1):
            with self.assertRaises(ValueError):
                ReverbSettings(room=value)

    def test_delay_reuses_beat_conversion(self):
        self.assertEqual(beats_to_seconds(0.5, 120), 0.25)
        document = effects_document()
        self.assertEqual(document["delay"]["delay_seconds"], 0.25)
        self.assertEqual(document["delay"]["feedback"], DELAY.feedback)

    def test_default_is_dry_and_note_event_is_unchanged(self):
        default = LayerPlayback("routed_saw")
        self.assertEqual((default.pan, default.delay_send, default.reverb_send), (0, 0, 0))
        self.assertEqual(set(NoteEvent.__dataclass_fields__), {"pitch", "start", "duration", "velocity"})
        self.assertTrue(all(layer.delay_send == layer.reverb_send == 0 for layer in DRY_LAYERS.values()))

    def test_serialization_separates_playback_and_effects(self):
        playback = playback_document(SPATIAL_LAYERS)
        effects = effects_document()
        self.assertEqual(playback["layers"]["melody"]["pan"], 0.2)
        self.assertNotIn("delay", playback)
        self.assertNotIn("layers", effects)
        self.assertEqual(effects["routing"], "wet-only send/return")

    def test_capstone_events_are_invariant_between_maps(self):
        events, layers = chapter_25_capstone()
        identity = tuple((e.pitch, e.start, e.duration, e.velocity, layer)
                         for e, layer in zip(events, layers, strict=True))
        self.assertEqual(len(events), 48)
        self.assertEqual(max(e.start + e.duration for e in events), 16)
        # Playback alternatives contain no event data and cannot alter identity.
        self.assertNotEqual(playback_document(DRY_LAYERS), playback_document(SPATIAL_LAYERS))
        self.assertEqual(identity, tuple((e.pitch, e.start, e.duration, e.velocity, layer)
                                        for e, layer in zip(events, layers, strict=True)))

    def test_artifacts_and_chapter24_backward_compatibility(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = render_chapter_25(root)
            self.assertTrue(all(path.exists() for path in paths))
            records = json.loads(paths[0].read_text())
            maps = json.loads(paths[1].read_text())
            self.assertEqual(set(maps), {"dry", "spatial"})
            self.assertEqual(len(records), 48)
            old = write_playback_configuration(BASIC_PLAYBACK, root / "chapter24.json")
            self.assertTrue(old.exists())

    def test_supercollider_bus_and_wet_only_sources(self):
        effects = Path("supercollider/synthdefs/effects.scd").read_text()
        lesson = Path("supercollider/chapter_25_space_and_effects.scd").read_text()
        for term in ("SynthDef", "\\simpleDelayFx", "\\simpleReverbFx", "In.ar",
                     "Out.ar", "DelayC", "FreeVerb", "mix: 1.0"):
            self.assertIn(term, effects)
        for term in ("Bus.audio", "Group.after", "\\routedSaw", "Pan2", "sourceGroup", "fxGroup"):
            self.assertIn(term, lesson)
        self.assertNotIn("OSC", effects)


if __name__ == "__main__":
    unittest.main()
