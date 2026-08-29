import random
import tempfile
import unittest
from pathlib import Path

from composition_lab.chapter28 import (
    PerformancePlan, PerformanceState, decide_next_region, replay_event_history,
    simulate_performance, write_performance_artifacts,
)


class Chapter28Tests(unittest.TestCase):
    def test_determinism_boundaries_and_progression(self):
        first = simulate_performance()
        second = simulate_performance()
        self.assertEqual(first.trace, second.trace)
        self.assertEqual(first.event_history(), second.event_history())
        self.assertEqual([(r.start_beat, r.start_beat + r.duration_beats) for r in first.regions],
                         [(float(x), float(x + 4)) for x in range(0, 32, 4)])
        self.assertEqual(first.states[-1].current_beat, 32)
        self.assertEqual(first.states[-1].phrase_index, 8)

    def test_rhythm_and_pitch_constraints(self):
        result = simulate_performance()
        melody = []
        for region in result.regions:
            self.assertAlmostEqual(sum(region.rhythm), 4)
            notes = next(layer.events for layer in region.layers if layer.name == "melody")
            melody.extend(notes)
            self.assertLessEqual(max(e.start + e.duration for e in notes), region.start_beat + 4)
        self.assertTrue(all((e.pitch - 60) % 12 in {0, 2, 4, 5, 7, 9, 11} for e in melody))
        self.assertTrue(all(abs(a.pitch - b.pitch) <= 5 for a, b in zip(melody, melody[1:])))

    def test_lookahead_is_operational_only(self):
        a = simulate_performance(PerformancePlan(lookahead_beats=2))
        b = simulate_performance(PerformancePlan(lookahead_beats=4))
        self.assertEqual(a.event_history(), b.event_history())
        a_second = next(entry for entry in a.trace if entry.target_beat == 4)
        b_second = next(entry for entry in b.trace if entry.target_beat == 4)
        self.assertNotEqual(a_second.beat, b_second.beat)

    def test_generator_is_transport_free_and_rng_continues(self):
        rng = random.Random(2026)
        region, state, _ = decide_next_region(PerformancePlan(), PerformanceState(), rng)
        rng_state = rng.getstate()
        decide_next_region(PerformancePlan(), state, rng)
        self.assertNotEqual(rng_state, rng.getstate())
        self.assertEqual(region.start_beat, 0)

    def test_constraint_and_deadline_fallback_continue(self):
        failed = simulate_performance(force_failure_at=frozenset({2}))
        late = simulate_performance(generation_costs={3: 99})
        self.assertTrue(failed.regions[2].fallback_used)
        self.assertTrue(late.regions[3].fallback_used)
        self.assertTrue(any(e.decision_type == "fallback" for e in failed.trace))
        self.assertEqual(failed.states[-1].current_beat, 32)

    def test_trace_replay_uses_recorded_events(self):
        result = simulate_performance()
        with tempfile.TemporaryDirectory() as directory:
            paths = write_performance_artifacts(result, Path(directory))
            self.assertEqual(replay_event_history(paths[1]), result.event_history())


if __name__ == "__main__":
    unittest.main()
