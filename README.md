# Computational Music Composition Lab

## An Executable Textbook for Composition, Generative Music, and Sound Design with Python and SuperCollider

This is a music composition textbook that you **read and execute**. Its central
question is:

> How can we represent musical ideas as data, transform them computationally,
> hear the results, and use those experiments to become better composers?

Python is the compositional and analytical engine: it makes musical decisions
visible as inspectable data and small transformations. Part VII begins using
SuperCollider as an optional synthesis and real-time performance engine while
retaining every earlier Python renderer. It is **not required** to run the
Python chapter commands or tests, which use only the standard library.

## The laboratory model

Every chapter should produce something audible. The book distinguishes three
layers, even when an early experiment temporarily combines them:

```text
COMPOSITION — What musical events happen and when?
       ↓
PERFORMANCE — How are those events performed?
       ↓
SOUND — What acoustic signal is produced?
```

Code is introduced when a musical question requires it—not as syntax for its
own sake. Important musical mechanics remain transparent, and future experiments
involving randomness will use explicit seeds so results can be reproduced.

## Requirements and setup

- Python 3.11 or newer
- No Python runtime dependencies for Chapters 0–23; SuperCollider is optional
  and used interactively only for Chapters 22–23 playback

From the repository root, either run directly:

```bash
python -m composition_lab chapter-00
python -m composition_lab chapter-01
python -m composition_lab chapter-02
python -m composition_lab chapter-03
python -m composition_lab chapter-04
python -m composition_lab chapter-05
python -m composition_lab chapter-06
python -m composition_lab chapter-07
python -m composition_lab chapter-08
python -m composition_lab chapter-09
python -m composition_lab chapter-10
python -m composition_lab chapter-11
python -m composition_lab chapter-12
python -m composition_lab chapter-13
python -m composition_lab chapter-14
python -m composition_lab chapter-15
python -m composition_lab chapter-16
python -m composition_lab chapter-17
python -m composition_lab chapter-18
python -m composition_lab chapter-19
python -m composition_lab chapter-20
python -m composition_lab chapter-21
python -m composition_lab chapter-22
python -m composition_lab chapter-23
python -m composition_lab chapter-24
```

or install an editable copy and use its console command:

```bash
python -m pip install -e .
composition-lab chapter-00
composition-lab chapter-01
composition-lab chapter-02
composition-lab chapter-03
composition-lab chapter-04
composition-lab chapter-05
composition-lab chapter-06
composition-lab chapter-07
composition-lab chapter-08
composition-lab chapter-09
composition-lab chapter-10
composition-lab chapter-11
composition-lab chapter-12
composition-lab chapter-13
composition-lab chapter-14
composition-lab chapter-15
composition-lab chapter-16
composition-lab chapter-17
composition-lab chapter-18
composition-lab chapter-19
composition-lab chapter-20
composition-lab chapter-21
composition-lab chapter-22
composition-lab chapter-23
composition-lab chapter-24
```

The commands create ordinary WAV files in `outputs/`; open them in any audio
player. Generated audio is ignored by Git; only `outputs/.gitkeep` preserves the
output directory.

## Completed chapters

- [Chapter 0 — The Composition Laboratory](chapters/00_composition_lab/README.md)
  carries one hard-coded-frequency idea from musical choice through waveform to
  listening, establishing the executable-textbook method.
- [Chapter 1 — Pitch Becomes Computable](chapters/01_pitch_becomes_computable/README.md)
  replaces stored frequencies with pitch names and integers, then makes
  transposition and interval preservation audible.
- [Chapter 2 — Time and Rhythm](chapters/02_time_and_rhythm/README.md)
  separates beats from seconds, then makes rhythm, tempo, rests, meter,
  subdivision, and syncopation audible.
- [Chapter 3 — The Musical Event](chapters/03_musical_event/README.md)
  joins pitch, onset, duration, and performance intensity in an immutable,
  inspectable event; events can overlap on a shared rendered timeline.
- [Chapter 4 — Scales, Keys, and Tonality](chapters/04_scales_keys_tonality/README.md)
  organizes pitch choices through transparent major and natural-minor patterns,
  tonics, scale degrees, and octave-independent membership.
- [Chapter 5 — Intervals and Melodic Motion](chapters/05_intervals_melodic_motion/README.md)
  measures signed motion, contour directions, range, and compact melodic profiles,
  then makes controlled interval, repetition, range, and contour comparisons audible.
- [Chapter 6 — Motifs and Transformation](chapters/06_motifs_transformation/README.md)
  turns short `NoteEvent` ideas into repeatable, transposable, reversible,
  invertible, time-scalable material and combines those changes in a development study.
- [Chapter 7 — Phrases, Questions, and Closure](chapters/07_phrases_questions_closure/README.md)
  arranges motifs into openings, fragmenting continuations, designed climaxes,
  melodic closures, and related question-and-answer phrase pairs.
- [Chapter 8 — Chords and Vertical Structure](chapters/08_chords_vertical_structure/README.md)
  organizes simultaneous pitches as major, minor, and diminished triads, then
  makes inversion, voicing, arpeggiation, and diatonic chord construction audible.
- [Chapter 9 — Chord Progressions and Harmonic Motion](chapters/09_chord_progressions_harmonic_motion/README.md)
  orders diatonic triads on a timeline, separating progression identity from
  harmonic rhythm and transposing scale-degree patterns between keys.
- [Chapter 10 — Harmonic Function and Tension](chapters/10_harmonic_function_tension/README.md)
  gives major-key harmonic motion broad tonic, predominant, and dominant roles,
  then compares expectation, resolution, deceptive motion, duration, and phrase shape.
- [Chapter 11 — Voice Leading and Efficient Motion](chapters/11_voice_leading_efficient_motion/README.md)
  separates harmonic identity from voicing, measures fixed voice positions, and makes
  deterministic inversion choices, common tones, and interacting melodic lines audible.
- [Chapter 12 — Melody Against Harmony](chapters/12_melody_against_harmony/README.md)
  aligns melody onsets and sustained events with harmonic spans, distinguishes
  chord tones from conservatively named non-chord tones, and makes context audible.
- [Chapter 13 — Groove, Pulse, and Syncopation](chapters/13_groove_pulse_syncopation/README.md)
  makes repeated timing, accent, displacement, expectation, and interacting
  rhythmic roles audible on a transparent beat-relative grid.
- [Chapter 14 — Bass as Harmony, Rhythm, and Melody](chapters/14_bass_harmony_rhythm_melody/README.md)
  connects harmonic roots, chord roles, register, groove onsets, passing motion,
  pedals, inversion, and measurable monophonic contour.
- [Chapter 15 — Accompaniment and Texture](chapters/15_accompaniment_texture/README.md)
  distributes independent melody, harmony, bass, and groove roles through register,
  activity, voicing, velocity, entrances, and deterministic accompaniment patterns.
- [Chapter 16 — Repetition, Contrast, and Variation](chapters/16_repetition_contrast_variation/README.md)
  turns passages into developing material through literal repetition, controlled one-variable
  variation, deliberate contrast, motivic continuity, literal return, and varied return.
- [Chapter 17 — Musical Form](chapters/17_musical_form/README.md)
  makes passages into locally normalized sections and assembles transparent plans
  for binary, ternary, AABA, verse/chorus, blues, and through-composed studies.
- [Chapter 18 — Constraint-Based Composition](chapters/18_constraint_based_composition/README.md)
  uses inspectable objective rules to enumerate, reject, retain, describe, and
  render multiple pitch and rhythm candidates without treating rules as taste.
- [Chapter 19 — Controlled Randomness](chapters/19_controlled_randomness/README.md)
  uses explicit seeds, bounded and weighted choice, rejection sampling, random
  walks, independent RNG streams, decision logs, and reproducible listening studies.
- [Chapter 20 — Musical Memory](chapters/20_musical_memory/README.md)
  derives inspectable first-order transition counts from short symbolic musical
  sequences, then uses seeded conditional choice for pitch and rhythm studies.
- [Chapter 21 — Evaluation: Describing Generated Music](chapters/21_evaluation_describing_generated_music/README.md)
  describes melody, rhythm, repetition, harmony alignment, training overlap,
  constraints, and generator diversity while leaving aesthetic judgment to the listener.

### Part VII — SuperCollider

- [Chapter 22 — From Notes to Sound](chapters/22_from_notes_to_sound/README.md)
  sends Python-authored musical events through an inspectable JSON bridge to a
  simple real-time SuperCollider sine SynthDef while retaining Python reference audio.
  Interactive playback uses `supercollider/chapter_22_first_sound.scd`.
- [Chapter 23 — Synthesizers as Instruments](chapters/23_synthesizers_as_instruments/README.md)
  keeps compositions fixed while waveforms, pulse width, harmonic mixtures,
  detuning, register, and explicit layer instrument maps change their timbre.
  Interactive playback uses `supercollider/chapter_23_synthesizers_as_instruments.scd`.
- [Chapter 24 — Envelopes, Filters, and Articulation](chapters/24_envelopes_filters_articulation/README.md)
  uses ADSR, low-pass filtering, velocity response, and explicit gate ratios to
  shape a fixed composition. Interactive playback uses
  `supercollider/chapter_24_envelopes_filters_articulation.scd`.

The progression so far is direct: Chapter 0 shows that sound can be generated
from numerical musical decisions; Chapter 1 makes pitch relationships
computable; Chapter 2 makes musical time computable; Chapter 3 makes music into
structured events; Chapter 4 organizes pitch choices through tonal systems;
Chapter 5 makes melodic movement measurable without treating measurement as judgment;
Chapter 6 makes small musical ideas transformable material; Chapter 7 makes
motifs into directed musical phrases; Chapter 8 makes simultaneous pitches into
harmonic structures; Chapter 9 makes chords into harmonic motion through time;
Chapter 10 gives that motion functional direction and resolution; Chapter 11 makes
harmonic progressions into interacting melodic voices; Chapter 12 gives melody
meaning relative to the harmony beneath it; Chapter 13 makes repeated timing,
accent, and displacement into groove; Chapter 14 makes bass connect harmony,
groove, and melodic motion.
Chapter 15 makes independent musical layers into texture and arrangement. Chapter 16 makes
repetition, contrast, and variation turn passages into developing musical material. Chapter 17
makes passages into sections, and sections into musical form. Chapter 18 makes explicit musical
constraints define spaces of possible compositions that the computer can search. Chapter 19
makes those spaces explorable with seeded randomness without sacrificing reproducibility.
Chapter 20 makes future choices depend on learned local relationships from prior
musical sequences. Chapter 21 describes generated music with structural metrics
while leaving aesthetic judgment to the listener. Chapter 22 makes Python musical
events cross into a dedicated synthesis engine and become real-time synthesized sound.
Chapter 23 turns a bare tone into reusable instruments with waveforms,
oscillator mixtures, and bounded synthesis parameters while event data stays fixed.
Chapter 24 shapes those instruments over time and frequency with envelopes,
filters, velocity response, and articulation while the composition stays fixed.

## Planned journey

Only Chapters 0 through 24 exist today. The broad route—not a claim of implemented
features beyond those chapters—is:

```text
sound / notes → pitch → rhythm → musical events → scales and tonality
→ intervals → motifs → phrases → chords → harmony → voice leading
→ melody against harmony → groove → bass → texture → variation → form
→ constraint-based composition → controlled randomness → musical memory
→ structural evaluation → synthesis → SuperCollider
→ OSC → algorithmic performance → style laboratories → complete composition
```

## Run the tests

```bash
python -m unittest discover -s tests -v
```
