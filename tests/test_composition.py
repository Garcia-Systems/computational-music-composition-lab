import json
from dataclasses import replace
import pytest
from composition_lab.composition import (
    CompositionSpec, SectionSpec, compose, build_section_timeline,
    composition_osc_schedule, result_events_and_layers, validate_spec,
    write_composition_artifacts, DEFAULT_PLAYBACK,
)
from composition_lab.osc import PlaybackChoice


def test_spec_validation():
    validate_spec(CompositionSpec())
    with pytest.raises(ValueError, match="bpm"):
        validate_spec(CompositionSpec(bpm=0))
    with pytest.raises(ValueError, match="unsupported"):
        validate_spec(CompositionSpec(mode="dorian"))
    with pytest.raises(ValueError, match="empty"):
        validate_spec(CompositionSpec(sections=()))
    bad = SectionSpec("A", 0, (1,), "generate", ("melody",))
    with pytest.raises(ValueError, match="positive"):
        validate_spec(CompositionSpec(sections=(bad,)))


def test_form_reproducibility_layers_duration_and_transformations():
    one = compose(CompositionSpec())
    two = compose(CompositionSpec())
    assert one == two
    assert [(s.label, s.start, s.end) for s in one.sections] == [
        ("A", 0, 8), ("A'", 8, 16), ("B", 16, 24), ("A", 24, 32)]
    assert {layer.name for layer in one.layers} == {"melody", "harmony", "bass", "groove"}
    assert one.duration == 32
    melody = one.layer("melody").events
    assert tuple(e.pitch for e in melody[8:16]) == tuple(e.pitch + 12 for e in melody[:8])
    assert tuple(e.pitch for e in melody[24:32]) == tuple(e.pitch for e in melody[:8])
    assert tuple(e.start - 24 for e in melody[24:32]) == tuple(e.start for e in melody[:8])


def test_harmony_bass_and_transposition_are_symbolic():
    c = compose(CompositionSpec(tonic=60))
    f = compose(CompositionSpec(tonic=65, pitch_range=(65, 89)))
    assert tuple(h.degree for h in c.harmony) == tuple(h.degree for h in f.harmony)
    assert tuple(h.start for h in c.harmony) == tuple(h.start for h in f.harmony)
    assert all((b.pitch - a.pitch) % 12 == 5 for a, b in zip(c.layer("melody").events, f.layer("melody").events))
    bass = c.layer("bass").events
    for span, root_event in zip(c.harmony, bass[::2], strict=True):
        assert root_event.pitch % 12 == span.pitches[0] % 12


def test_playback_maps_do_not_change_composition_and_schedule_timing():
    result = compose(CompositionSpec())
    before = result
    centered = {name: PlaybackChoice("sine", 0) for name in DEFAULT_PLAYBACK}
    schedule_a = composition_osc_schedule(result)
    schedule_b = composition_osc_schedule(result, centered, bpm=120)
    assert result == before
    assert schedule_a[0].at_seconds == schedule_b[0].at_seconds == 0
    assert next(g for g in schedule_b if g.beat == 1).at_seconds == .5
    events, layers = result_events_and_layers(result)
    assert sum(len(g.messages) for g in schedule_a) == len(events) == len(layers)


def test_deterministic_json_artifacts(tmp_path):
    result = compose(CompositionSpec())
    first = write_composition_artifacts(result, tmp_path)
    content = first[0].read_bytes()
    write_composition_artifacts(result, tmp_path)
    assert first[0].read_bytes() == content
    data = json.loads(content)
    assert data["specification"]["seed"] == 2026
    assert [layer["name"] for layer in data["layers"]] == ["melody", "harmony", "bass", "groove"]
    assert all(path.exists() for path in first)
