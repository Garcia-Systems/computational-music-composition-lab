// Chapter 26 — localhost Python -> sclang OSC -> scsynth.
// Evaluate this file first. Language port 57121 avoids the default server port 57110.
(
// 1. Boot and define the four deliberately small, gate-aware instruments.
s.options.bindAddress = "127.0.0.1";
thisProcess.openUDPPort(57121);
s.waitForBoot {
    SynthDef(\oscSine, { |freq=440, amp=0.08, gate=1, pan=0|
        var env = EnvGen.kr(Env.adsr(0.01, 0.08, 0.75, 0.2), gate, doneAction: 2);
        Out.ar(0, Pan2.ar(SinOsc.ar(freq) * env * amp.clip(0, 0.15), pan.clip(-1, 1)));
    }).add;
    SynthDef(\oscSaw, { |freq=440, amp=0.08, gate=1, pan=0|
        var env = EnvGen.kr(Env.adsr(0.01, 0.08, 0.65, 0.25), gate, doneAction: 2);
        Out.ar(0, Pan2.ar(LPF.ar(Saw.ar(freq), 2200) * env * amp.clip(0, 0.15), pan.clip(-1, 1)));
    }).add;
    SynthDef(\oscPulse, { |freq=440, amp=0.08, gate=1, pan=0|
        var env = EnvGen.kr(Env.adsr(0.005, 0.06, 0.6, 0.18), gate, doneAction: 2);
        Out.ar(0, Pan2.ar(LPF.ar(Pulse.ar(freq, 0.4), 1800) * env * amp.clip(0, 0.15), pan.clip(-1, 1)));
    }).add;
    SynthDef(\articulatedSaw, { |freq=440, amp=0.08, gate=1, pan=0|
        var env = EnvGen.kr(Env.adsr(0.02, 0.12, 0.6, 0.35), gate, doneAction: 2);
        Out.ar(0, Pan2.ar(RLPF.ar(Saw.ar(freq), 1600, 0.7) * env * amp.clip(0, 0.15), pan.clip(-1, 1)));
    }).add;
    s.sync;

    // 2. Strings select only this allowlist: no OSC argument is evaluated as code.
    ~pythonInstruments = Dictionary[
        "sine" -> \oscSine, "saw" -> \oscSaw, "pulse" -> \oscPulse,
        "articulated_saw" -> \articulatedSaw
    ];
    ~pythonVoices = IdentitySet.new;

    // 3. Predictable names replace old handlers when this block is reevaluated.
    OSCdef(\pythonPing).free; OSCdef(\pythonNote).free; OSCdef(\pythonPanic).free;
    OSCdef(\pythonPing, { |msg, time, addr, recvPort|
        ("Python /ping received from " ++ addr.ip ++ ":" ++ addr.port).postln;
    }, '/ping', recvPort: 57121);

    OSCdef(\pythonNote, { |msg|
        var freq, amp, duration, instrument, pan, synthName, voice;
        if(msg.size < 6) { "Rejected /note: expected five arguments".warn } {
            freq=msg[1]; amp=msg[2]; duration=msg[3]; instrument=msg[4].asString; pan=msg[5];
            synthName=~pythonInstruments[instrument];
            if(synthName.isNil) { ("Rejected /note: unknown instrument " ++ instrument).warn } {
                if((freq <= 0) or: { duration <= 0 } or: { amp < 0 } or: { amp > 0.15 } or: { pan < -1 } or: { pan > 1 }) {
                    "Rejected /note: invalid frequency, amplitude, duration, or pan".warn
                } {
                    ("Received /note freq=" ++ freq ++ " amp=" ++ amp ++ " duration=" ++ duration ++ " instrument=" ++ instrument ++ " pan=" ++ pan).postln;
                    voice=Synth(synthName, [\freq, freq, \amp, amp, \gate, 1, \pan, pan]);
                    ~pythonVoices.add(voice);
                    SystemClock.sched(duration, { voice.set(\gate, 0); ~pythonVoices.remove(voice); nil });
                }
            }
        }
    }, '/note', recvPort: 57121);

    OSCdef(\pythonPanic, {
        "Python /panic: freeing Chapter 26 source synths".postln;
        ~pythonVoices.do(_.free); ~pythonVoices.clear;
    }, '/panic', recvPort: 57121);
    "Chapter 26 receiver ready on 127.0.0.1:57121".postln;
};
)

// Run: python -m composition_lab chapter-26 --live
// Cleanup (also prevents duplicate handlers):
// OSCdef(\pythonPing).free; OSCdef(\pythonNote).free; OSCdef(\pythonPanic).free;
// ~pythonVoices.do(_.free); ~pythonVoices.clear;
