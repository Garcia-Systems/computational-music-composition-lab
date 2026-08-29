# Chapter 23 — Synthesizers as Instruments

> What turns a bare oscillator into an instrument with a recognizable sonic
> identity and useful musical controls?

```text
OSCILLATOR → WAVEFORM → HARMONIC CONTENT → OSCILLATOR MIXTURE
→ REGISTER + DETUNING + BALANCE → INSTRUMENT PARAMETERS → REUSABLE SYNTHESIZER
```

## Pitch stays fixed; spectrum changes

Chapter 22 carried Python events into `\simpleSine`. A sine oscillator contains
one sinusoidal frequency component. It is useful for learning synthesis, but
most familiar instrumental sounds contain richer spectra. It is not inferior;
it is **spectrally simple**.

Pitch answers, approximately, **what periodic rate do we hear?** Timbre answers
**what spectral and temporal structure accompanies that pitch?** `SinOsc`,
`Saw`, and `Pulse` are useful digital synthesis models whose spectra differ in
systematic ways; they should not be mistaken for perfect ideal mathematical
waveforms at every frequency.

- sine is approximately one frequency component;
- saw contains both even and odd members of a harmonic series;
- pulse has a distribution that changes with pulse width (at `0.5` it is
  square-like).

The script holds A4 (440 Hz), amplitude, envelope, and duration constant while
changing only waveform: **change one sound variable → listen → compare**.
Equal amplitude parameters do not guarantee equal perceived loudness, because
spectral energy differs. This is an approximate comparison, not a calibrated
psychoacoustic test, and no normalization machinery is hidden in it.

## A small, shared interface

| metadata | SynthDef | oscillator(s) | extra controls |
|---|---|---|---|
| `sine` | `\simpleSine` | `SinOsc` | none |
| `saw` | `\simpleSaw` | `Saw` | none |
| `pulse` | `\simplePulse` | `Pulse` | `width` |
| `two_partial` | `\twoPartial` | two `SinOsc`s | `partialRatio`, `partialMix` |
| `detuned_saw` | `\detunedSaw` | two `Saw`s | `detune` (Hz) |

All accept `freq`, `amp`, `gate`, and `pan`, use the same simple ASR envelope,
and free themselves after release. Chapter examples keep `amp` in 0–0.2,
`width` in 0.1–0.9, `partialMix` in 0–0.5, and detuning to a few hertz. These are
safe pedagogical ranges, not universal technical limits. Saw and pulse are
intentionally raw and unfiltered.

Pulse widths `0.5`, `0.25`, and `0.1` change waveform shape and harmonic
spectrum without changing 440-Hz pitch. The register study uses the same saw at
A2, A3, A4, and A5: frequency moves all spectral components, so the same preset
may behave differently across register.

## One note is not necessarily one oscillator

`\twoPartial` combines a fundamental with a second sine at
`freq * partialRatio`. Integer multipliers 2, 3, and 4 are harmonic
relationships. `partialMix` controls how prominent that upper component is.
The 880-Hz oscillator in the 440-Hz example is synthesis inside one Synth—not a
second Python `NoteEvent`.

`\detunedSaw` averages saws at `freq` and `freq + detune`. Nearby frequencies
can create beating and a thicker result. **Transposition** intentionally changes
musical pitch; **detuning** offsets simultaneous oscillators representing one
intended note. It is synthesis, not a newly composed harmony.

Both multi-oscillator instruments leave headroom: detuned saw explicitly uses
`(osc1 + osc2) * 0.5`; the partial mixture crossfades and applies a conservative
scale. They never sum two full-amplitude voices.

Polyphony means multiple musical notes at once; an oscillator stack means
multiple signal generators inside one note. A C-major triad played by
`\detunedSaw` is three `NoteEvent`s and three Synths, but six oscillators.
Increasing instrument complexity therefore multiplies synthesis cost as
polyphony grows; no CPU benchmark is needed to understand the distinction.

## Composition and playback specifications

Run:

```bash
python -m composition_lab chapter-23
```

The command writes one C4–E4–G4–C5 melody and one eight-beat capstone event
file. Chapter 22 fields (`pitch`, `frequency`, `start`, `duration`, `velocity`)
remain valid; `layer` is descriptive metadata. Event-level `instrument` is
optional and defaults conceptually to sine when absent. Python validates the
small names above when such metadata is requested, rather than accepting a
string as executable SuperCollider code.

More importantly, the capstone has two separate maps:

```text
all sine: melody=sine, harmony=sine, bass=sine
colored:  melody=pulse, harmony=two_partial, bass=detuned_saw
```

Both maps point at the *exact same* event file. Musical roles, pitches, starts,
durations, and velocities do not change. The composer assigns this mapping
explicitly; range-based orchestration and automatic instrument selection are
not implemented. The SuperCollider dispatch table validates known metadata and
warns then falls back to `\simpleSine` for an unknown name.

```text
ONE NoteEvent → ONE Synth → ONE OR MORE OSCILLATORS

WHAT IS PLAYED                         HOW IT SOUNDS
C4 at beat 2 for one beat       ≠      sine / saw / pulse / mixture / detuned pair
```

## Listening laboratory

Open `supercollider/chapter_23_synthesizers_as_instruments.scd`, boot first,
load the SynthDefs second, then evaluate comparisons in numbered order.

1. Play the unchanged melody through sine, saw, pulse, and detuned saw. What
   changes when pitch and rhythm remain identical?
2. Compare pulse widths 0.5, 0.3, and 0.1. How does character change while
   pitch stays 440 Hz?
3. Try partial ratios 2, 3, and 4 at a low mix. How does the harmonic relation
   change timbre while the fundamental remains tied to the note?
4. Try partial mixes 0.05, 0.20, and 0.40. When is the upper component prominent?
5. Compare detune 0, a small offset, and a slightly larger offset. When does a
   stable pitch begin to sound beating or widened?
6. Compare one preset in low and high registers. Does it work identically?
7. Compare the same C-major triad through sine, saw, and pulse at lower
   per-voice gain. Does timbre change how dense the same pitches feel?
8. Compare sine and saw on the same bass note; then exchange melody and bass
   mappings without editing notes. How does role perception change?
9. Compare one oscillator with two on the same note and observe both timbre and
   headroom.

## Deliberate boundary

Waveform is only one contributor to identity. Envelope, filtering, dynamics,
noise, modulation, articulation, register, performance behavior, and effects
also matter. This chapter keeps one basic amplitude envelope and adds **no
filters, noise, LFO/PWM animation, FM, AM, ring modulation, reverb, delay,
chorus, distortion, OSC, automatic orchestration, or drum synthesis**. Chapter
24 will address envelopes, filters, velocity, duration, and articulation; it is
not implemented here.

## Bridge forward

Oscillators establish spectrum, but musical behavior also depends on change through time. Chapter 24 adds envelope, filtering, velocity mapping, and articulation.
