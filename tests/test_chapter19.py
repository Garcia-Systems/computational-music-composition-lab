import random
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from composition_lab.chapter18 import build_chapter_18_study
from composition_lab.chapter19 import (
    CHAPTER_19_FILENAMES, bounded_velocities, build_seeded_composition,
    generate_valid_random_candidate, motif_transformations, random_valid_candidate,
    random_walk_degrees, render_chapter_19, seed_manifest, weighted_choice,
)


class ControlledRandomnessTests(unittest.TestCase):
    def test_seeded_valid_selection_and_empty_handling(self):
        candidates = build_chapter_18_study().pitch_search.valid
        self.assertEqual(random_valid_candidate(candidates, random.Random(42)),
                         random_valid_candidate(candidates, random.Random(42)))
        with self.assertRaisesRegex(ValueError, "no valid candidates"):
            random_valid_candidate((), random.Random(1))

    def test_weight_validation(self):
        rng = random.Random(1)
        for choices, weights in (((), ()), ((1,), ()), ((1,), (-1,)), ((1, 2), (0, 0))):
            with self.assertRaises(ValueError):
                weighted_choice(choices, weights, rng)
        self.assertEqual(weighted_choice(("only",), (2,), rng), "only")

    def test_bounded_velocity_is_seeded_and_clamped(self):
        first = bounded_velocities(30, 125, 5, random.Random(8))
        self.assertEqual(first, bounded_velocities(30, 125, 5, random.Random(8)))
        self.assertTrue(all(120 <= velocity <= 127 for velocity in first))

    def test_independent_streams(self):
        pitch = random.Random(10)
        rhythm = random.Random(20)
        expected = tuple(pitch.randrange(100) for _ in range(5))
        pitch = random.Random(10)
        rhythm.randrange(100); rhythm.randrange(100)
        self.assertEqual(tuple(pitch.randrange(100) for _ in range(5)), expected)

    def test_seeded_rhythm_and_motif(self):
        rhythms = build_chapter_18_study().rhythm_candidates
        self.assertEqual(random_valid_candidate(rhythms, random.Random(2)),
                         random_valid_candidate(rhythms, random.Random(2)))
        self.assertEqual(motif_transformations(6), motif_transformations(6))
        self.assertTrue(set(motif_transformations(6)) <=
                        {"original", "transpose +5", "retrograde"})

    def test_rejection_acceptance_and_limit(self):
        accepted = generate_valid_random_candidate(lambda rng: (rng.randrange(3),),
                                                    (lambda value: value == (2,),),
                                                    random.Random(1), 20)
        self.assertEqual(accepted.candidate, (2,))
        self.assertLessEqual(accepted.attempts, 20)
        failed = generate_valid_random_candidate(lambda rng: (1,),
                                                  (lambda value: False,), random.Random(1), 7)
        self.assertIsNone(failed.candidate)
        self.assertEqual((failed.attempts, failed.rejected), (7, 7))

    def test_walk_length_boundaries_and_steps(self):
        walk = random_walk_degrees(1, 100, (-2, -1, 0, 1, 2), 1, 8, random.Random(4))
        self.assertEqual(len(walk), 100)
        self.assertTrue(all(1 <= degree <= 8 for degree in walk))
        self.assertTrue(all(b - a in (-2, -1, 0, 1, 2) for a, b in zip(walk, walk[1:])))

    def test_manifest_and_capstone_replay(self):
        self.assertEqual(seed_manifest(2026), seed_manifest(2026))
        first, replay = build_seeded_composition(2026), build_seeded_composition(2026)
        self.assertEqual(first.events, replay.events)
        self.assertEqual(first.decisions, replay.decisions)
        self.assertTrue(first.valid)

    def test_artifacts(self):
        with TemporaryDirectory() as directory:
            paths = render_chapter_19(Path(directory))
            self.assertEqual(tuple(path.name for path in paths), CHAPTER_19_FILENAMES)
            self.assertTrue(all(path.exists() and path.stat().st_size > 44 for path in paths))


if __name__ == "__main__":
    unittest.main()
