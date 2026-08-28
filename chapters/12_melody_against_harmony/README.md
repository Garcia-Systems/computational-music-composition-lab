# Chapter 12 — Melody Against Harmony

We can create a melody and a chord progression independently. The missing
question is temporal: **which chord is sounding when each melody note begins?**

```text
melody note → current harmony → membership → local context → motion
```

Run the experiments from the repository root:

```bash
python -m composition_lab chapter-12
```

## Objective structure first

`HarmonicSpan` adapts the existing scale-degree progression to a timeline. Its
interval is half open: `start <= beat < end`. Consequently, a note beginning
exactly at a change belongs to the new chord. `harmonies_during_event` instead
uses positive interval overlap, so a sustained event can encounter several
chords; endpoint contact alone does not count.

A **chord tone** has a pitch class contained in the active chord. Octave does
not affect this fact: E4 and E5 both belong to C major. Register still changes
contour and voicing. A **non-chord tone** lacks that membership. It is not
therefore a mistake, ugly, accidental, undesirable, or dissonant in every
context. Dissonance also depends on interval, register, voicing, tuning,
timbre, style, and context.

Only after membership is computed does the chapter attach strict local labels:

- **passing**: chord tone → step → non-chord middle note → step in the same
  direction → chord tone;
- **neighbor**: chord tone → one step away → return to the identical pitch;
- **approach**: a non-chord tone one chromatic or diatonic step from a following
  chord tone;
- **suspension-like**: a held chord tone crosses a change, becomes a non-chord
  tone, then moves by step to a tone of the new chord;
- **other-non-chord-tone**: the evidence does not meet those narrow rules.

The last category is essential: the program does not force interpretation.
Likewise, chord-tone event and duration percentages describe alignment—not
melody quality.

## Listening comparisons

The command renders all-chord-tone and altered melodies, direct versus
passing motion, static versus neighbor motion, diatonic and chromatic
approaches, with/without suspension, resolution versus continuation, the same
melody under different harmony, different melodies over the same I–IV–V–I,
and a complete opening–continuation–climax–closing phrase. It also renders that
phrase over root-position and Chapter 11 voice-led chords. Voicing changes the
sound and voice motion, but not chord identity or pitch-class membership.

The suspension comparison exposes onset harmony versus harmony during sustain.
The held G begins over C major, continues into F major as a non-chord tone, and
then steps to F. The example is suspension-like; it does not make every held
non-chord tone a suspension.

The same fixed E is a chord tone over C major but a non-chord tone over D minor.
Relationship therefore belongs to pitch **in context**, not pitch alone.
Function is a separate layer again: tonic, predominant, and dominant labels
can coexist with melody analysis without being conflated with it.

## Reader experiments

A. Move one stable chord tone by one scale step. What changes?

B. Replace C→E with C→D→E. How does filling the leap affect continuity?

C. Replace E→E with E→F→E. How does motion decorate stability?

D. Delay a non-chord tone's move to a chord tone.

E. Put the identical non-chord pitch on a strong beat, then between beats.

F. Keep the melody fixed and change the harmony. Which memberships change?

G. Remove every non-chord tone. What musical character changes?

H. Add many non-chord tones. When does the harmony become harder for *you* to
hear? That threshold is not universal.

## Deliberate limits

This is a small triadic, mostly diatonic tonal laboratory—not a universal
ornament or aesthetic analyzer. Real music also uses appoggiaturas,
anticipations, escape tones, pedal points, chromatic tones, seventh chords and
extensions, modal harmony, blues vocabulary, jazz tensions, polytonality, and
nonfunctional harmony. Those are acknowledged, not implemented. The chapter
stops at melody/harmony interaction; it does not implement Chapter 13, groove,
drums, bass design, accompaniment patterns, counterpoint, SuperCollider, or OSC.
