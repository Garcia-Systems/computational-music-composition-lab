import copy
import random
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from composition_lab.chapter20 import (
    CHAPTER_20_FILENAMES, TRAINING_RHYTHM, build_memory_capstone,
    degrees_to_events, melody_constraints, render_chapter_20,
)
from composition_lab.markov import (
    DeadEndError, build_transition_counts, build_transition_counts_from_sequences,
    choose_next_state, generate_markov_sequence, generate_valid_markov_candidate,
    transition_pairs, transition_probabilities,
)


class MusicalMemoryTests(unittest.TestCase):
    def test_pairs_counts_probabilities_and_deterministic_training(self):
        sequence = (1, 2, 3, 2, 1)
        self.assertEqual(transition_pairs(sequence), ((1, 2), (2, 3), (3, 2), (2, 1)))
        expected = {1: {2: 1}, 2: {3: 1, 1: 1}, 3: {2: 1}}
        self.assertEqual(build_transition_counts(sequence), expected)
        self.assertEqual(build_transition_counts(sequence), build_transition_counts(sequence))
        probabilities = transition_probabilities(expected)
        self.assertEqual(probabilities[1], {2: 1.0})
        self.assertEqual(probabilities[2], {3: .5, 1: .5})
        self.assertTrue(all(abs(sum(row.values()) - 1) < 1e-12
                            for row in probabilities.values()))

    def test_seeded_choice_sequence_and_immutability(self):
        counts = build_transition_counts((1, 2, 1, 3, 1, 2), cyclic=True)
        snapshot = copy.deepcopy(counts)
        self.assertEqual(choose_next_state(counts, 2, random.Random(8)), 1)
        first = generate_markov_sequence(counts, 1, 30, random.Random(20))
        self.assertEqual(first, generate_markov_sequence(counts, 1, 30, random.Random(20)))
        self.assertEqual(counts, snapshot)
        self.assertGreater(first.count(2), 0)
        self.assertGreater(first.count(3), 0)

    def test_dead_end_stop_restart_and_cyclic(self):
        linear = build_transition_counts((1, 2, 3))
        with self.assertRaisesRegex(DeadEndError, "no observed successor"):
            choose_next_state(linear, 3, random.Random(1))
        with self.assertRaises(DeadEndError):
            choose_next_state(linear, 7, random.Random(1))
        self.assertEqual(generate_markov_sequence(linear, 1, 6, random.Random(1)), (1, 2, 3))
        self.assertEqual(generate_markov_sequence(linear, 1, 6, random.Random(1), dead_end="restart"),
                         (1, 2, 3, 1, 2, 3))
        cyclic = build_transition_counts((1, 2, 3), cyclic=True)
        self.assertEqual(cyclic[3], {1: 1})

    def test_boundary_aware_and_rhythm_states(self):
        counts = build_transition_counts_from_sequences(((1, 2), (4, 5)))
        self.assertEqual(counts, {1: {2: 1}, 4: {5: 1}})
        self.assertNotIn(4, counts.get(2, {}))
        rhythm = build_transition_counts(TRAINING_RHYTHM, cyclic=True)
        generated = generate_markov_sequence(rhythm, 1.0, 20, random.Random(5))
        self.assertTrue(set(generated) <= {.5, 1.0, 2.0})

    def test_degree_realization_and_different_keys(self):
        degrees = (1, 2, 3, 1)
        c = degrees_to_events(degrees, 60)
        f = degrees_to_events(degrees, 65)
        self.assertEqual(tuple(event.pitch for event in c), (60, 62, 64, 60))
        self.assertEqual(tuple(event.pitch for event in f), (65, 67, 69, 65))
        self.assertEqual(tuple(b.pitch - a.pitch for a, b in zip(c, f)), (5, 5, 5, 5))

    def test_constraint_sampling_and_capstone_replay(self):
        counts = build_transition_counts((1, 2, 1, 3, 1), cyclic=True)
        result = generate_valid_markov_candidate(counts, 1, 5, melody_constraints(),
                                                 random.Random(2), 100)
        self.assertIsNotNone(result.candidate)
        self.assertTrue(all(rule(result.candidate) for rule in melody_constraints()))
        first = build_memory_capstone(2026)
        self.assertEqual(first, build_memory_capstone(2026))
        self.assertTrue(first.valid)
        self.assertNotEqual(first.sections[:3], build_memory_capstone(2027).sections[:3])

    def test_artifacts(self):
        with TemporaryDirectory() as directory:
            paths = render_chapter_20(Path(directory))
            self.assertEqual(tuple(path.name for path in paths), CHAPTER_20_FILENAMES)
            self.assertTrue(all(path.exists() and path.stat().st_size > 44 for path in paths))


if __name__ == "__main__":
    unittest.main()
