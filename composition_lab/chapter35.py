"""Chapter 35: an evidence-based audit of the canonical Chapter 34 score."""
from __future__ import annotations
from collections import Counter
from dataclasses import asdict
import json
from pathlib import Path

from .chapter34 import (EFFECTS, FORM, MASTER_SEED, PLAYBACK,
    RECORDED_A_PRIME_SELECTION, RECORDED_B_SELECTION, REVISION_ID, SOURCE_MOTIF,
    TITLE, CompletePiece, build_complete_piece)

DECISION_CATEGORIES = {"human", "algorithm", "human_selected_algorithm_candidate", "derived"}
MATERIAL_CATEGORIES = {"human-authored", "algorithm-generated", "algorithm-transformed",
                       "mechanically-derived", "human-revised"}

def _event(e): return asdict(e)
def _score(piece):
    return {s.id:{k:[_event(e) for e in v] for k,v in s.layers.items()} for s in piece.sections}

def build_authorship_audit(piece: CompletePiece | None = None) -> dict:
    """Reconstruct and inspect Chapter 34; never create or mutate a new score."""
    piece = piece or build_complete_piece()
    original = _score(piece)
    ap_ids=[c.id for c in piece.a_prime_candidates]; b_ids=[c.id for c in piece.b_candidates]
    raw=next(c for c in piece.b_candidates if c.id==RECORDED_B_SELECTION)
    b=next(s for s in piece.sections if s.id=="b")
    changes=[]
    for i,(old,new) in enumerate(zip(piece.b_before_revision,b.layers["melody"],strict=True)):
        after=_event(new); after["start"]-=b.start
        if _event(old)!=after:
            changes.append({"event_index":i,"before":_event(old),"after":after,
              "requested_by":"human","revision_id":REVISION_ID,
              "changed_properties":[k for k,v in _event(old).items() if after[k]!=v]})
    alt_id=next(x for x in b_ids if x!=RECORDED_B_SELECTION)
    alt=build_complete_piece(b_selection=alt_id)
    changed_sections=[x for x in FORM if _score(piece)[x]!=_score(alt)[x]]
    section_classes={
      "intro":"human-authored motif fragment + mechanically-derived bass",
      "a":"human-authored theme + mechanically-derived accompaniment",
      "a_prime":"algorithm-transformed motif + human selection + derived accompaniment",
      "b":"algorithm-generated melody + human selection + human revision",
      "development":"algorithm-transformed units from the human-authored motif",
      "a_return":"human-directed return + algorithm-transformed register + derived arrangement",
      "coda":"human-directed closure + algorithm-transformed augmented fragment"}
    contributions=[
      ("Form","brief / ledger","human-authored","human"),("A motif","motif-a","human-authored","human"),
      ("A' variation","motif-a","algorithm-transformed","algorithm proposed; human selected"),
      ("B candidates","seeded constrained random walk","algorithm-generated exact pitches and rhythms","algorithm proposed"),
      ("B selection",RECORDED_B_SELECTION,"human-selected","human"),("B revision",REVISION_ID,"human-revised","human"),
      ("Development","motif-a","algorithm-transformed","human-designed process"),
      ("Harmony / voicing","harmonic plan + chord table","human-authored plan; mechanically-derived pitches","human"),
      ("Bass","roots_and_fifths","human strategy; mechanically-derived placement","human"),
      ("Groove","quarter pulse/backbeat","human recipe; mechanically-derived placement","human"),
      ("Arrangement","texture plan","human-arranged","human"),("Playback","playback map","human-selected / performed","human configuration"),
      ("Audio rendering","final NoteEvents","synthesized / machine-rendered","finalized score")]
    claims=[
      "The human authored the brief, form, tonal framework, source motif, constraints, harmonic and arrangement plans, selections, revision, and stopping decision.",
      "The algorithm generated the exact pitch and rhythm sequences in the B candidate pool; the selected candidate became B's basis.",
      "The algorithm executed deterministic motif transformations, distinct from authoring their source motif.",
      "The human selected one A' transformation and one B candidate, then revised the selected B ending.",
      "Bass, groove, chord pitches, placement, frequency conversion, and OSC payloads largely follow chosen rules mechanically.",
      "Rendering and SuperCollider synthesis create audio signals; OSC transports instructions; none chose the form.",
      "The evidence supports neither an entirely human-written score nor an autonomously computer-composed piece."]
    audit={
      "composition_title":piece.brief["title"],
      "canonical_identity":{"chapter":34,"master_seed":piece.brief["master_seed"],"form":list(FORM),
        "selected_a_prime":RECORDED_A_PRIME_SELECTION,"selected_b":RECORDED_B_SELECTION},
      "audited_artifact_ids":["chapter_34_brief","chapter_34_manifest","chapter_34_candidates","chapter_34_decision_ledger","chapter_34_provenance","chapter_34_complete_piece","chapter_34_osc_schedule"],
      "definitions":{"generated":"algorithm chooses among multiple musically possible symbolic outcomes",
        "transformed":"an existing source is changed by an explicit operation",
        "derived":"a result follows mechanically from a chosen representation or rule",
        "selected":"an actor chooses among existing alternatives","revised":"an actor deliberately edits a selected result",
        "arranged":"existing material is distributed across layers, registers, entrances, and textures",
        "synthesized":"an audio signal is created to realize symbolic events","performed":"events are executed through time"},
      "valid_decision_categories":sorted(DECISION_CATEGORIES),"valid_material_classifications":sorted(MATERIAL_CATEGORIES),
      "decision_counts":dict(sorted(Counter(d.category.value for d in piece.ledger).items())),
      "decision_count_warning":"Counts do not indicate creative importance.",
      "decisions":[asdict(d)|{"category":d.category.value} for d in piece.ledger],
      "source_motif":{"id":"motif-a","events":[_event(e) for e in SOURCE_MOTIF],"provenance":"human-authored",
        "transformations":["fragmentation","rhythmic variation","sequence","diminution","inversion","transposition","augmentation"]},
      "section_authorship_map":section_classes,
      "section_audits":[{"id":s.id,"start":s.start,"duration":s.duration,"source_material":s.material_id,
          "layers":list(s.layers),"classification":section_classes[s.id]} for s in piece.sections],
      "layer_authorship_map":{"melody":["human-authored","algorithm-generated","algorithm-transformed","human-revised"],
        "harmony":["human-authored progression","mechanically-derived fixed voicing"],
        "bass":["human-authored strategy","mechanically-derived events"],"groove":["human-authored recipe","mechanically-derived events"],
        "texture":["human-arranged","mechanically executed"],"playback":["human-selected configuration","machine-rendered"]},
      "voice_leading_classification":"No inversion search occurs in Chapter 34; human-authored degrees index a fixed chord table, so exact voicing pitches are mechanically derived.",
      "candidate_generation":{"generator":raw.transformation,"master_seed":MASTER_SEED,"candidate_seeds":{c.id:c.seed for c in piece.b_candidates},
        "constraints":{"scale":"C major","pitch_range":[60,72],"maximum_leap":7,"duration_beats":24,
          "rhythm_vocabulary":[.5,1,1.5],"ending":"C-major triad; canonical candidates end C4"},
        "attempts":piece.trace["attempts"],"valid":piece.trace["valid_candidates"],"preserved":len(b_ids),
        "failure_reasons":piece.trace["rejection_reasons"],"selected":RECORDED_B_SELECTION},
      "selected_b_raw_events":[_event(e) for e in raw.events],"revision_records":changes,
      "rejected_material":{"a_prime":{"generated":len(ap_ids),"selected":RECORDED_A_PRIME_SELECTION,"rejected":[x for x in ap_ids if x!=RECORDED_A_PRIME_SELECTION]},
        "b":{"generated":len(b_ids),"selected":RECORDED_B_SELECTION,"rejected":[x for x in b_ids if x!=RECORDED_B_SELECTION]},"revision_alternatives":[]},
      "randomness":{"stochastic":["B initial pitch, next pitches, and durations"],"master_seed":MASTER_SEED,
        "deterministic":["A' transformations","fragmentation","sequence","diminution","inversion","octave transposition","augmentation","section positioning","harmony, bass, groove, and OSC placement"],
        "note":"A seed reproduces a path through an algorithm. It does not explain the musical rules that made the path possible."},
      "contribution_records":[{"component":a,"source":b,"action":c,"final_authority":d} for a,b,c,d in contributions],
      "lineages":{"transformation":["motif-a [human]","├── a-prime-candidate-02 [rhythmic transformation; human selected]","├── motif-a-development [fragmentation, sequence, diminution + inversion]","├── motif-a-return [octave transposition]","└── motif-a-augmented-fragment [fragmentation + augmentation]"],
        "generation":["B constrained-random-walk generator"]+[f"{'└──' if x==b_ids[-1] else '├──'} {x} [{'human selected → '+REVISION_ID if x==RECORDED_B_SELECTION else 'rejected'}]" for x in b_ids],
        "sound":["final NoteEvents","↓ playback configuration","↓ OSC messages / Python renderer","↓ SuperCollider SynthDefs","↓ audio samples"]},
      "counterfactuals":{"alternate_b_selection":{"candidate_id":alt_id,"changed_sections":changed_sections,"unchanged_sections":[x for x in FORM if x not in changed_sections],"candidate_pool_unchanged":piece.b_candidates==alt.b_candidates},
        "without_revision":{"changed_section":"b","differences":changes,"restores_selected_candidate_exactly":piece.b_before_revision==raw.events},
        "alternate_playback":{"symbolic_score_unchanged":True,"canonical":{k:asdict(v)|{"effect":EFFECTS[k]} for k,v in PLAYBACK.items()},"change":"reverse melody pan analytically; do not rebuild events"}},
      "composition_vs_sound":{"composition":["pitch","rhythm","harmony","form","motif","bass","texture"],"playback_sound":["instrument","oscillator","envelope","filter","pan","reverb","OSC transport"]},
      "final_claims":claims,
      "limitations":["Provenance only captures recorded decisions; informal reasons and preferences can be absent.","The model covers pitch, time, duration, velocity, layers, harmony, and playback metadata—not embodied gesture, microtiming, cultural meaning, or listener experience.","No structural metric establishes beauty, originality, emotional power, meaning, or artistic success; neither metrics nor provenance replaces listening."]}
    assert original==_score(piece)
    return audit

def render_authorship_report(a):
    cg=a["candidate_generation"]; rej=a["rejected_material"]; cf=a["counterfactuals"]
    out=[f"# Chapter 35 Authorship Report: {a['composition_title']}","","## Composition","This audits the canonical Chapter 34 score and creates no new composition.","","## Audit basis","The Chapter 34 pure builder reconstructs the brief, manifest data, candidates, ledger, provenance, score, playback, and OSC evidence.","","## Human-authored decisions","The human authored the goal, form, C-major framework, motif, constraints, harmony, arrangement, selections, revision, and stopping point.","","## Algorithm-generated material",f"The seeded constrained random walk preserved {cg['preserved']} valid B candidates and chose their exact pitches and rhythms inside a human-designed possibility space.","","## Algorithmic transformations","A', Development, return, and coda use explicit transformations of motif-a. Transformation is not generation of the source.","","## Derived material","Fixed chord pitches, bass/groove placement, section positioning, frequency/time conversion, velocity mapping, and OSC payloads follow selected representations or rules.","","## Human selections",f"The recorded choices are `{RECORDED_A_PRIME_SELECTION}` and `{RECORDED_B_SELECTION}`. Generation is not selection; generated is not used.","","## Human revisions",f"`{REVISION_ID}` changes exactly {len(a['revision_records'])} event; this is not a complete human rewrite."]
    for x in a["revision_records"]: out += [f"- Event {x['event_index']}: `{x['before']}` → `{x['after']}`; properties: {', '.join(x['changed_properties'])}."]
    out += ["","## Rejected alternatives",f"A': {', '.join(rej['a_prime']['rejected'])}. B: {', '.join(rej['b']['rejected'])}. They evidence exploration, not score inclusion.","","## Section-by-section audit"]
    out += [f"- **{s['id']}** — {s['duration']:g} beats; `{s['source_material']}`; {s['classification']}; layers: {', '.join(s['layers'])}." for s in a["section_audits"]]
    out += ["","## Arrangement decisions","The human chose layer entrances/exits, density, register, bass strategy, and groove recipe; code instantiated events.","","## Contribution ledger","| Component | Source | Action | Final authority |","|---|---|---|---|"]
    out += [f"| {r['component']} | {r['source']} | {r['action']} | {r['final_authority']} |" for r in a["contribution_records"]]
    out += ["","## Playback / synthesis","Python renders finalized events into samples. SuperCollider generates audio-rate samples. OSC carries instructions, not waveforms. None thereby chooses the symbolic form.","","COMPOSITION → PERFORMANCE → SOUND","","AUTHORSHIP / PROVENANCE asks who or what made each stage's decisions.","","## Lineages"]
    for name in ("transformation","generation","sound"): out += [f"### {name.title()}","```text",*a["lineages"][name],"```"]
    out += ["","## Counterfactual comparisons",f"- Alternate B `{cf['alternate_b_selection']['candidate_id']}` changes only `{', '.join(cf['alternate_b_selection']['changed_sections'])}`.",f"- No revision restores the selected raw candidate: {cf['without_revision']['restores_selected_candidate_exactly']}.",f"- Alternate playback leaves symbolic data unchanged: {cf['alternate_playback']['symbolic_score_unchanged']}.","","## Defensible claims",*[f"- {x}" for x in a["final_claims"]],"","## Limitations",*[f"- {x}" for x in a["limitations"]],"","Decision counts describe records, not creative importance or an authorship percentage.",""]
    return "\n".join(out)

def write_authorship_artifacts(audit, output=Path("outputs")):
    output.mkdir(parents=True,exist_ok=True); j=output/"chapter_35_authorship_audit.json"; m=output/"chapter_35_authorship_report.md"
    j.write_text(json.dumps(audit,indent=2,sort_keys=True)+"\n"); m.write_text(render_authorship_report(audit)); return j,m

def run_chapter_35(output=Path("outputs")):
    a=build_authorship_audit(); paths=write_authorship_artifacts(a,output)
    print(f"Chapter 35 — What Did the Computer Actually Compose?\nCanonical audit: Chapter 34 — {TITLE}\n\nGENERATED ≠ TRANSFORMED ≠ DERIVED ≠ SELECTED ≠ REVISED ≠ ARRANGED ≠ SYNTHESIZED ≠ PERFORMED")
    print("\n"+"\n".join(f"- {x}" for x in a["final_claims"])); print("\nCreated:\n"+"\n".join(map(str,paths))); return paths
