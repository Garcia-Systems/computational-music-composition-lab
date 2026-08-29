# Chapter 21 — Evaluation: Describing Generated Music

> Once a system can generate many pieces, how can we measure structural
> characteristics without pretending those measurements determine musical quality?

```text
GENERATED MUSIC → MEASUREMENT → DESCRIPTION → COMPARISON → DIAGNOSIS → HUMAN JUDGMENT
```

The governing distinction is **descriptive metric ≠ aesthetic score**. Given
Candidates A, B, and C, this chapter does not ask software which is best. It
asks how their observable structures differ, then returns the listening choice
to the composer.

| Descriptive (often computable) | Aesthetic (contextual judgment) |
|---|---|
| wide pitch range | exciting |
| many repeated notes | boring |
| large average interval | dramatic |
| high rhythmic density | energetic |
| many chord tones | consonant |
| many n-grams absent from training | original |
| symmetrical phrases | balanced |

Style, intention, performance, and listener all affect the right column. Code
must never silently translate the left column into it.

## The evaluation module

`composition_lab/evaluation.py` is deliberately a small collection of pure,
standard-library observers. `melody_profile` wraps Chapter 5's interval,
contour, range, and motion analysis, adding absolute/pitch-class diversity and
distributions. Empty sequences have `None` for undefined interval means and
maxima; a one-note range is zero. `rhythm_profile` observes actual onsets and
durations: beat span, attack count, attacks per beat, on/off beats, duration
range, mean, and histogram. Values retain precision; the CLI alone rounds them.

Repetition reports immediate repeats and explicit 2- and 3-gram counts. An
n-gram overlap is exactly the fraction of generated n-gram occurrences found
in the supplied training sequence. Thus “30% were not observed” is justified;
“30% original” is not. Exact-copy and longest-shared-contiguous-run checks are
likewise literal facts, not plagiarism judgments.

Harmony alignment reuses Chapter 12 pitch-class membership and harmonic
timeline lookup. It reports event-count, duration-weighted, and strong-beat
chord-tone fractions. Passing tones, neighbors, suspensions, appoggiaturas, and
chromaticism make clear why a larger fraction is not automatically preferable.
Constraint pass rate describes compliance with stated Chapter 18 rules.
Generation diversity counts distinct tuples; it does not measure quality.

## Controlled listening studies

Run:

```bash
python -m composition_lab chapter-21
```

The terminal dashboard and WAV artifacts compare: a known melody; equal-rhythm
stepwise/leaping melodies; fixed-pitch sparse/dense rhythms; chord/non-chord
placements over one harmony; loose/tight maximum-leap rules; Chapter 19
independent choice/random walk; Chapter 20 frequency/Markov generation; seeds
0–9; A/A'/B facts; and five capstone strategies in the same C-major register,
length, rhythm, tempo, and renderer. Tables remain side-by-side and never become
one composite score. The constraint capstone, independent random, weighted
random, walk, and Markov representatives are rendered separately.

The seed sweep reports only count, minimum, mean, maximum, and unique-sequence
ratio. Repeating it verifies that identical parameters and seed yield identical
events. Strict Markov transition coverage is a correctness invariant: every
generated adjacent pair must have been learned (including documented cyclic
edges), even when the complete recombination never occurred in training.

## Metrics are lossy—and useful for debugging

Two permutations can have the same pitch-class histogram but different
intervals and contours. Two melodies can share a mean interval while ordering
their motions differently. Summary statistics compress information:

```text
RAW EVENTS → DETAILED SEQUENCES → LOCAL FEATURES → SUMMARY METRICS → HUMAN INTERPRETATION
```

That limitation does not make measurement useless. A promised stepwise
generator whose maximum leap is 12 may have a wrapping, octave conversion, or
missing-constraint bug. Regression tests should assert explicit requirements
such as range membership and configured maximum leap—not “average interval
below 2.5 because that sounds better.” Transposition should retain intervals,
range, and rhythm while changing absolute extrema; a rhythm-only edit should
retain pitch metrics.

## Reader experiments

1. Transpose a melody and identify changed and invariant metrics.
2. Reverse it; inspect range, histogram, interval order, and contour.
3. Double all durations and observe unchanged pitch facts.
4. Add an octave leap; observe maximum and mean adjacent interval.
5. Add repeats; inspect immediate and n-gram repetition.
6. Change Chapter 19 weights and aggregate degree counts over 20 seeds.
7. Change Markov training with the generation seed fixed.
8. Tighten Chapter 18 constraints and inspect pass rate and interval profiles.
9. Listen to equal-histogram melodies with different pitch order.
10. Choose a capstone favorite *before* reading metrics. What mattered that the
    report missed? Did preference correlate with interval size, repetition,
    range, or training overlap?

Musical identity often needs recurrence **and** change, so blindly maximizing
either repetition or training-defined novelty is questionable. This chapter
does not measure beauty, emotion, expressiveness, originality, importance,
authenticity, or enjoyment. It adds no aesthetic model, optimizer, automatic
selection, SuperCollider, OSC, or Chapter 22 functionality.

## Bridge forward

The symbolic and reference-rendering curriculum can now describe generated results. Chapter 22 changes rendering architecture—without changing the score—by introducing SuperCollider synthesis.
