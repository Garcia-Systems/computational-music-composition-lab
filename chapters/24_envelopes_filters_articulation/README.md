# Chapter 24 — Envelopes, Filters, and Articulation

> How can the shape of a sound over time and frequency make the same oscillator
> behave like very different musical instruments?

```text
OSCILLATOR → AMPLITUDE ENVELOPE → FILTER / FILTER ENVELOPE
→ ARTICULATION → INSTRUMENT BEHAVIOR
```

The laboratory deliberately uses Chapter 23's spectrally rich `Saw` throughout.
Pitch, notes, and waveform can remain fixed while time shape and spectrum change.
This demonstrates instrument *behavior*, not accurate guitar, piano, or string
emulation.

## Amplitude over time

An ADSR envelope has four practical stages. **Attack** moves from silence to the
peak; **decay** moves from the peak to the **sustain level**; sustain level is
held while the gate remains open; **release** moves toward silence after gate-off.
The parameter is consequently named `sustainLevel`, rather than the ambiguous
`sustain`.

Musical duration and envelope timing are different quantities:

```text
NoteEvent duration: beats on the composition timeline
attack / decay / release: seconds belonging to an instrument
```

A two-beat note at 120 BPM has a nominal duration of one second, but may still
have a 0.01-second attack and 0.20-second release. `Env.adsr` and `EnvGen` receive
`gate = 1`, hold the sustain stage, then receive `gate = 0`. Release begins and
`doneAction: 2` frees the Synth only when release completes. Gate-off therefore
does not mean instant silence. Long tails also mean more simultaneous Synths and
greater summed level, so examples use conservative voice gain instead of hiding
gain problems behind a limiter.

The `\adsrSaw` experiments compare neutral `short`, `sustained`, and
`slow_attack` settings. Try attacks 0.005, 0.05, and 0.5 seconds; releases 0.05,
0.3, and 1.5 seconds; and sustain levels 0.2, 0.6, and 1.0. A deliberately awkward
0.25-second gate with a 0.5-second attack may enter release before reaching its
intended peak: instrument settings must fit musical context.

## Spectrum over time

The consistent path is:

```text
Saw oscillator → RLPF → amplitude envelope → Pan2 → output
```

A low-pass filter passes frequencies below its cutoff more readily and reduces
higher regions. In `\filteredSaw`, compare cutoff 500, 1500, and 5000 Hz while
pitch, waveform, amplitude envelope, amplitude, duration, and `rq` remain fixed.
Cutoff is clamped to 20–18000 Hz in the SynthDef; educational playback presets
require a positive value.

`RLPF`'s `rq` is reciprocal Q, not a universal resonance-amount dial. Within the
practical 0.1–1.0 range used here, **smaller `rq` means narrower, more resonant
behavior** around cutoff. Compare 0.9, 0.5, and 0.2 and listen to how emphasis at
the cutoff region changes.

A fixed 1000-Hz cutoff does not have the same relationship to C2, C4, and C6.
The key-tracking demonstration instead computes `freq * cutoffRatio`, trying a
ratio of 4 and clamping the result. This is only a comparison, not a keyboard
tracking curve or modulation matrix.

`\filterEnvSaw` keeps two controls separate:

```text
AMPLITUDE ENVELOPE → level
FILTER ENVELOPE    → spectral filtering

moving cutoff = baseCutoff + (filterEnvelope * filterAmount)
```

The filter envelope is a short `Env.perc`, so a 500-Hz base plus 3000-Hz amount
begins relatively open and decays toward the base. Static and moving versions
use identical amplitude ADSRs. A `short_bright_decay` setting combines fast
amplitude attack with this closing filter. A `pad_like` setting may use slow
attack, high sustain, longer release, and moderate cutoff—but it is only a
simple sustained synthesizer texture, not a production pad.

## Articulation is playback behavior

Articulation describes how an event is shaped and separated from surrounding
events. Onset, gate-off/offset, and the next onset are separate variables. This
chapter computes:

```text
gate duration in beats = NoteEvent.duration * gate_ratio
```

`short=0.50`, `normal=0.85`, and `sustained=1.00`; validation requires
`0 < gate_ratio <= 1`. At 120 BPM, a one-beat short event gates for 0.5 beats,
or 0.25 seconds. The scheduler knows beat time and sends gate-off; the SynthDef
knows how its seconds-based release responds. Release can extend beyond nominal
duration. Changing ratio changes offsets and note separation, never the onset
grid or `NoteEvent.duration`. Overlap can arise from release tails, but true
legato, voice stealing, portamento, and invisible ratios above one are not built.

Run:

```bash
python -m composition_lab chapter-24
```

Python prints an articulation/seconds inspector and creates:

```text
outputs/chapter_24_capstone_events.json
outputs/chapter_24_basic_playback.json
outputs/chapter_24_articulated_playback.json
```

The first file is the unchanged eight-beat I–IV–V–I music—pitch, start,
duration, velocity, and melody/harmony/bass layer. Both playback documents refer
to that same music. Basic playback uses Chapter 23-style saw behavior; articulated
playback gives melody a short velocity-sensitive moving filter, harmony a slow
sustained shape, and bass a moderate gate with lower cutoff. Synthesis parameters
are layer metadata, not duplicated in each note, while velocity correctly remains
per-note event data.

Velocity first maps explicitly to `velocity / 127`, then to conservative voice
amplitude. A second controlled experiment adds a bounded cutoff offset. Higher
velocity opening the filter is a synthesizer design choice, not a universal law.
Compare velocities 30, 80, and 120 with amplitude-only and amplitude-plus-filter
response.

## Listening studies

Open `supercollider/chapter_24_envelopes_filters_articulation.scd` after running
the Python command. Its numbered blocks cover: ADSR; short versus sustained
melody; cutoff; RQ; fixed versus frequency-relative cutoff; static versus moving
filter; velocity-to-amplitude; velocity-to-amplitude-plus-cutoff; three gate
ratios; and the capstone. Try gate ratios 0.25, 0.5, 0.9, and 1.0 without changing
onsets. Swap short melody, sustained harmony, and normal bass settings. Does
separation help clarify roles? Then try slow attacks on short notes or long
releases on dense chords and observe why sound design depends on context.

## Boundary

The architecture remains:

```text
NoteEvent (pitch/start/duration/velocity)
→ playback configuration (instrument/gate/envelope/filter)
→ SynthDef (oscillator/filter/envelopes)
→ sound
```

No harmony, melody, or form moved into SuperCollider. There is no preset manager,
automatic articulation inference, audio-server requirement for Python, OSC,
effects, reverb, delay, effect buses, spatial processing, or Chapter 25 work.

```text
SAME OSCILLATOR + DIFFERENT ENVELOPE + DIFFERENT FILTER
+ DIFFERENT ARTICULATION = VERY DIFFERENT INSTRUMENT BEHAVIOR
```

The composition itself may remain unchanged.
