import json
import wave

from composition_lab.chapter33 import DecisionCategory
from composition_lab.chapter34 import (
    FORM, RECORDED_A_PRIME_SELECTION, RECORDED_B_SELECTION, REVISION_ID,
    SECTION_DURATIONS, SOURCE_MOTIF, build_complete_piece, composition_brief,
    write_artifacts,
)
from composition_lab.events import composition_duration


def test_brief_form_motif_and_reproducibility():
    first, second = build_complete_piece(), build_complete_piece()
    assert composition_brief() == composition_brief()
    assert tuple(s.id for s in first.sections) == FORM
    assert tuple(s.duration for s in first.sections) == SECTION_DURATIONS
    assert SOURCE_MOTIF[1].pitch == 64
    assert first == second
    assert composition_duration(first.flattened()[0]) == sum(SECTION_DURATIONS)


def test_candidates_revision_provenance_and_boundaries():
    piece = build_complete_piece()
    assert RECORDED_A_PRIME_SELECTION in {c.id for c in piece.a_prime_candidates}
    assert RECORDED_B_SELECTION in {c.id for c in piece.b_candidates}
    assert all(all(c.constraints.values()) for c in piece.b_candidates)
    assert len(piece.a_prime_candidates) == 3 and len(piece.b_candidates) == 6
    b = next(s for s in piece.sections if s.id == "b")
    assert b.layers["melody"][-1].start == b.start + 22
    assert b.layers["melody"][-1].duration == 2
    assert all(p["source_material"] for p in piece.provenance)
    assert {d.category for d in piece.ledger} <= set(DecisionCategory)
    assert any(d.id == REVISION_ID for d in piece.ledger)
    for section in piece.sections:
        assert all(section.start <= event.start and event.start + event.duration <= section.start + section.duration
                   for events in section.layers.values() for event in events)


def test_alternate_selection_does_not_regenerate_pool_and_playback_is_independent():
    main = build_complete_piece()
    alternate = build_complete_piece(a_prime_selection="a-prime-candidate-01",
                                     b_selection="b-candidate-01")
    assert main.a_prime_candidates == alternate.a_prime_candidates
    assert main.b_candidates == alternate.b_candidates
    # The symbolic builder has no playback-map argument or dependency.
    assert "playback" not in main.brief


def test_artifacts_and_reference_wav(tmp_path):
    paths = write_artifacts(build_complete_piece(), tmp_path)
    assert all(path.exists() and path.stat().st_size for path in paths)
    score = json.loads((tmp_path / "chapter_34_complete_piece.json").read_text())
    assert [section["id"] for section in score["sections"]] == list(FORM)
    assert all("layers" in section for section in score["sections"])
    with wave.open(str(tmp_path / "chapter_34_complete_piece_reference.wav")) as wav:
        assert wav.getnframes() > 0 and wav.getframerate() == 8000
