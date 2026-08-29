import json

from composition_lab.chapter31 import PLAYBACK_RICH, PLAYBACK_SIMPLE, write_development_artifacts
from composition_lab.classical_style import (SECTION_PLAN, adapt_for_vi,
    build_development_study, developed_phrase, fragment, source_motif)
from composition_lab.events import composition_duration
from composition_lab.motifs import (augment_motif, diminish_motif, invert_motif,
    retrograde_motif, sequence_motif)
from composition_lab.osc import build_osc_schedule


def test_source_and_transformations_are_exact():
    motif = source_motif()
    assert [(e.pitch, e.start, e.duration) for e in motif] == [
        (60, 0, .5), (62, .5, .5), (67, 1, .5), (64, 1.5, .5)]
    assert [e.pitch for e in sequence_motif(motif, (3,))] == [63, 65, 70, 67]
    assert fragment(motif) == motif[:2]
    assert [(e.start, e.duration) for e in augment_motif(motif)] == [(0, 1), (1, 1), (2, 1), (3, 1)]
    assert [(e.start, e.duration) for e in diminish_motif(motif)] == [(0, .25), (.25, .25), (.5, .25), (.75, .25)]
    assert [b.pitch - a.pitch for a, b in zip(invert_motif(motif, 60), invert_motif(motif, 60)[1:])] == [-2, -5, 3]
    assert [e.pitch for e in retrograde_motif(motif)] == [64, 67, 62, 60]


def test_phrase_expansion_and_harmonic_adaptation_are_explicit():
    motif = source_motif()
    assert composition_duration(developed_phrase(motif)) == 8
    assert composition_duration(developed_phrase(motif, True)) == 12
    adapted = adapt_for_vi(motif)
    assert [e.pitch for e in adapted] == [60, 62, 69, 64]
    assert [e.start for e in adapted] == [e.start for e in motif]
    assert [e.duration for e in adapted] == [e.duration for e in motif]


def test_form_return_and_provenance_have_no_orphans():
    study = build_development_study()
    assert tuple((s.name, s.start, s.end) for s in study.sections) == SECTION_PLAN
    assert composition_duration(study.events) == 64
    returned = [e for e, layer in zip(study.events, study.layers, strict=True)
                if layer == "motif" and 40 <= e.start < 42]
    assert [(e.pitch, e.start - 40, e.duration) for e in returned] == [
        (e.pitch, e.start, e.duration) for e in study.motif]
    labels = {m.label for m in study.materials} | {"cadence"}
    assert all(p.material_label in labels for p in study.provenance)
    assert all(p.source in {"source", "A"} for p in study.provenance)


def test_deterministic_artifacts_and_playback_independence(tmp_path):
    study = build_development_study()
    rich = build_osc_schedule(study.events, study.layers, bpm=study.bpm, playback_by_layer=PLAYBACK_RICH)
    simple = build_osc_schedule(study.events, study.layers, bpm=study.bpm, playback_by_layer=PLAYBACK_SIMPLE)
    assert [g.beat for g in rich] == [g.beat for g in simple]
    paths = write_development_artifacts(study, tmp_path)
    before = [p.read_bytes() for p in paths if p.suffix == ".json"]
    write_development_artifacts(study, tmp_path)
    assert before == [p.read_bytes() for p in paths if p.suffix == ".json"]
    manifest = json.loads(paths[1].read_text())
    assert manifest["seed"] is None and manifest["return_strategy"].startswith("literal A")
