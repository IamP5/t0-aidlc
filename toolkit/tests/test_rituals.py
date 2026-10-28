import subprocess

import pytest

from t0 import rituals
from t0.kb import KB
from t0.profile.spec import EventKind
from t0.redact import redact
from t0.view import Ref
from t0.write import Plan, Refusal
from test_check import build
from test_kb import do, env, on  # noqa: F401  (autouse env fixture)

NOW = "2026-10-28T10:00:00-03:00"
G = "generated: { by: human:ana, at: 2026-10-27T10:00:00-03:00 }"


def concept(kb, rel, type_, uid, extra):
    p = kb / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(f"---\ntype: {type_}\ntitle: \"{uid}\"\ndescription: \"d\"\nuid: {uid}\nowner: role:x\n{G}\n{extra}---\n")


def ritual_kb(tmp_path, *, lgpd=False):
    kb = build(tmp_path)
    for slug, transcribable in (("daily-time", "true"), ("harness-health", "false"), ("demo", "false")):
        concept(kb, f"rituals/{slug}/ritual.md", "Ritual", f"ritual-{slug}",
                f"cadence: diária\nduration: PT10M\nfacilitator: role:flow-steward\ncommand: t0 ritual {slug}\nrecorded: true\n"
                f"transcribable: {transcribable}\ninputs:\n  - {{id: b, source: \"kb:Slice state=blocked\", desc: travados}}\n"
                "  - {id: m, source: \"forge:merged\", desc: merges}\n  - {id: r, source: \"forge:review-pending\", desc: reviews}\n"
                "state: active\nstatus: stable\n")
    for slug, who in (("flow-steward", "human:ana"), ("harness-keeper", "human:bia")):
        concept(kb, f"team/rotations/{slug}.md", "Rotation", f"rotation-{slug}",
                f"role: /team/roles/{slug}.md\ncadence: P2W\nroster: [human:ana, human:bia, human:caio]\nassignments:\n"
                f"  - {{who: {who}, from: 2026-10-20T09:00:00-03:00, to: 2026-11-03T09:00:00-03:00}}\n"
                "stale_after: 2026-11-03T09:00:00-03:00\n")
    concept(kb, "methodology/policies/transcript-retention.md", "Policy", "policy-transcript-retention",
            f"persist: {'on' if lgpd else 'dry-run'}\nlgpd_signoff: {'human:lead' if lgpd else 'null'}\n"
            "thresholds: { retention: P180D }\nstale_after: 2027-01-01T00:00:00-03:00\n")
    subprocess.run(["git", "-C", str(kb), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qam", "x"], check=False)
    subprocess.run(["git", "-C", str(kb), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(kb), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "rituais"], check=True)
    return kb


def test_parse_decisions_markdown_and_yaml():
    md = ("## Presentes\n- ana\n- human:bia\n## Decisões\n- canal #t0 (dono: bia, prazo: 2026-10-30)\n"
          "## Bloqueios\n- sem token (dono: caio)\n## Rodízio\n- flow-steward: bia\n")
    c = rituals.parse_decisions(md)
    assert c.attended == ("human:ana", "human:bia") and c.rotation == {"flow-steward": "human:bia"}
    assert c.decisions == (rituals.Decision("canal #t0", "human:bia", "2026-10-30"),
                           rituals.Decision("sem token", "human:caio", None, "blocker"))
    y = rituals.parse_decisions("decisions:\n  - {text: x, owner: ana}\naccepted: [HI-0001 com PR]\n")
    assert y.decisions[0].owner == "human:ana" and y.accepted == ("HI-0001",)


def test_open_daily_time_prints_the_digest_and_inputs(tmp_path):
    kb = ritual_kb(tmp_path)
    do(kb, "record", EventKind.BLOCKER, "sem token do forge")
    text = rituals.open_agenda(KB.open(kb).view(), "daily-time", NOW)
    assert "## Digest" in text and "sem token do forge (human:ana)" in text
    assert "- travados: 0" in text and text.count("Merges e reviews: sem forge configurado, não consultados") == 1
    assert "forge:" not in text
    assert isinstance(rituals.open_agenda(KB.open(kb).view(), "nada", NOW), Refusal)


def test_close_needs_an_owner_for_every_decision_and_is_idempotent(tmp_path):
    kb = ritual_kb(tmp_path)
    do(kb, "record", EventKind.DECISION, "usar o canal #t0")
    v = KB.open(kb).view()
    r = rituals.close(v, "daily-time", rituals.CloseInput(), now=NOW, handle="ana")
    assert isinstance(r, Refusal) and "usar o canal #t0" in r.reasons_pt[0]
    inp = rituals.parse_decisions("## Decisões\n- usar o canal #t0 (dono: bia)\n")
    p = rituals.close(v, "daily-time", inp, now=NOW, handle="ana")
    rec = p.knowledge.puts[0]
    assert rec.path == "/rituals/daily-time/2026-10-28.md" and "owner: human:bia" in rec.text
    KB.open(kb).apply(p)
    branch = on(kb, p.knowledge.branch)
    again = rituals.close(branch.view(), "daily-time", inp, now=NOW, handle="ana")
    assert again.knowledge.puts[0].text == (branch.tree / "rituals/daily-time/2026-10-28.md").read_text()


def test_unowned_blocker_is_recorded_and_listed_by_the_next_daily_time(tmp_path):
    kb = ritual_kb(tmp_path)
    concept(kb, "rituals/daily-pod/ritual.md", "Ritual", "ritual-daily-pod",
            "cadence: diária\nduration: PT30M\nfacilitator: role:bet-owner\ncommand: t0 ritual daily-pod\n"
            "recorded: true\ntranscribable: true\nstate: active\nstatus: stable\n")
    inp = rituals.parse_decisions("## Bloqueios\n- review do SBP-2 parado (dono: a definir)\n- sem ambiente de QA\n"
                                  "## Decisões\n- usar o canal #t0 (dono: bia)\n")
    assert [d.owner for d in inp.decisions] == ["human:bia", "unassigned", "unassigned"]
    p = rituals.close(KB.open(kb).view(), "daily-pod", inp, now=NOW, handle="ana")
    assert isinstance(p, Plan)
    rec = p.knowledge.puts[0].text
    assert "owner: unassigned" in rec and "Bloqueio: sem ambiente de QA (dono: a definir)" in rec
    KB.open(kb).apply(p)
    text = rituals.open_agenda(on(kb, p.knowledge.branch).view(), "daily-time", "2026-10-29T10:00:00-03:00")
    section = text.split("### Bloqueios sem dono")[1]
    assert "- review do SBP-2 parado (daily-pod de 2026-10-28)" in section and "sem ambiente de QA" in section
    assert "canal #t0" not in section


def test_decision_still_needs_an_owner_even_written_as_a_definir(tmp_path):
    kb = ritual_kb(tmp_path)
    inp = rituals.parse_decisions("## Decisões\n- usar o canal #t0 (dono: a definir)\n")
    r = rituals.close(KB.open(kb).view(), "daily-time", inp, now=NOW, handle="ana")
    assert isinstance(r, Refusal) and "toda decisão tem dono" in r.reasons_pt[0]


def test_harness_health_refuses_an_accepted_item_without_pr(tmp_path):
    kb = ritual_kb(tmp_path)
    do(kb, "new", "harness", pattern="esquece fuso")
    subprocess.run(["git", "-C", str(kb), "switch", "-q", "main"], check=True)
    subprocess.run(["git", "-C", str(kb), "merge", "-q", "kb/ana/HI-0001"], check=True)
    inp = rituals.CloseInput(accepted=("HI-0001",))
    r = rituals.close(KB.open(kb).view(), "harness-health", inp, now=NOW, handle="ana")
    assert isinstance(r, Refusal) and "t0 ci HI-0001" in r.reasons_pt[0]
    do(kb, "ci", "HI-0001", pr="api#5", state="draft")
    p = rituals.close(KB.open(kb).view(), "harness-health", inp, now=NOW, handle="ana")
    assert isinstance(p, Plan) and "harness_accepted:\n- HI-0001" in p.knowledge.puts[0].text


def test_demo_records_the_new_rotation(tmp_path):
    kb = ritual_kb(tmp_path)
    v = KB.open(kb).view()
    assert isinstance(rituals.close(v, "demo", rituals.CloseInput(), now=NOW, handle="ana"), Refusal)
    same = rituals.CloseInput(rotation={"flow-steward": "human:bia", "harness-keeper": "human:bia"})
    assert "dois papéis" in " ".join(rituals.close(v, "demo", same, now=NOW, handle="ana").reasons_pt)
    ok = rituals.CloseInput(rotation={"flow-steward": "human:bia", "harness-keeper": "human:caio"})
    p = rituals.close(v, "demo", ok, now=NOW, handle="ana")
    KB.open(kb).apply(p)
    rot = on(kb, p.knowledge.branch).get(Ref("/team/rotations/flow-steward.md"))
    assert rot["assignments"][-1] == {"who": "human:bia", "from": NOW, "to": "2026-11-11T10:00:00-03:00"}
    assert rot["assignments"][-2]["to"] == NOW and rot["stale_after"] == "2026-11-11T10:00:00-03:00"


@pytest.mark.parametrize("lgpd", [False, True])
def test_transcript_persists_only_after_lgpd_signoff(tmp_path, lgpd):
    kb = ritual_kb(tmp_path, lgpd=lgpd)
    t = redact("ana: cpf 529.982.247-25 [fora do registro]x[/fora do registro]")
    p = rituals.close(KB.open(kb).view(), "daily-time", rituals.CloseInput(), now=NOW, handle="ana", transcript=t)
    paths = [d.path for d in p.knowledge.puts]
    assert ("/transcripts/2026-10-28-daily-time.md" in paths) is lgpd
    if lgpd:
        tr = p.knowledge.puts[1].text
        assert "529" not in tr and "off_record_spans: 1" in tr and "stale_after: '2027-04-26T10:00:00-03:00'" in tr
    else:
        assert any("dry-run" in m for m in p.messages_pt)
    r = rituals.close(KB.open(kb).view(), "demo", rituals.CloseInput(), now=NOW, handle="ana", transcript=t)
    assert isinstance(r, Refusal)
