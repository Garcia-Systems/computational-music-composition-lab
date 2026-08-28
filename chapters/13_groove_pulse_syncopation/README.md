# Chapter 13 — Groove, Pulse, and Syncopation

Chapter 2 made durations computable, but `1, 1, .5, .5, 2` alone does not
explain why listeners hear strong positions, weak positions, or deliberate
displacement. This chapter asks: **what makes timed events feel like a recurring
pattern rather than merely a list of durations?**

```text
TIME → PULSE → SUBDIVISION → PATTERN → ACCENT → SYNCOPATION → GROOVE
```

Run the deterministic listening laboratory:

```bash
python -m composition_lab chapter-13
```

## A transparent rhythmic structure

A **pulse** is a recurring temporal reference. The chapter retains beats as
composition time and reuses Chapter 2's tempo conversion only when rendering.
At 120 BPM, one beat is 0.5 seconds. A four-beat, straight-eighth grid is:

```text
labels:     1   &   2   &   3   &   4   &
positions: 0.0 0.5 1.0 1.5 2.0 2.5 3.0 3.5
```

The end boundary, 4.0, is not another onset in this cycle. Sixteenths can use
`1 e & a`, but eighth notes remain the primary subdivision here. `GroovePattern`
stores only cycle length, subdivisions per beat, selected integer steps, and
optional velocities. `groove_events` turns those selections into ordinary
`NoteEvent` objects in beat space. There is no sequencer framework and no new
tempo system.

The **grid** contains every available position; the **pattern** selects some of
them. Velocity keeps accent independent from onset placement. The downbeat and
backbeat comparison activates identical eighth-note positions, emphasizing 1
and 3 in one version and 2 and 4 in the other. Backbeat emphasis is important
in many rock, pop, blues, funk, and related practices, but it is not a universal
definition of groove. Accent can also arise through duration, register,
articulation, timbre, density, and context.

## Syncopation, repetition, and layers

In this deliberately limited 4/4 model, integer positions are on-beat and `.5`
positions are eighth-note offbeats. The command compares quarter-note attacks
with the same attacks displaced half a beat, a mixed `X . X X . X . X`
pattern, and a short offbeat with a one-beat event that crosses the following
beat. Thus duration as well as onset can create syncopation. These are
constructed examples, not a universal detector or score.

A groove cycle repeats every four beats. One- and four-cycle renders let
repetition establish expectation. In another render, three literal cycles are
followed by one changed cycle; a separate accent mutation keeps onsets fixed and
changes one velocity. Objective attack density is reported as attacks divided
by cycle beats. It is not a quality judgment.

The composite uses pitched proxies rather than realistic drums:

```text
      1 & 2 & 3 & 4 &
LOW   X . . . X . . .   C3 proxy
MID   . . X . . . X .   C4 proxy
HIGH  X X X X X X X X   C5 proxy
```

The single-layer/composite comparison exposes interaction among roles. The
same composite is rendered at 70, 100, and 130 BPM without changing its
beat-relative structure. Finally, a small melodic phrase sounds over two
cycles, connecting Chapter 7 phrase thinking to a recurring foundation without
creating an accompaniment system or bass-line generator.

## Reader experiments

A. Keep every onset and move strong accents from 1/3 to 2/4.

B. Shift every attack by 0.5 beat.

C. Remove beat 1 while preserving the remainder of the cycle.

D. Add one `&` attack to quarter notes.

E. Lengthen an offbeat event so that it crosses a beat.

F. Compare 4, 6, 8, and 12 attacks in four beats; do not treat density as quality.

G. Repeat four times and mutate only the last cycle.

H. Retain the high layer but remove the 2-and-4 mid-role accents.

I. Change tempo only, leaving every beat-space value fixed.

## Deliberate limits

This narrow laboratory uses regular 4/4 pulse, straight-eighth subdivision,
simple velocity accents, on/offbeat distinctions, and four-beat cycles. Groove
can also involve swing, shuffle, microtiming, polymeter, polyrhythm, clave,
tuplets, asymmetric meters, rubato, and culturally specific rhythmic systems.
Those require their own contexts and are acknowledged rather than simulated.
No randomness, drum engine, universal syncopation index, or groove-quality score
is introduced. Chapter 14 and bass-line generation remain unimplemented.
