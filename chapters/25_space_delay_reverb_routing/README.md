# Chapter 25 — Space, Delay, Reverb, and Signal Routing

> Once an instrument has pitch, timbre, and articulation, how can delay,
> reverberation, stereo placement, and signal routing place that sound inside
> an acoustic space?

```text
INSTRUMENT SIGNAL → DRY SOUND → PAN → EFFECT SEND → DELAY / REVERB
                                                   ↓
                              FINAL STEREO OUTPUT ← WET SIGNAL
```

Python still decides **what** happens: events, layers, harmony, and form.
Playback metadata says how a layer is articulated, panned, and sent. SuperCollider
produces and routes the signal. Effects do not become composers.

## Dry, wet, and pan

A **dry signal** is the original instrument signal before a spatial effect is
mixed in. A **wet signal** has passed through an effect. The chapter uses:

```text
final output = dry signal + wet delay return + wet reverb return
```

Wet is not a synonym for better. Compare 100% dry, mostly dry, and more wet while
holding the note and effect settings fixed. Because each effect return is 100%
wet, changing a layer's send changes effect amount without doubling its dry path.

SuperCollider's `Pan2` convention is `-1` left, `0` center, and `+1` right.
Python validates that range. The controlled pan study replays one note at
`-0.8`, `0`, and `0.8`, keeping pitch, velocity, envelope, filter, and duration
fixed. Stereo placement may be less apparent through mono playback.

Pan is not added to `NoteEvent`. **C4 at beat 2 remains the same event whether
heard left, center, or right.** Pan belongs to `LayerPlayback`, beside gate ratio
and send levels. Missing Chapter 25 fields default to center and zero sends, so
Chapter 24-style playback remains dry and valid.

## Delay: physical and musical time

A delay produces a time-shifted copy of a signal:

```text
dry note → wait → repeat
```

The first experiment uses `DelayC` with feedback zero: dry plus one delayed
copy. Compare 0.1, 0.25, and 0.5 seconds. Only after that physical-time comparison
do we reconnect to beat time through Chapter 2's existing `beats_to_seconds`:

```text
120 BPM: one beat = 0.5 seconds
0.5 beat delay = 0.25 seconds
```

Configuration stores `delay_beats`; Python derives `delay_seconds`. Keeping a
0.5-beat delay while changing tempo therefore changes seconds. Try 0.25, 0.5,
and 1 beat at fixed tempo and listen for their relationship to the grid.

Feedback routes part of delayed audio back into the delay, creating further
echoes. The SynthDef clips its feedback to `0...0.8`, and Python accepts only
`0 <= feedback < 1`; the supplied value is 0.35. Compare 0.2, 0.4, and 0.6.
This prevents runaway examples while making persistence controllable.

An acoustic echo can resemble a note, but it is not necessarily a new event:

```text
COMPOSITION: C4 at beat 0 + C4 at beat 1 (two NoteEvents)
EFFECT:      C4 at beat 0 → delayed audio (one NoteEvent)
composed repetition != delay repetition
```

A delay repeats whatever audio it receives. It knows no key, scale, chord, or
phrase and cannot make harmonic decisions.

## Reverb and tails

Reverberation is a dense collection of delayed reflections that creates the
impression of acoustic space. `FreeVerb` provides a qualitative `room` control
for room-size-like character and `damp`, which reduces high-frequency
persistence. These are not physical dimensions. Compare room values 0.25, 0.5,
and 0.75 while keeping send and damping fixed.

The reverb sets `mix: 1.0`, so its SynthDef outputs wet audio only. Distinct
repeats characterize the delay experiment; a dense reflection-like tail
characterizes reverb. A `NoteEvent` ending does not mean all sound stops: an
instrument release and a reverb tail can continue. Reverb does not understand
section boundaries or form even when a tail overlaps the next section.

## Audio buses and send/return routing

An **audio bus** moves audio-rate signals between synths inside the server. A
control bus instead carries control values; this chapter needs no control buses.

```text
Instrument Synth
      |
      v
   Audio Bus
      |
      v
  Effect Synth
      |
      v
   Output
```

The practical send/return design is:

```text
DRY PATH:  routedSaw → Pan2 → hardware output
SEND PATH: routedSaw → stereo effect bus → wet-only effect → hardware output
```

The routing-aware Chapter 25 instrument writes a panned stereo signal directly
to `dryOut`, and scaled copies to stereo delay and reverb buses. Historical
SynthDefs remain unchanged. `sendLevel` is the copy's level; it is not an
internal dry/wet mix. With no send, a bus and its return remain silent.

`sourceGroup` precedes `fxGroup`. Instruments therefore write buses before the
persistent effects read them with `In.ar` in the same server block. One delay
and one reverb Synth live for the experiment or piece rather than being created
per note. Many sources can feed one reverb bus:

```text
melody  ─┐
harmony ─┼→ shared reverb bus → one persistent wet return
bass    ─┘
```

The example uses restrained values:

| Layer | Pan | Delay send | Reverb send |
|---|---:|---:|---:|
| Melody | 0.2 | 0.15 | 0.30 |
| Harmony | -0.3 | 0.05 | 0.38 |
| Bass | 0.0 | 0.00 | 0.10 |

The lower bass send preserves clarity in this study; it is a design choice, not
a universal prohibition. Conservative voice gain and return amplitudes leave
headroom for dry + delay + reverb summing. No limiter or mastering chain hides
that gain staging.

## Run the file-based capstone

```bash
python -m composition_lab chapter-25
```

The command requires no SuperCollider and writes:

```text
outputs/chapter_25_capstone_events.json
outputs/chapter_25_playback_map.json
outputs/chapter_25_effects.json
```

The 16-beat event file repeats the existing I–IV–V–I melody, harmony, and bass
study. The playback document contains dry and spatial versions that reference
the exact same events; only pan and send metadata changes. Global delay and
reverb parameters live separately rather than being duplicated for every layer.
One melody event follows this path:

```text
NoteEvent(pitch=69, start=4, duration=1, velocity=90)
→ articulated routedSaw → pan 0.2
→ dry output + delay send + reverb send
→ wet delay + wet reverb → final stereo mix
```

Open `supercollider/chapter_25_space_and_effects.scd` for numbered dry, pan,
single-echo, feedback, dry/wet, room, shared-space, capstone, and cleanup blocks.
Try layer sends reversed, or let a tail overlap a section boundary: does the
composition boundary remain the same even though its rendering overlaps?

## Boundary

This is signal routing, not a mixing/mastering course. There is no chorus,
flanging, phasing, distortion, compression, normalization, live scheduling,
socket, UDP, or OSC implementation. Python and SuperCollider still meet through
files and a manually evaluated script. Real-time communication remains Chapter
26 work.
