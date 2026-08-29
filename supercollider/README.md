# SuperCollider: Chapter 22

SuperCollider adds a dedicated real-time synthesis path without replacing the
book's transparent Python WAV renderer. **`sclang`** is the language/interpreter
that sends instructions; **`scsynth`** is the audio server that produces audio.
They are separate processes: synth definitions and running synth instances
ultimately execute on the server.

Install SuperCollider using the official installer appropriate for your system,
then open `chapter_22_first_sound.scd` in its IDE. Evaluate `s.boot;`, wait until
the default server is ready, and evaluate selected parenthesized blocks with the
IDE's evaluate-selection shortcut. The script is intentionally interactive;
Python never launches it and the Python test suite needs no audio server.

For safety, `s.freeAll;` frees synths on the server. The IDE's standard emergency
stop (usually Cmd-. or Ctrl-.) runs `CmdPeriod.run;`. Individual gate-based notes
release with `voice.set(\gate, 0)` and free themselves after their envelope.

Run `python -m composition_lab chapter-22` from the repository root first. It
writes inspectable JSON and reference WAV files under `outputs/`. JSON retains
beat-based `start` and `duration`; the script uses a 120 BPM `TempoClock`, groups
equal starts, waits onset deltas, starts every voice in a group together, and
schedules each gate release independently. Velocity is mapped to
`(velocity / 127) * 0.15`; velocity is performance intensity, not acoustic
loudness, and the small multiplier leaves headroom when voices overlap.

```text
NoteEvent.pitch
    ↓ Python pitch_to_frequency()
event JSON (pitch, frequency, start, duration, velocity)
    ↓ SuperCollider reads frequency and maps velocity
SinOsc.ar(freq) → EnvGen → Pan2 → scsynth → speakers
```

Chapter 0 calculated every sample in Python. Chapter 22 instead describes a
synthesis graph and lets `scsynth` calculate samples. Both initially use sine
waves so the controlled comparison changes the rendering architecture—not the
composition or sound-design ambition.

## Chapter 24: envelopes, filters, and articulation

Run `python -m composition_lab chapter-24`, then open
`chapter_24_envelopes_filters_articulation.scd`. It loads the separate
`synthdefs/articulated_instruments.scd` library and provides numbered ADSR,
cutoff, RQ, key-tracking, filter-envelope, velocity, articulation, and capstone
comparisons. `gate_ratio` remains playback metadata: the scheduler converts its
beat duration to seconds and sends `gate = 0`; each gate-aware `EnvGen` completes
its own release and frees its Synth. `RLPF` uses reciprocal-Q `rq`, so smaller
values are narrower/more resonant within the documented safe range. The Python
command neither installs nor launches SuperCollider.


## Chapter 26: localhost OSC receiver

1. Open `chapter_26_osc_receiver.scd`; evaluate its boot/definition block and wait for readiness.
2. It opens sclang UDP port `57121` on localhost, loads four gate-aware SynthDefs, installs allowlisted instrument dispatch, and registers predictable `/ping`, `/note`, and `/panic` OSCdefs.
3. Run `python -m composition_lab chapter-26 --live`. Python does not launch SuperCollider.
4. `/note` starts immediately; `SystemClock.sched` releases its gate after the transmitted duration. Same-onset packets create separate polyphonic Synths.
5. Send `/panic` through `OscNoteClient.panic()`, or evaluate the documented cleanup block / `s.freeAll` if needed. Cleanup frees all three OSCdefs to prevent duplicate handlers.

This is unauthenticated localhost teaching infrastructure. UDP send success is not receiver readiness, and ordinary language scheduling is not sample-accurate.

## Chapter map and safe workflow

- Chapter 22: `chapter_22_first_sound.scd` introduces the language/server split and a sine voice.
- Chapter 23: `chapter_23_synthesizers_as_instruments.scd` changes oscillator structure while score events stay fixed.
- Chapter 24: `chapter_24_envelopes_filters_articulation.scd` adds ADSR **levels and times**, filtering, and gate-based articulation. ADSR sustain is a level, not a duration; smaller `RLPF.rq` values produce a narrower, more resonant response.
- Chapter 25: `chapter_25_space_and_effects.scd` adds pan (`-1` left, `0` center, `+1` right), bounded delay feedback, reverb, buses, and send/return routing.
- Chapter 26: `chapter_26_osc_receiver.scd` receives localhost control messages. OSC carries event controls, never audio samples.

For every file: boot `s`, wait for the server, evaluate SynthDefs before examples, keep gains conservative, and use `s.freeAll;` or the IDE emergency stop to silence the server. The Python chapter command always remains the non-live starting point.
