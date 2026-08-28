"""Chapter 26 dry-run and opt-in live OSC demonstration."""
from __future__ import annotations
from .chapter22 import TEMPO_BPM
from .chapter25 import chapter_25_capstone
from .osc import OSC_HOST, OSC_PORT, OscNoteClient, PlaybackChoice, build_osc_schedule, execute_osc_schedule
from .pitch import pitch_to_name

PLAYBACK_BY_LAYER = {
    "melody": PlaybackChoice("pulse", 0.15),
    "harmony": PlaybackChoice("articulated_saw", -0.15),
    "bass": PlaybackChoice("sine", 0.0),
}

def chapter_26_schedule():
    events, layers = chapter_25_capstone()
    return events, layers, build_osc_schedule(events, layers, bpm=TEMPO_BPM,
                                               playback_by_layer=PLAYBACK_BY_LAYER)

def run_chapter_26(*, live: bool = False, host: str = OSC_HOST, port: int = OSC_PORT) -> None:
    events, layers, schedule = chapter_26_schedule()
    rows = []
    for event, layer in sorted(zip(events, layers, strict=True), key=lambda pair: pair[0].start):
        choice = PLAYBACK_BY_LAYER[layer]
        rows.append(f"{event.start:>4.1f}   {layer:<9} {pitch_to_name(event.pitch):<5} {choice.instrument}")
    print(f"""Chapter 26 — OSC: Sending Musical Events in Real Time

Python holds NoteEvents and decides WHEN; SuperCollider receives control data and decides HOW sound is made.
OSC is small control data (address + arguments), not audio samples.
Destination: {host}:{port} (localhost UDP application traffic to sclang, separate from sclang → scsynth)
Protocol: /ping []; /note [frequency, amplitude, duration_seconds, instrument, pan]; /panic []

Capstone schedule ({TEMPO_BPM:g} BPM, 16 beats):
time   layer     pitch instrument
{chr(10).join(rows)}
""")
    if not live:
        print("Dry run: would send /ping, then the /note onset groups above.\nUse --live to transmit; no network packets or audio were created.")
        return
    print("Make sure:\n1. SuperCollider is open.\n2. chapter_26_osc_receiver.scd has been evaluated.\n3. the audio server is running.\n\nSending OSC...")
    client = OscNoteClient(host, port)
    client.ping()
    execute_osc_schedule(schedule, client, verbose=True)
    print("Performance complete. Use /panic if sound lingers.")
