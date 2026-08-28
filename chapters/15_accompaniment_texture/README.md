# Chapter 15 — Accompaniment and Texture

> Once melody, harmony, groove, and bass exist, how can we distribute material so each layer has a clear role?

```text
MUSICAL MATERIAL → LAYER → REGISTER → RHYTHMIC ACTIVITY → TEXTURE → ARRANGEMENT
```

Run the listening laboratory with `python -m composition_lab chapter-15`.

## The arrangement problem

If melody, chords, bass, and groove all attack on every eighth note, what should
the listener follow? **Texture** pragmatically describes how simultaneous layers
are distributed and how independently they behave. Thin texture has fewer active
layers, thick texture has more simultaneous layers/events, and active texture has
many attacks and moving parts. These are descriptions, not ratings; thick does
not mean louder or better.

`MusicalLayer` stores a role name and immutable `NoteEvent` tuple. Melody is a
foreground line, harmony is chordal support, bass is a low harmonic/rhythmic
foundation, and groove is a repeating rhythmic reference. Roles are not fixed
instruments: a piano can perform several. `combine_event_layers()` preserves the
events and pitches, sorts them deterministically, and never “improves” or balances
the music. `shift_layer()` makes entrances by returning new events.

## Register, rhythm, and accompaniment

The pedagogical plan is bass C2–C3, harmony C3–C5, and melody C4–C6—not a universal
orchestration rule. Collision and separation files keep harmonic roles and rhythm
similar while changing octave allocation. Low/mid chord and open/closed comparisons
likewise ask how spacing changes clarity and perceived thickness without claiming
psychoacoustic facts beyond this sine renderer.

A block chord gives all tones one onset. `arpeggiate_voicing()` visibly maps chord
plus the index pattern `0 1 2 1` onto equal timed subdivisions. Sustained and
repeated files distinguish **harmonic rhythm** (identity changes) from
**accompaniment rhythm** (re-attacks). `attack_density()` counts distinct onsets
per beat: 0.25, 1, and 2 are factual activity descriptions, not quality scores.
The rhythmic-chord experiment applies Chapter 13's explicit `X . X . . X X .`
grid. A pattern variation such as `0 2 1 2` can alter accompaniment while harmony
remains unchanged.

Foreground/background can be influenced by activity, register, velocity,
repetition, duration, and density. Here, activity, register, and velocity do most
of the work. The role-based rendering uses melody 95, bass near 80, harmony 65,
and groove 55–75, but it is a demonstration rather than a universal recipe.
Musical velocity remains intact event data. Separately, the renderer performs
technical peak normalization only if summed samples exceed the valid range; this
protects PCM output without unpredictably rewriting individual velocities.

## Texture experiments and capstone

Layer-count files add melody, bass, harmony, then groove. Parallel attacks make a
rigid comparison; complementary rhythms leave space rather than constantly
coinciding. `attack_overlap()` reports shared and total distinct onset positions
without producing a complementarity or quality score. Root-position and Chapter
11 voice-led blocks demonstrate that voicing and texture interact but remain
independent choices.

The 16-beat texture arc encodes entrances and exits directly in event timelines:
melody+bass, sustained harmony, broken harmony+groove, then reduced support. The
24-beat capstone uses functional I–V–vi–IV harmony, a melody, voice-led voicings,
bass, groove, explicit arpeggiation, thinning, and a full return. This previews
change over time without defining formal sections or implementing form machinery.

## Reader laboratory

1. Remove chords; hear melody+bass+groove.
2. Remove bass; hear melody+harmony+groove.
3. Raise chords one octave.
4. Make every layer attack together.
5. Halve chord-attack density.
6. Replace blocks with arpeggios while retaining harmony.
7. Change closed to open voicing without changing rhythm.
8. Delay the groove entrance halfway through.
9. Thin rather than thicken the climax.
10. Render melody, bass, harmony, and groove alone, then together. Does each have a clear job?

## Deliberate boundary

This simplified arranging model uses melody, triadic harmony, monophonic bass, a
pitched simple-groove proxy, block/broken chords, register, density, and layer
entrances. Texture can also involve polyphony, heterophony, contrapuntal
independence, orchestration, doubling, call and response, countermelodies, timbral
layering, unison, and spatial arrangement. They are acknowledged, not implemented.
There is no random orchestration, synthesis framework, best-arrangement function,
or formal repetition/contrast system. Chapter 16 remains unimplemented.
