// Chapter 24 instruments. Signal path: Saw -> RLPF -> amplitude envelope -> Pan2.
(
SynthDef(\adsrSaw, { |out = 0, freq = 440, amp = 0.08, gate = 1, pan = 0,
    attack = 0.01, decay = 0.10, sustainLevel = 0.7, release = 0.20|
    var envelope = EnvGen.kr(Env.adsr(attack.max(0.001), decay.max(0),
        sustainLevel.clip(0, 1), release.max(0.001)), gate, doneAction: 2);
    Out.ar(out, Pan2.ar(Saw.ar(freq) * envelope * amp.clip(0, 0.2), pan));
}).add;

SynthDef(\filteredSaw, { |out = 0, freq = 440, amp = 0.08, gate = 1, pan = 0,
    attack = 0.01, decay = 0.10, sustainLevel = 0.7, release = 0.20,
    cutoff = 1500, cutoffRatio = 0, rq = 0.7|
    var envelope = EnvGen.kr(Env.adsr(attack.max(0.001), decay.max(0),
        sustainLevel.clip(0, 1), release.max(0.001)), gate, doneAction: 2);
    // cutoffRatio 0 selects fixed cutoff; a positive ratio tracks note frequency.
    var selectedCutoff = Select.kr(cutoffRatio > 0, [cutoff, freq * cutoffRatio]).clip(20, 18000);
    var filtered = RLPF.ar(Saw.ar(freq), selectedCutoff, rq.clip(0.1, 1));
    Out.ar(out, Pan2.ar(filtered * envelope * amp.clip(0, 0.2), pan));
}).add;

SynthDef(\filterEnvSaw, { |out = 0, freq = 440, amp = 0.08, gate = 1, pan = 0,
    attack = 0.01, decay = 0.10, sustainLevel = 0.7, release = 0.20,
    baseCutoff = 500, filterAmount = 3000, filterAttack = 0.005,
    filterDecay = 0.25, velocityCutoff = 0, rq = 0.7|
    var amplitudeEnvelope = EnvGen.kr(Env.adsr(attack.max(0.001), decay.max(0),
        sustainLevel.clip(0, 1), release.max(0.001)), gate, doneAction: 2);
    var filterEnvelope = EnvGen.kr(Env.perc(filterAttack.max(0.001), filterDecay.max(0.001)), gate);
    var movingCutoff = (baseCutoff + velocityCutoff + (filterEnvelope * filterAmount)).clip(20, 18000);
    var filtered = RLPF.ar(Saw.ar(freq), movingCutoff, rq.clip(0.1, 1));
    Out.ar(out, Pan2.ar(filtered * amplitudeEnvelope * amp.clip(0, 0.2), pan));
}).add;
)
