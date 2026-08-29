# Computational Music Composition Lab

## An executable textbook for composition, generative music, and sound design with Python and SuperCollider

**Executable textbook curriculum: complete**
**Chapters: 0–35**

This is a composition textbook that you **read, run, and hear**. It is for motivated readers who know basic Python or are willing to trace small functions; music-theory terms are introduced as the experiments need them. Its organizing question is:

> How can we represent musical ideas as data, transform them computationally, hear the results, and use those experiments to become better composers?

The curriculum is complete, not “finished forever”: corrections and bounded revisions remain welcome, while notation, MIDI workflows, microtonality, orchestration, and machine learning are deliberately outside this edition.

## Start here

1. Install **Python 3.11 or newer**.
2. From a fresh clone, run `python -m pip install -e .`. The declared `python-osc` dependency supports optional live OSC; dry-run chapters do not contact a network or audio server.
3. Read [Chapter 0](chapters/00_composition_lab/README.md), then run `python -m composition_lab chapter-00`.
4. Open `outputs/chapter_00_first_composition.wav` in any audio player. Do not substitute reading the terminal output for listening.
5. Continue sequentially. Use `python -m composition_lab chapters` to see every command.
6. Before Part VII, optionally install SuperCollider and follow [the concise setup guide](supercollider/README.md). SuperCollider is not required for Python reference WAVs, dry runs, structural verification, or tests.

Generated files use predictable `outputs/chapter_XX_*` names. They are intentionally ignored by Git; `outputs/.gitkeep` preserves the directory. Committed Chapter 35 report examples document the canonical audit, while rerunning commands may regenerate ignored working artifacts.

## The book's architecture

```text
MUSICAL IDEA
    ↓
SYMBOLIC EVENTS (pitch; onset and duration in beats; velocity)
    ↓
TRANSFORMATION / GENERATION
    ↓
FORM + LAYERS
    ↓
PLAYBACK CONFIGURATION
    ↓
REFERENCE WAV or OSC CONTROL → SUPERCOLLIDER
    ↓
AUDIO
```

```text
COMPOSITION — what musical events happen and when
       ↓
PERFORMANCE — how those events are played
       ↓
SOUND — the acoustic signal produced

PROVENANCE — who or what made the decisions at every layer
```

OSC messages are control data, **not audio samples**. Symbolic timing remains in beats; tempo converts beats to seconds at rendering or real-time scheduling boundaries. MIDI-style pitch integers identify equal-tempered pitches; frequency in Hz is derived only when sound or a protocol payload needs it.

## Experimental method

```text
HYPOTHESIS
    ↓
CHANGE ONE MUSICAL VARIABLE
    ↓
GENERATE
    ↓
LISTEN
    ↓
COMPARE
    ↓
EXPLAIN
```

Controlled comparisons matter: the same pitches with different rhythm answer a clearer question than two wholly different passages. Metrics describe measurable structure; constraints validate stated rules; neither provides beauty, creativity, authenticity, or authorship scores. See the concise [glossary](GLOSSARY.md) for the vocabulary used throughout the book.

## Commands and verification

```bash
python -m composition_lab                 # useful help
python -m composition_lab chapters        # ordered 00–35 listing
python -m composition_lab chapter-00      # any chapter-00 … chapter-35
python -m composition_lab verify-book     # static structure; no rendering or OSC
python -m unittest discover -s tests -v
```

Chapter 26 and later commands default to file output or simulation where applicable. Add `--live` only after starting the documented Chapter 26 SuperCollider receiver; Python never launches SuperCollider for you. Run `python -m composition_lab chapter-XX --help` to inspect the intentionally shared, small option set.

## Curriculum

Each Part begins from an abstraction the reader has already used and introduces the next unresolved compositional question.

### Part I — Music Becomes Data (0–3)

Turn pitch, time, and intensity into inspectable events.

- [Chapter 0 — The Composition Laboratory](chapters/00_composition_lab/README.md) — `python -m composition_lab chapter-00`
- [Chapter 1 — Pitch Becomes Computable](chapters/01_pitch_becomes_computable/README.md) — `python -m composition_lab chapter-01`
- [Chapter 2 — Time and Rhythm](chapters/02_time_and_rhythm/README.md) — `python -m composition_lab chapter-02`
- [Chapter 3 — The Musical Event](chapters/03_musical_event/README.md) — `python -m composition_lab chapter-03`

### Part II — Building Musical Ideas (4–7)

Organize pitches, measure melody, transform motifs, and shape phrases.

- [Chapter 4 — Scales, Keys, and Tonality](chapters/04_scales_keys_tonality/README.md) — `python -m composition_lab chapter-04`
- [Chapter 5 — Intervals and Melodic Motion](chapters/05_intervals_melodic_motion/README.md) — `python -m composition_lab chapter-05`
- [Chapter 6 — Motifs and Transformation](chapters/06_motifs_transformation/README.md) — `python -m composition_lab chapter-06`
- [Chapter 7 — Phrases, Questions, and Closure](chapters/07_phrases_questions_closure/README.md) — `python -m composition_lab chapter-07`

### Part III — Harmony (8–12)

Build vertical structures, progressions, function, voice leading, and melody/harmony context.

- [Chapter 8 — Chords and Vertical Structure](chapters/08_chords_vertical_structure/README.md) — `python -m composition_lab chapter-08`
- [Chapter 9 — Chord Progressions and Harmonic Motion](chapters/09_chord_progressions_harmonic_motion/README.md) — `python -m composition_lab chapter-09`
- [Chapter 10 — Harmonic Function and Tension](chapters/10_harmonic_function_tension/README.md) — `python -m composition_lab chapter-10`
- [Chapter 11 — Voice Leading and Efficient Motion](chapters/11_voice_leading_efficient_motion/README.md) — `python -m composition_lab chapter-11`
- [Chapter 12 — Melody Against Harmony](chapters/12_melody_against_harmony/README.md) — `python -m composition_lab chapter-12`

### Part IV — Rhythm, Bass, Texture (13–15)

Coordinate pulse, low-register motion, accompaniment, and layers.

- [Chapter 13 — Groove, Pulse, and Syncopation](chapters/13_groove_pulse_syncopation/README.md) — `python -m composition_lab chapter-13`
- [Chapter 14 — Bass as Harmony, Rhythm, and Melody](chapters/14_bass_harmony_rhythm_melody/README.md) — `python -m composition_lab chapter-14`
- [Chapter 15 — Accompaniment and Texture](chapters/15_accompaniment_texture/README.md) — `python -m composition_lab chapter-15`

### Part V — Form and Composition (16–18)

Develop passages, arrange sections, and define bounded possibility spaces.

- [Chapter 16 — Repetition, Contrast, and Variation](chapters/16_repetition_contrast_variation/README.md) — `python -m composition_lab chapter-16`
- [Chapter 17 — Musical Form](chapters/17_musical_form/README.md) — `python -m composition_lab chapter-17`
- [Chapter 18 — Constraint-Based Composition](chapters/18_constraint_based_composition/README.md) — `python -m composition_lab chapter-18`

### Part VI — Generative Composition (19–21)

Explore with seeded choice, history-dependent models, and descriptive evaluation.

- [Chapter 19 — Controlled Randomness](chapters/19_controlled_randomness/README.md) — `python -m composition_lab chapter-19`
- [Chapter 20 — Musical Memory](chapters/20_musical_memory/README.md) — `python -m composition_lab chapter-20`
- [Chapter 21 — Evaluation: Describing Generated Music](chapters/21_evaluation_describing_generated_music/README.md) — `python -m composition_lab chapter-21`

### Part VII — SuperCollider (22–25)

Separate a fixed score from synthesis, articulation, and spatial playback.

- [Chapter 22 — From Notes to Sound](chapters/22_from_notes_to_sound/README.md) — `python -m composition_lab chapter-22`
- [Chapter 23 — Synthesizers as Instruments](chapters/23_synthesizers_as_instruments/README.md) — `python -m composition_lab chapter-23`
- [Chapter 24 — Envelopes, Filters, and Articulation](chapters/24_envelopes_filters_articulation/README.md) — `python -m composition_lab chapter-24`
- [Chapter 25 — Space, Delay, Reverb, and Signal Routing](chapters/25_space_delay_reverb_routing/README.md) — `python -m composition_lab chapter-25`

### Part VIII — Python Meets SuperCollider (26–28)

Move from OSC transport to complete-score and online-generation performance models.

- [Chapter 26 — OSC: Sending Musical Events in Real Time](chapters/26_osc_real_time/README.md) — `python -m composition_lab chapter-26`
- [Chapter 27 — The Composition Engine](chapters/27_composition_engine/README.md) — `python -m composition_lab chapter-27`
- [Chapter 28 — Algorithmic Performance](chapters/28_algorithmic_performance/README.md) — `python -m composition_lab chapter-28`

### Part IX — Style Labs (29–32)

Test shared infrastructure in four limited, explicitly non-exhaustive compositional models.

- [Chapter 29 — Blues](chapters/29_blues/README.md) — `python -m composition_lab chapter-29`
- [Chapter 30 — Rock and Songwriting](chapters/30_rock_songwriting/README.md) — `python -m composition_lab chapter-30`
- [Chapter 31 — Classical-Style Development](chapters/31_classical_style_development/README.md) — `python -m composition_lab chapter-31`
- [Chapter 32 — Minimalism and Generative Music](chapters/32_minimalism_generative_music/README.md) — `python -m composition_lab chapter-32`

### Part X — Capstone (33–35)

Delegate decisions, compose one canonical piece, and audit its provenance.

- [Chapter 33 — Human + Algorithm](chapters/33_human_algorithm/README.md) — `python -m composition_lab chapter-33`
- [Chapter 34 — Compose a Complete Piece](chapters/34_compose_complete_piece/README.md) — `python -m composition_lab chapter-34`
- [Chapter 35 — What Did the Computer Actually Compose?](chapters/35_what_did_the_computer_compose/README.md) — `python -m composition_lab chapter-35`

## How audio works

Chapters 0–21 retain a deliberately small Python reference renderer. It calculates buffered floating-point samples, mixes events on one timeline, applies headroom only if a mix would clip, clips safely at PCM conversion, and writes a complete WAV; Python does not make one speaker call per sample. A DAC in the playback device later converts the stored PCM stream into an analog signal.

Part VII adds `sclang` (the SuperCollider language process) and `scsynth` (the audio server). The score remains inspectable Python data. Parts VIII–X can translate finalized or incrementally generated events into OSC messages, but non-live defaults remain useful when SuperCollider is absent.

## Philosophy and limits

This repository is an executable textbook, not a production audio engine, DAW, comprehensive theory, genre classifier, or autonomous composer. Major and natural-minor scales, mostly triadic tonal harmony, simple grids, abstract oscillator instruments, and integer pitches are teaching models. Pitched proxies stand in for percussion in some reference WAVs. Style labs investigate selected structures and do not model whole genres or traditions.

Some repeated early code is **pedagogical repetition**: Chapter 0 should visibly store frequency even though later chapters derive it from pitch. Shared event placement, rendering, OSC conversion, stable seed derivation, and provenance logic are centralized where repetition would instead create conflicting definitions. Small transparent functions preserve the trace from musical decision to data to transformation to sound.

For findings, resolved issues, verification scope, and deliberately deferred work, read [BOOK_AUDIT.md](BOOK_AUDIT.md).

---

**Executable textbook curriculum: complete**
**Chapters: 0–35**
