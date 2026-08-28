import tempfile
import unittest
from pathlib import Path

from composition_lab.cli import CHAPTER_13_FILENAMES, chapter_13_layered_cycle, run_chapter_13
from composition_lab.events import NoteEvent, composition_duration
from composition_lab.groove import (
    GroovePattern, combine_layers, crosses_beat, events_per_beat, groove_events,
    is_offbeat_eighth, is_on_beat, pattern_grid, repeat_groove,
    subdivision_positions,
)


class GrooveTests(unittest.TestCase):
    def test_eighth_grid_has_eight_positions_without_end_boundary(self):
        self.assertEqual(subdivision_positions(4, 2), (0, .5, 1, 1.5, 2, 2.5, 3, 3.5))

    def test_pattern_validation(self):
        for kwargs in ({"cycle_beats": 0, "subdivisions_per_beat": 2, "active_steps": ()},
                       {"cycle_beats": 4, "subdivisions_per_beat": 0, "active_steps": ()},
                       {"cycle_beats": 4, "subdivisions_per_beat": 2, "active_steps": (8,)},
                       {"cycle_beats": 4, "subdivisions_per_beat": 2, "active_steps": (0,), "velocities": ()},
                       {"cycle_beats": 4, "subdivisions_per_beat": 2, "active_steps": (0,), "velocities": (128,)}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                GroovePattern(**kwargs)

    def test_pattern_to_events_maps_onsets_and_velocities(self):
        events = groove_events(GroovePattern(4, 2, (0, 2, 4, 6), (100, 80, 90, 70)), pitch=72)
        self.assertEqual(tuple(event.start for event in events), (0, 1, 2, 3))
        self.assertEqual(tuple(event.velocity for event in events), (100, 80, 90, 70))
        self.assertTrue(all(event.pitch == 72 for event in events))

    def test_offbeat_pattern_and_identification(self):
        starts = tuple(event.start for event in groove_events(GroovePattern(4, 2, (1, 3, 5, 7))))
        self.assertEqual(starts, (.5, 1.5, 2.5, 3.5))
        self.assertTrue(all(is_offbeat_eighth(value) for value in starts))
        self.assertTrue(all(is_on_beat(value) for value in (0, 1, 2, 3)))
        self.assertFalse(is_offbeat_eighth(.25))

    def test_repetition_timing_and_cycle_duration(self):
        cycle = groove_events(GroovePattern(4, 2, (0, 2, 4, 6)), note_duration=1)
        repeated = repeat_groove(cycle, 3, 4)
        self.assertEqual(tuple(event.start for event in repeated[::4]), (0, 4, 8))
        self.assertEqual(composition_duration(repeated), 12)

    def test_crossing_density_grid_and_layers(self):
        self.assertFalse(crosses_beat(NoteEvent(60, 1.5, .2)))
        self.assertTrue(crosses_beat(NoteEvent(60, 1.5, 1)))
        events = groove_events(GroovePattern(4, 2, (0, 2, 3, 5, 7)))
        self.assertEqual(events_per_beat(events, 4), 1.25)
        self.assertEqual(pattern_grid(GroovePattern(4, 2, (0, 2))), "X . X . . . . .")
        self.assertEqual(len(combine_layers(events[:2], events[2:])), 5)
        self.assertEqual(len(chapter_13_layered_cycle()), 12)

    def test_expected_audio_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = run_chapter_13(Path(directory))
            self.assertEqual(tuple(path.name for path in paths), CHAPTER_13_FILENAMES)
            self.assertTrue(all(path.exists() and path.stat().st_size > 44 for path in paths))


if __name__ == "__main__":
    unittest.main()
