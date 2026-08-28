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
