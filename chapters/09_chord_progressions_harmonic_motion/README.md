# Chapter 9 — Chord Progressions and Harmonic Motion

> How do individual chords become a harmonic journey through time?

Chapter 8 constructed C major, F major, and G major separately. Composition now
places them in time: `C → F → G → C`. A chord has one identity in isolation and
another role when surrounded by other chords. We can hear that difference
without yet building a theory of harmonic function.

```text
CHORD                         PROGRESSION
C E G                         I → IV → V → I
vertical pitch organization   harmonic relationships over time
```

## A deliberately small representation

The progression is two transparent parallel sequences:

```python
degrees = (1, 4, 5, 1)
durations = (2.0, 2.0, 2.0, 2.0)
```

`scale degree + key + duration → chord events on a timeline`. The helper
`progression_events` validates these sequences, reuses Chapter 8's
`triad_from_scale_degree`, gives all three `NoteEvent` values a common onset,
and advances by the requested duration. There is no harmony DSL and no duplicate
timing model. For durations `2 2 4 2`, `progression_starts` returns `0 2 4 8`,
and the total span is 10 beats.

Run all listening experiments:

```bash
python -m composition_lab chapter-09
```

## Scale-degree vocabulary and Roman numerals

In major, stacked diatonic thirds produce:

```text
Degree   1      2      3      4      5      6       7
Quality  major  minor  minor  major  major  minor   diminished
Roman    I      ii     iii    IV     V      vi      vii°
```

Uppercase commonly labels major, lowercase minor, and `°` diminished. Our helper
only labels a degree and known triad quality; it is intentionally not a complete
Roman-numeral parser. `1 4 5 1` is more abstract than `C F G C`.

```text
I IV V I → Key = C major → C F G C
I IV V I → Key = F major → F Bb C F
I IV V I → Key = G major → G C D G
```

Absolute pitches change while relationships remain. Roman numerals and scale
degrees describe a harmonic idea independently of key.

## Sequence and ending

The first experiment holds every chord for two beats. Compare `I–IV–V` with
`I–IV–V–I`, keeping key, voicing, tempo, and harmonic duration constant. What
does final I change? Does returning to the first chord feel different from simply
stopping on V? These observations prepare later analysis without naming a full
functional or cadence system.

A second widely used tonal pattern is `I–V–vi–IV`, or C–G–Am–F in C major.
Compare it with `I–IV–V–I`. Then compare `I–V–vi–IV` and `I–IV–vi–V`: exactly
the same inventory, differently ordered. **Harmony depends on sequence, not only
chord inventory.** A one-chord variation, `I–V–IV–IV`, further asks how much one
change can alter an otherwise fixed loop.

## Harmonic rhythm

**Harmonic rhythm is the rate at which chords change.** It is distinct from
melodic rhythm. Slow, medium, and fast files keep `I IV V I` identical while
each chord lasts 4, 2, or 1 beat. The total spans are 16, 8, and 4 beats. At what
rate does the same progression feel static, active, or restless?

Repeating `I–V–vi–IV` twice preserves the progression and its two-beat harmonic
rhythm while extending its timeline. How quickly does a loop establish
expectation? When does familiarity become predictability?

## Inspecting the bass and root-position limitation

In C major the root-position bass sequence of `I–IV–V–I` is C–F–G–C. Bass
motion is one audible component of harmonic motion. The inspector printed by the
CLI exposes start, duration, degree, Roman numeral, root, and every chord tone
before listening.

```text
C E G → F A C → G B D → C E G
```

Root position makes identity easy to inspect, but it may produce large jumps
between voices. We deliberately do not improve those lines here. Inversions and
voice-leading optimization would obscure this chapter's single question and
belong later.

## Melody-over-progression preview

The final experiment combines a simple scale-degree melody (horizontal layer)
with a slow progression (vertical and temporal layer). Melody velocity 90 and
chord velocity 60 are practical balances for this sine-wave experiment, not
universal mixing laws. This is only a preview: Chapter 12 will examine melody
against harmony properly.

## Reader experiments

1. **Change one chord:** begin with `I V vi IV`, alter one position, and listen.
2. **Reorder:** retain exactly I, IV, V, and vi but change their sequence.
3. **Change harmonic rhythm:** try 4, 2, 1, and 0.5 beat per chord. When does it
   become restless or static?
4. **Change key:** render the identical degree pattern in several major keys.
5. **Leave it open:** stop on V, then add I, and compare.
6. **Repeat:** render one, two, four, and eight loops. When does expectation become
   predictability?
7. **Change the melody layer:** hold the progression fixed and alter only melody.

## Boundaries

Natural minor can use the same machinery—for example A minor `i–VI–VII–i`—but
real minor-key harmony is richer than this natural-minor-only model. Real practice
may include inversions, seventh and non-diatonic chords, secondary dominants,
modal mixture, modulation, chromatic bass, pedal tones, substitutions, and
nonfunctional harmony. None is implemented here. Nor are harmonic-function
analysis, tension categories, cadence taxonomy, or voice-leading optimization:
those questions remain for later chapters, especially Chapter 10.

## Listening artifacts

The command creates the basic progression; open/closed endings; three harmonic
rhythms; C, F, and G transpositions; `I–V–vi–IV`; two orderings; a repeated loop;
a one-chord variation; and the melody-over-progression preview. Their descriptive
`chapter_09_*.wav` names make every comparison discoverable in `outputs/`.

## Bridge forward

A progression records chord identity and duration but not the broad directional roles listeners may hear in this limited major-key model. Chapter 10 adds tonic, predominant, and dominant function.
