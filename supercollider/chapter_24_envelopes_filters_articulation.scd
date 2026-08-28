// Chapter 24 — evaluate numbered sections separately. No effects or OSC.
// 1. Boot and 2. load definitions.
s.boot;
(
~projectRoot = PathName(thisProcess.nowExecutingPath).pathOnly.dirname;
(~projectRoot +/+ "supercollider/synthdefs/basic_instruments.scd").load;
(~projectRoot +/+ "supercollider/synthdefs/articulated_instruments.scd").load;
~tempo = 120; ~secondsPerBeat = 60 / ~tempo;
~playGated = { |definition, freq=261.625565, beats=1, gateRatio=0.85, amp=0.06, args=#[]|
    var voice = Synth(definition, [\freq, freq, \amp, amp, \gate, 1] ++ args);
    SystemClock.sched(beats * gateRatio * ~secondsPerBeat, { voice.set(\gate, 0); nil });
};
~melody = [261.625565, 329.627557, 391.995436, 523.251131];
~playMelody = { |gateRatio=0.85, args=#[]| Routine({
    ~melody.do({ |freq| ~playGated.(\filteredSaw, freq, 1, gateRatio, 0.05, args); ~secondsPerBeat.wait; });
}).play; };
)

// 3. ADSR: same saw/pitch/amplitude/gate; only envelope changes.
~playGated.(\adsrSaw, args: [\attack, 0.005, \decay, 0.08, \sustainLevel, 0.25, \release, 0.05]); // short
~playGated.(\adsrSaw, args: [\attack, 0.05, \decay, 0.10, \sustainLevel, 0.85, \release, 0.30]); // sustained
~playGated.(\adsrSaw, args: [\attack, 0.50, \decay, 0.10, \sustainLevel, 0.85, \release, 0.50]); // slow_attack
// Awkward case: 0.25-second gate, 0.5-second attack; release can begin before the peak.
~playGated.(\adsrSaw, beats: 0.5, gateRatio: 1, args: [\attack, 0.5]);

// 4. Cutoff comparison: only 500, 1500, then 5000 Hz changes.
Routine({ [500, 1500, 5000].do({ |hz| ~playGated.(\filteredSaw, args: [\cutoff, hz, \rq, 0.7]); 0.8.wait; }); }).play;

// 5. RLPF rq is reciprocal Q: smaller rq is narrower/more resonant in this range.
Routine({ [0.9, 0.5, 0.2].do({ |rq| ~playGated.(\filteredSaw, args: [\cutoff, 1500, \rq, rq]); 0.8.wait; }); }).play;

// Fixed 1000-Hz cutoff across C2/C4/C6, then frequency-relative freq * 4.
Routine({ [65.406391, 261.625565, 1046.502261].do({ |f| ~playGated.(\filteredSaw, f, args: [\cutoff, 1000]); 0.8.wait; }); }).play;
Routine({ [65.406391, 261.625565, 1046.502261].do({ |f| ~playGated.(\filteredSaw, f, args: [\cutoffRatio, 4]); 0.8.wait; }); }).play;

// 6. Static versus moving filter; amplitude ADSR stays identical.
~playGated.(\filteredSaw, args: [\cutoff, 500]);
~playGated.(\filterEnvSaw, args: [\baseCutoff, 500, \filterAmount, 3000, \filterDecay, 0.25]);

// 7. Velocity 40/80/120: amplitude only, then amplitude plus bounded cutoff offset.
Routine({ [40, 80, 120].do({ |v| ~playGated.(\filterEnvSaw, amp: (v/127)*0.10, args: [\filterAmount, 0]); 0.8.wait; }); }).play;
Routine({ [40, 80, 120].do({ |v| ~playGated.(\filterEnvSaw, amp: (v/127)*0.10,
    args: [\filterAmount, 0, \velocityCutoff, (v/127)*1800]); 0.8.wait; }); }).play;
// Velocity-to-cutoff is a patch design choice, not a universal instrumental law.

// 8–9. Same melody/onsets/instrument/tempo; gate-off changes (release remains separate).
~playMelody.(0.4); ~playMelody.(0.95); // compare separately
~playMelody.(0.5); ~playMelody.(0.85); ~playMelody.(1.0); // short/normal/sustained
// Also compare low/medium/high static cutoff without editing melody notes.
~playMelody.(0.85, [\cutoff, 500]); ~playMelody.(0.85, [\cutoff, 1500]); ~playMelody.(0.85, [\cutoff, 5000]);

// 10. Capstone: same event JSON, articulated playback metadata selects each layer.
(
~events = JSON.parse(File.readAllString(~projectRoot +/+ "outputs/chapter_24_capstone_events.json"));
~config = JSON.parse(File.readAllString(~projectRoot +/+ "outputs/chapter_24_articulated_playback.json"));
~events.do({ |event| var preset = ~config[\layers][event[\layer]]; var definition;
    definition = if(preset[\instrument] == "filter_env_saw", { \filterEnvSaw }, { \filteredSaw });
    SystemClock.sched(event[\start] * ~secondsPerBeat, {
        ~playGated.(definition, event[\frequency], event[\duration], preset[\gate_ratio],
            (event[\velocity] / 127) * 0.08,
            [\baseCutoff, preset[\base_cutoff] ? 1000, \cutoff, preset[\base_cutoff] ? 1000,
             \rq, preset[\rq] ? 0.7, \velocityCutoff, (event[\velocity]/127) * (preset[\velocity_cutoff_range] ? 0)]); nil;
    });
});
)

// 11. Cleanup. Long releases leave voices active after gate-off; headroom comes first.
s.freeAll; CmdPeriod.run;
