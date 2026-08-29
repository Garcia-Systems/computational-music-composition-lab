# Chapter 18 — Constraint-Based Composition

> If we specify musical rules and limits, how can a computer generate candidate
> material that satisfies them without pretending that the rules define good music?

Earlier chapters represented, analyzed, transformed, arranged, and organized
material. Here the computer first proposes new local material, but only inside a
small space whose construction remains visible:

```text
MUSICAL GOAL → CONSTRAINT → CANDIDATE → VALIDATION → SEARCH
             → VALID SOLUTION SET → HUMAN CHOICE
```

Run the complete listening laboratory:

```bash
python -m composition_lab chapter-18
```

## A rule is not a judgment

**Objective constraint:** “Every pitch must remain between C4 and C5.” Given a
pitch tuple, the program can report an exact pass or failure and identify an
offending pitch.

**Subjective judgment:** “The melody should be beautiful.” A small Boolean
function cannot honestly settle that question. This chapter never implements a
beauty score or calls one legal candidate the best melody.

A candidate initially needs no timing:

```python
candidate = (60, 62, 64, 67)
```

An immutable tuple makes the search easy to read and preserves every proposal.
Only selected legal tuples become sequential `NoteEvent` values for listening.

## Inspectable results

`ConstraintResult` is a frozen value with `name`, `passed`, and `detail` fields.
Thus validation retains facts rather than collapsing immediately to one Boolean:

```text
pitch range  FAIL  pitch 74 exceeds maximum 72
maximum leap FAIL  C4 -> G4 = 7 semitones; maximum allowed = 5
```

`Constraint` pairs a display name with one callable. A tuple of these callables
is the entire “constraint language”—there is no inheritance hierarchy or hidden
solver. `evaluate_candidate` returns every result, while
`candidate_is_valid` visibly means that all of those results passed. Rejected
candidates and their complete results remain in `SearchResult` for diagnosis.

The implemented pitch facts include:

- absolute pitch range (where pitches may exist),
- pitch-class membership in a caller-chosen scale,
- maximum adjacent leap,
- required starting and ending pitch classes,
- fixed note count,
- no immediate equal neighbors,
- minimum fraction of stepwise movements,
- melodic range (distance from the candidate's own lowest to highest pitch),
- literal pitch motifs and relational interval motifs.

A chromatic pitch fails scale membership only because that particular experiment
requested a diatonic collection. Repeated notes, leaps, non-tonic endings, and
non-chord tones remain perfectly legitimate musical choices elsewhere.

## Manual comparison

The CLI first applies the same rules to contrasting examples:

```text
A  C D  E  C   passes
B  C F# G  C   fails this experiment's scale membership
C  C G  D  C   fails the five-semitone leap limit
D  C D  E  G   fails the requested tonic ending
```

These are factual rejection reasons, not rankings. A failure inspector prints
every result for `C4 G4 D4 C4`, including the seven-semitone first movement.

## Transparent enumeration and the constraint funnel

The first pool is `(60, 62, 64, 65, 67)`. `itertools.product` enumerates every
four-position tuple in lexicographic order:

```text
5 pitches ^ 4 positions = 625 candidates
```

The funnel applies one rule at a time and reports actual survivors. The CLI also
counts rejection reasons. Those reason counts overlap: a single proposal may
violate its ending, leap, and repeat rules simultaneously.

`find_valid_candidates` retains valid tuples in enumeration order. The audible
study chooses the first, middle, and last survivor only to provide reproducible,
diverse listening positions. That deterministic selection is an implementation
choice, not a quality ranking.

For each capstone selection the report prints pitch integers and names,
intervals, range, step and leap counts, stepwise percentage, and ending. These
are descriptive facts offered to a listener, not substitutes for listening.

## Constraint sensitivity and contradiction

The same search is repeated with maximum leaps of 2, 4, 7, and 12 semitones.
Only one threshold changes, so its effect on the survivor count is inspectable.

An intentionally contradictory set requires both C and G as the final pitch
class. Its last funnel row contains zero. This is a successful search result:
zero solutions may show that rules are incompatible or too restrictive. The
funnel identifies precisely where the set became empty. Removing or relaxing
one rule lets the composer run a controlled comparison.

## Fixed pitch versus fixed rhythm

Pitch search uses one fixed duration pattern, `(1, 0.5, 0.5, 1)`, so its audible
difference is pitch. Rhythm search then reverses that isolation. It enumerates
four durations from `(0.5, 1.0, 2.0)`, retains totals of exactly four beats, and
allows at most one duration of two beats. Floating comparisons use an explicit
tolerance. Three legal rhythms receive the identical pitch tuple.

`melody_from_pitches_and_durations` pairs the independently chosen tuples and
advances a start cursor, returning immutable sequential events. It refuses
unequal tuple lengths rather than silently truncating them.

## Harmony-aware filtering

A fixed I–IV–V–I timeline reuses Chapter 12's `HarmonicSpan`, harmony lookup,
and octave-independent chord-tone test. For this laboratory, every event onset
at an integer beat must belong to its active chord. Offbeat events are allowed
to be non-chord tones. The CLI renders one violation and one passing example.

This is a compositional requirement for one experiment, not a universal law of
melody or counterpoint.

## Capstone: several legal answers

The capstone uses C-major pitches C4 through B4, a fixed six-attack/eight-beat
rhythm, and the I–IV–V–I harmony. Exhaustive candidates must:

1. begin and end on tonic,
2. remain in the C-major collection,
3. span no more than twelve semitones,
4. move no more than five semitones between neighbors,
5. use steps for at least half their movements,
6. avoid immediate pitch repetition, and
7. put chord-change-beat onsets in their active chord.

The report shows the initial `7^6` space and survivors after every rule. First,
middle, and last valid candidates are concatenated with one beat of silence in
`chapter_18_constraint_capstone.wav`. Passing identical rules does not make the
three melodies equivalent. After listening: which would you keep, alter,
combine, or reject?

## Search-space growth

Exhaustion is educational only while the space is small:

```text
5^4   = 625
7^8   = 5,764,801
12^16 = 184,884,258,895,036,416
```

`enumerate_pitch_candidates` calculates the theoretical size first and refuses
spaces above its explicit safety limit. It does not begin an impractical loop.
How to explore larger spaces is a real computational problem, deliberately not
solved in this chapter.

## Constraint-composition recipe

1. Define the search space.
2. Define objective constraints.
3. Enumerate or otherwise generate candidates.
4. Evaluate every candidate.
5. Keep all valid solutions.
6. Inspect why rejected candidates failed.
7. Listen to several valid solutions.
8. Select, edit, or change the constraints as a human composer.

```text
COMPUTER searches systematically
HUMAN chooses the rules
COMPUTER finds candidates
HUMAN listens and judges
HUMAN changes rules or edits material
```

Rules define a permitted **space**, not one correct answer and not good music.

## Reader experiments

- Compare absolute ranges C4–G4 and C4–C5.
- Tighten maximum leap from seven to five to two semitones.
- Remove the tonic-ending rule and inspect the count change.
- Reverse the repeat experiment by requiring at least one repeated pitch.
- Require a literal motif, then require the interval fragment `(+2, +2)`.
- Substitute the natural-minor interval collection.
- Change rhythm while retaining every pitch rule.
- Add or remove the strong-beat chord-tone requirement.
- Make the rules impossible and identify the funnel row that reaches zero.
- Listen to five legal candidates and pick one manually. What artistic criteria
  did you use that the program did not know about?

## Deliberate boundary

The experiments do not claim that scales, tonic endings, small leaps, stepwise
motion, non-repetition, or strong-beat chord tones are stylistic ideals. Pieces
may productively violate every one. There is no randomness, probability,
weighted selection, Markov model, machine learning, evolutionary search,
simulated annealing, neural network, SuperCollider, or OSC here. Controlled
randomness belongs to Chapter 19 and has not been implemented.

## Bridge forward

Enumeration shows what is allowed but scales poorly and always visits possibilities in the same order. Chapter 19 uses local, explicitly seeded randomness to explore valid alternatives reproducibly.
