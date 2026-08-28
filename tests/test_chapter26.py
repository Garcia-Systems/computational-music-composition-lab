import unittest
from composition_lab.events import NoteEvent
from composition_lab.osc import (NOTE_ADDRESS, PANIC_ADDRESS, OscNoteClient, PlaybackChoice,
                                 build_osc_schedule, note_event_to_osc_payload)

class FakeTransport:
    def __init__(self): self.sent=[]
    def send_message(self, address, arguments): self.sent.append((address, tuple(arguments)))

class Chapter26Tests(unittest.TestCase):
    def test_payload_reuses_pitch_velocity_time_and_pan(self):
        event=NoteEvent(69,0,1,90)
        payload=note_event_to_osc_payload(event,bpm=120,instrument="saw",pan=-0.5)
        self.assertAlmostEqual(payload[0],440)
        self.assertAlmostEqual(payload[1],0.15*90/127)
        self.assertEqual(payload[2:],(0.5,"saw",-0.5))
        self.assertEqual(event,NoteEvent(69,0,1,90))

    def test_simultaneous_and_sequential_groups(self):
        chord=[NoteEvent(p,0,1) for p in (60,64,67)]
        mapping={"music":PlaybackChoice("sine")}
        groups=build_osc_schedule(chord,["music"]*3,bpm=120,playback_by_layer=mapping)
        self.assertEqual((len(groups),len(groups[0].messages)),(1,3))
        seq=build_osc_schedule([NoteEvent(60,n,1) for n in range(3)],["music"]*3,
                               bpm=120,playback_by_layer=mapping)
        self.assertEqual(tuple(g.at_seconds for g in seq),(0,0.5,1.0))
        self.assertTrue(all(m.address==NOTE_ADDRESS for g in seq for m in g.messages))

    def test_client_helpers_use_injected_transport(self):
        fake=FakeTransport(); client=OscNoteClient(transport=fake)
        client.ping(); client.note((440,0.1,0.5,"sine",0)); client.panic()
        self.assertEqual(fake.sent[0],("/ping",()))
        self.assertEqual(fake.sent[-1],(PANIC_ADDRESS,()))

    def test_validation(self):
        with self.assertRaises(ValueError): PlaybackChoice("unknown")
        with self.assertRaises(ValueError): PlaybackChoice("sine",1.1)
        with self.assertRaises(ValueError): OscNoteClient(port=0,transport=FakeTransport())
        with self.assertRaises(ValueError): OscNoteClient(host="0.0.0.0",transport=FakeTransport())

    def test_receiver_contains_protocol_and_safe_dispatch(self):
        source=__import__("pathlib").Path("supercollider/chapter_26_osc_receiver.scd").read_text()
        for term in ("OSCdef", "'/ping'", "'/note'", "'/panic'", "Synth(",
                     "Dictionary", "SystemClock.sched"):
            self.assertIn(term,source)

if __name__ == "__main__": unittest.main()
