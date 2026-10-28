import shutil
from pathlib import Path

from t0.gates import evaluate
from t0.kb import read_docs
from t0.okf.document import Document
from t0.profile.table import REGISTRY
from t0.view import Ref, fold

FIX = Path(__file__).parent / "fixtures" / "kb-negative" / "_base"
NOW = "2026-10-28T10:00:00-03:00"
BET = "products/p/bets/BET-001/bet.md"
SPEC = "products/p/bets/BET-001/spec.md"
SLICE = "products/p/bets/BET-001/slices/01-api.md"


def view(tmp_path, edits=()):
    kb = tmp_path / "kb"
    shutil.copytree(FIX, kb)
    for rel, old, new in edits:
        p = kb / rel
        text = p.read_text() if p.exists() else ""
        assert old in text, (rel, old)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text.replace(old, new, 1) if old else new)
    return fold([d for d in read_docs(kb) if isinstance(d, Document)], kb_sha="t")


def decide(v, gate, ref="BET-001"):
    return evaluate(v, REGISTRY.gate(gate), v.resolve(Ref(ref)), now=NOW)


def failed(d):
    return {r.check.value for r in d.results if not r.passed}


def test_aposta_bet_track_passes_with_the_owner_as_approver(tmp_path):
    d = decide(view(tmp_path), "aposta")
    assert d.ok and d.approvers == ("human:ana",) and d.already is None
    assert [(c.kb_id, to) for c, to in d.target.moves] == [("BET-001", "active")]


def test_aposta_names_missing_bet_fields(tmp_path):
    d = decide(view(tmp_path, [(BET, 'kill_criteria: "ninguém usa"\n', "")]), "aposta")
    assert not d.ok and failed(d) == {"bet_fields_complete"}
    assert "kill_criteria" in d.results[0].detail_pt


def test_aposta_appetite_over_the_track_ceiling(tmp_path):
    d = decide(view(tmp_path, [(BET, "appetite: P1W", "appetite: P3W")]), "aposta")
    assert "bet_fields_complete" in failed(d)


def test_lead_required_for_tier2_and_missing_lead_is_a_problem(tmp_path):
    d = decide(view(tmp_path, [(SLICE, "tier: 1", "tier: 2")]), "aposta")
    assert not d.ok and any("Lead" in p for p in d.approver_problems)
    lead = ("team/roles/lead.md", "", "---\ntype: Role\ntitle: Lead\ndescription: d\nuid: role-lead\nowner: role:lead\n"
            "generated: { by: human:ana, at: 2026-10-27T10:00:00-03:00 }\nholders: [human:bia]\n---\n")
    d = decide(view(tmp_path / "2", [(SLICE, "tier: 1", "tier: 2"), lead]), "aposta")
    assert d.ok and d.approvers == ("human:ana", "human:bia")


def test_cross_pod_requires_the_lead(tmp_path):
    d = decide(view(tmp_path, [(BET, "pods: [p]", "pods: [p, q]")]), "aposta")
    assert any("cruza pods" in p for p in d.approver_problems)


def test_junior_never_approves_alone(tmp_path):
    d = decide(view(tmp_path, [("team/people/ana.md", "handle: ana", "handle: ana\njunior: true")]), "aposta")
    assert "júnior não aprova sozinho" in d.approver_problems


def test_rapida_needs_current_expected_unchanged_and_the_test(tmp_path):
    v = view(tmp_path, [(BET, "track: bet", "track: rapida"), (BET, "appetite: P1W", "appetite: P1D")])
    d = decide(v, "aposta")
    assert failed(d) == {"rapida_slice_complete"}
    assert "seções '## Atual', '## Esperado', '## Não muda' vazias ou ausentes" in d.results[1].detail_pt
    body = "\n## Atual\n\nsai 07:50\n\n## Esperado\n\nsai 08:50\n\n## Não muda\n\n- o canal\n"
    v = view(tmp_path / "2", [(BET, "track: bet", "track: rapida"), (BET, "appetite: P1W", "appetite: P1D"),
                              (SLICE, "Corpo.\n", "Corpo.\n" + body)])
    assert decide(v, "aposta").ok


def test_spec_refuses_before_the_aposta_and_with_open_markers(tmp_path):
    assert "bet_active" in failed(decide(view(tmp_path), "spec"))
    v = view(tmp_path / "2", [(BET, "state: proposed\nstatus: draft", "state: active\nstatus: stable"),
                              (SPEC, "- retorna 422 acima do limite\n", "- retorna 422 acima do limite\n\n[PRECISA ESCLARECER] qual?\n")])
    d = decide(v, "spec")
    assert failed(d) == {"markers_zero"} and "linhas" in d.results[1].detail_pt


def test_spec_refuses_gherkin_and_empty_slices(tmp_path):
    v = view(tmp_path, [(BET, "state: proposed\nstatus: draft", "state: active\nstatus: stable"),
                        (SLICE, "retorna 422 acima do limite", "Quando passa do limite"), (SLICE, "\npytest -k limite", "")])
    d = decide(v, "spec")
    assert failed(d) == {"slices_ready"}
    assert "Gherkin" in d.results[-1].detail_pt and "seção '## Como verificar' vazia ou ausente" in d.results[-1].detail_pt


ACTIVE = (BET, "state: proposed\nstatus: draft", "state: active\nstatus: stable")


def test_spec_passes_from_body_sections_alone(tmp_path):
    v = view(tmp_path, [ACTIVE, (SPEC, "## Critérios de aceite", "## Criterios de Aceite")])
    d = decide(v, "spec")
    assert d.ok, d.lines_pt()
    assert next(r for r in d.results if r.check.value == "acceptance_bullets").detail_pt == "1 critérios"


def test_spec_refuses_an_empty_section_naming_it(tmp_path):
    v = view(tmp_path, [ACTIVE, (SPEC, "- retorna 422 acima do limite\n", "<!-- só comentário -->\n- \n")])
    d = decide(v, "spec")
    assert failed(d) == {"acceptance_bullets"}
    assert "seção '## Critérios de aceite' sem bullets" in d.results[2].detail_pt
    v = view(tmp_path / "2", [ACTIVE, (SPEC, "\npytest -k limite", "\n<comando>")])
    d = decide(v, "spec")
    assert failed(d) == {"verify_how_present"}
    assert d.results[3].detail_pt.endswith("seção '## Como verificar' vazia ou ausente")


def test_already_decided_is_reported_not_redone(tmp_path):
    v = view(tmp_path, [(BET, "state: proposed\nstatus: draft", "state: active\nstatus: stable")])
    assert decide(v, "aposta").already == "active"
