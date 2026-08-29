# Chapter 26 — OSC: Sending Musical Events in Real Time

> How can Python send compositional decisions directly to SuperCollider while the music is running?

## The first live bridge

Open Sound Control (OSC) is a message format commonly used for communication between music and media applications. A message has an **address**, which identifies its kind, and **arguments**, which carry its data. OSC is small control data—not audio samples. Python can request “play 440 Hz at this amplitude for this duration”; SuperCollider generates the waveform.

```text
Chapter 22:    Python → event file → reader → SuperCollider
Chapters 23–25: same bridge + richer synthesis
Chapter 26:    Python → OSC over UDP → SuperCollider now
```

UDP sends lightweight datagrams without a persistent connection. Every example targets `127.0.0.1:57121`: the loopback address means the same computer, and port 57121 avoids the usual scsynth server port. This application conversation is **Python → sclang**; sclang's separate internal OSC conversation with **scsynth** creates audio-server Synths.

```text
PYTHON NoteEvent
  ↓ pitch/velocity/beat conversion
OSC packet /note
  ↓ UDP localhost
sclang OSCdef
  ↓ Synth(\articulatedSaw)
scsynth
  ↓
speakers
```

## Tiny protocol

Argument order is a stable contract:

| Address | Arguments | Purpose |
|---|---|---|
| `/ping` | none | make receiver print confirmation |
| `/note` | `frequency, amplitude, duration_seconds, instrument, pan` | start one complete note now |
| `/panic` | none | free only Chapter 26 source synths |

Python converts pitch to positive frequency, maps velocity with Chapter 22's bounded `velocity / 127 * 0.15`, converts beat duration to seconds, and validates pan `-1…+1`. Instrument is one of `sine`, `saw`, `pulse`, or `articulated_saw`. SuperCollider independently validates the packet and performs an allowlisted dictionary lookup; it rejects malformed notes and unknown names rather than evaluating strings.

One `/note` starts immediately. `SystemClock.sched(duration)` later sets its gate to zero, and the envelope finishes its release and frees the Synth. Separate note-off packets are intentionally unnecessary. Notes with equal beat starts become one Python onset group; its packets are sent back-to-back and create polyphonic Synths. They are near-simultaneous, not literally simultaneous at the sample level. OSC bundles are a future option, not required here.

## Run it

1. Open and evaluate `supercollider/chapter_26_osc_receiver.scd`; wait for server boot and “receiver ready”.
2. Verify the CI-safe plan: `python -m composition_lab chapter-26`.
3. Transmit the 16-beat melody/harmony/bass capstone: `python -m composition_lab chapter-26 --live`.
4. Watch `/ping` and musical `/note` traces in both programs. Use `/panic` (the Python helper is `OscNoteClient.panic()`) or the script cleanup block if needed.

The default command sends nothing. Live mode never launches SuperCollider and a successful UDP send does **not** prove a receiver exists; a real readiness test needs a reply listener, deferred here. The schedule is pure data built from unchanged `NoteEvent`s and a layer playback map. Execution records `time.monotonic()`, sleeps toward each absolute target (`start beats → seconds`), sends a late group immediately, and does not drop it. This avoids accumulating sleep drift while remaining deliberately simple.

Experiments progress from `/ping`, A4, C4–E4–G4–C5, a same-onset C triad, velocity 40/80/120, sine/saw/pulse, pan −0.6/0/+0.6, I–IV–V–I, a mixed timeline, and the existing 16-beat capstone. Reuse Chapter 18, seeded Chapter 19, or Markov Chapter 20 events to show that OSC does not care how events were composed. Change only BPM (90/120/150), playback instrument, chord onset staggering, an invalid instrument, receiver availability, or panic behavior for controlled reader studies.

## Timing and scope

Real-time systems have latency from Python scheduling, the OS, UDP, sclang processing, audio-server buffers, and the interface. `time.sleep()` is not hard real-time. This chapter demonstrates live integration—not zero latency, sample accuracy, a DAW transport, distributed clocks, or a production sequencer. Packet receipt time is not audio onset time. Do not expose this unauthenticated synthesis-control port to untrusted networks.

The boundary remains: Python owns score, tempo, onset scheduling, and playback conversion; SuperCollider owns safe instrument lookup, synthesis, routing, and release. File exports remain valuable for reproducibility and debugging. Chapter 27 builds the complete-score engine on that boundary; Chapter 28 then contrasts it with online generation.

## Bridge forward

Live transport can trigger events but does not itself compose a whole piece. Chapter 27 assembles one complete symbolic score before sending it to any playback path.
