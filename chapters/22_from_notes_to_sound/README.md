# Chapter 22 — From Notes to Sound

> How can symbolic musical structures generated in Python become richer
> synthesized sound in a dedicated audio engine?

## Part VII — SuperCollider

The book's architecture now becomes physically visible:

```text
COMPOSITION (Python: what happens and when)
       ↓
PERFORMANCE (event starts, durations, velocity, scheduling)
       ↓
SOUND (SuperCollider synthesis graph and audio server)
```

Python remains the compositional brain: music theory, event representation,
generation, form, and analysis stay there. SuperCollider begins to own the sound
layer. A sound generator should know `freq`, `amp`, `gate`, and `pan`; it should
not know scales, keys, motifs, chords, Markov probabilities, or form.

## Why add another renderer?

The Python renderer intentionally exposed frequency, amplitude, samples, timing,
overlap, mixing, and WAV output. That educational path remains intact and works
without SuperCollider. A dedicated engine makes reusable synthesis graphs,
envelopes, oscillator choices, filters, effects, polyphony, and real-time
scheduling easier to develop later. Capability is the distinction—not a claim
that one engine automatically sounds more artistic or professional.

Chapter 0 asks Python to calculate each waveform sample. Chapter 22 describes a
signal graph and asks `scsynth` to calculate those samples. Both paths use sine
waves here, deliberately isolating the **rendering engine** from sound design.

## Language and server

SuperCollider has two pieces important today:

```text
sclang — language/interpreter; sends instructions
                 ↓
scsynth — audio synthesis server; produces audio
```

The language process and audio server are separate. Synth definitions and synth
instances ultimately run on the server. Open
`supercollider/chapter_22_first_sound.scd`, evaluate `s.boot;`, and wait for the
server before evaluating sound blocks. The smallest graph is:

```supercollider
{ SinOsc.ar(440, 0, 0.1) }.play;
```

`SinOsc` is a sine oscillator, `440` is frequency in hertz, and `0.1` is
amplitude. Stop that temporary node before continuing. Pitch 69 is still A4 at
440 Hz—not new SuperCollider theory, but Chapter 1's Python conversion arriving
at a new consumer.

## Blueprint, instance, and gate

A `SynthDef` is a reusable signal-processing definition: an instrument
blueprint. `Synth(\simpleSine, ...)` creates a running instance of that blueprint.
The definition uses one `SinOsc`, an `Env.asr` envelope through `EnvGen`, centered
stereo output through `Pan2`, and only `freq`, `amp`, `gate`, and `pan` controls.

Creating a Synth with gate 1 begins the attack. Setting gate 0 begins release;
`doneAction: 2` frees the instance after release. This is preferable to an
indefinite raw oscillator and teaches a lifetime usable by later real-time event
triggering. Several simultaneous synths sum, so voices use conservative gains.
Polyphony is simply multiple running Synth instances—the same sequential-versus-
overlapping distinction introduced in Chapter 3, without a voice manager.

## The offline bridge

Run:

```bash
python -m composition_lab chapter-22
```

The command does not locate or launch `sclang`. It writes deterministic JSON:

```json
{
  "pitch": 60,
  "frequency": 261.6255653005986,
  "start": 0.0,
  "duration": 1.0,
  "velocity": 90
}
```

Both pitch and frequency are kept so the conversion is visible and Python
remains authoritative. Starts and durations remain beats. SuperCollider maps
`amp = (velocity / 127) * 0.15`; this is one explicit, conservative control
mapping, not a claim that velocity equals perceived or acoustic loudness.

The first export plays C4, E4, G4, C5 at beats 0–3, then a C-major triad whose
three notes all retain start 4. A 120 BPM `TempoClock` turns musical beats into
server scheduling. The script sorts/group events by absolute start, waits only
the delta from the preceding onset, triggers an entire equal-onset group, and
schedules every gate-off independently. It therefore preserves chords and notes
that overlap rather than incorrectly waiting each note's duration.

## Controlled comparisons and capstone

The command creates:

- `chapter_22_events.json` and `chapter_22_python_reference.wav`;
- `chapter_22_capstone_events.json` and
  `chapter_22_capstone_python_reference.wav`.

The modest eight-beat capstone combines a C-major melody, I–IV–V–I sustained
triads, and bass roots. Its optional `layer` field is inspection metadata only;
all roles use exactly the same `\simpleSine` SynthDef.

Trace one melody event end to end:

```text
Python NoteEvent: pitch=64, start=1, duration=1, velocity=90
       ↓ pitch_to_frequency
329.627557 Hz in JSON
       ↓ SuperCollider: amp=(90/127)*0.15, gate=1
SinOsc → ASR envelope → centered Pan2 output
       ↓ duration scheduled as one TempoClock beat
gate=0 → release → node freed → scsynth → speakers
```

The Python renderer calculates samples and writes an offline mono WAV.
SuperCollider reads composition data, schedules synths, and produces real-time
stereo audio. Neither path erases the educational value of the other.

## Experiments

1. Change direct frequency from 440 to 220 or 880. What changed physically and
   perceptually?
2. Compare safe amplitudes 0.03, 0.1, and 0.2. How is this unlike pitch change?
3. Slightly change attack or release. How can equal pitch and duration feel
   different when amplitude shape changes?
4. Generate C–Eb–G frequencies with Python, replacing C–E–G. What changed while
   synthesis stayed identical?
5. Change `tempoBpm` among 90, 120, and 150 without changing event beats.
6. Move an onset before the preceding release and listen for Chapter 3 overlap.
7. Compare each Python reference WAV with interactive SuperCollider playback.
   Which differences arise from envelope, gain, implementation, or scheduling
   rather than composition?

Optional recording uses `s.record;` and `s.stopRecording;`; no path is assumed.
Use `s.freeAll;` to free server synths or the IDE emergency stop, equivalent to
`CmdPeriod.run;`, if an experiment runs unexpectedly.

## Boundary kept for Chapter 23

This primitive sine-plus-envelope graph is a signal-path lesson, not a piano,
guitar, bass, drum, orchestra, polished electronic instrument, or promise of
professional sound. This chapter adds no MIDI, OSC, live Python streaming,
patterns, custom classes, filters, effects, modulation, extra oscillators, or
advanced waveforms. Chapter 23—not this chapter—will ask how a synthesizer gains
a recognizable sonic identity and useful musical controls.
