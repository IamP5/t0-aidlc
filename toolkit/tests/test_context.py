import json
import re
from dataclasses import replace
from pathlib import Path

import pytest

from t0.context import (
    AGENTS_BUDGET, DELTA_BUDGET, SUBAGENT_BUDGET, BetFacts, Card, CardFacts, CardFormat, CardOverBudget,
    ResolvedBet, Section, SliceFacts, Stamp, WorkspaceFacts, card_skills, compose, parse_stamp, render,
)
from t0.okf.document import BundlePath, Document
from t0.view import Concept, View

STAMP = Stamp("9f3c1e2", "2026-10-27T13:02:11-03:00", "bet.json", "BET-042")
WS = WorkspaceFacts("payments", (("ledger", "Ledger", "main", False), ("api", "API REST", "PAY-131-x", False),
                                 ("admin", "Backoffice", "main", True)), "./kb")


def bet(n_ac=4, n_slices=2, intent_len=20, title="Limites diários"):
    slices = tuple(SliceFacts(f"0{i}-s", f"slice {i}", "api", "ready", f"PAY-13{i}", None) for i in range(n_slices))
    return BetFacts("BET-042", title, "active", "P2W", "2026-11-07", "/products/payments/bets/BET-042",
                    tuple("x" * intent_len for _ in range(3)), "PAY-130", tuple(f"critério {i}" for i in range(n_ac)),
                    slices, "PAY-123")


def test_full_card_has_all_sections_and_stamp():
    card = compose(CardFacts(STAMP, WS, bet()), CardFormat.AGENTS)
    assert card.dropped == ()
    assert card.text.startswith("<!-- t0:card kb=9f3c1e2 at=2026-10-27T13:02:11-03:00 rule=bet.json -->")
    for heading in ("## Bet ativa: BET-042", "## Repos", "## Change set", "## Mapa do KB", "## Skills"):
        assert heading in card.text
    assert "[ausente: sem acesso]" in card.text
    assert parse_stamp(card.text) == ("9f3c1e2", "2026-10-27T13:02:11-03:00", "bet.json")


def test_truncation_drops_bottom_sections_first_and_keeps_1_to_3():
    many = bet(n_slices=10, intent_len=2500)
    card = compose(CardFacts(STAMP, WS, many), CardFormat.AGENTS)
    assert len(card.text) <= AGENTS_BUDGET
    assert card.dropped[0] is Section.SKILLS
    assert "## Bet ativa" in card.text and "## Repos" in card.text
    assert all(s not in (Section.HEADER, Section.BET, Section.REPOS) for s in card.dropped)


def test_trims_acceptance_but_never_below_three():
    huge = BetFacts("BET-1", "t", "active", "P2W", "x", "/products/p/bets/BET-1", (), "PAY-1",
                    tuple("c" * 600 for _ in range(30)), ())
    card = compose(CardFacts(STAMP, WS, huge), CardFormat.AGENTS)
    assert len(card.text) <= AGENTS_BUDGET
    assert card.text.count("- " + "c" * 600) >= 3


def test_sections_1_to_3_over_budget_raises():
    huge = BetFacts("BET-1", "t" * 9000, "active", "P2W", "x", "/products/p/bets/BET-1", (), None, (), ())
    with pytest.raises(CardOverBudget):
        compose(CardFacts(STAMP, WS, huge), CardFormat.AGENTS)


def test_card_constructor_rejects_over_budget():
    with pytest.raises(CardOverBudget):
        Card("x" * 101, 100, STAMP, ())


def test_delta_none_when_fresh_and_bounded_when_changed():
    facts = CardFacts(STAMP, WS, bet(n_ac=40, intent_len=400))
    assert compose(facts, CardFormat.DELTA) is None
    delta = compose(facts, CardFormat.DELTA, changed=frozenset({Section.BET, Section.CHANGESET}))
    assert len(delta.text) <= DELTA_BUDGET
    assert "Isto substitui as seções 2 e 4 do AGENTS.md" in delta.text
    assert "## Repos" not in delta.text


def test_subagent_card_budget():
    card = compose(CardFacts(STAMP, WS, bet(n_ac=40, intent_len=300)), CardFormat.SUBAGENT)
    assert len(card.text) <= SUBAGENT_BUDGET
    assert "Story ativa PAY-130" in card.text


def test_no_bet_card_says_ask():
    card = compose(CardFacts(Stamp("abc", "t", "none", None), WS, None), CardFormat.AGENTS)
    assert "Nenhuma bet resolvida" in card.text
    skills = card.text.split("## Skills\n", 1)[1]
    assert skills.startswith("- `/t0` porta de entrada") and "`bet-new`" in skills
    assert "slice-build" not in skills


def test_story_card_points_to_slice_skills():
    card = compose(CardFacts(STAMP, WS, bet()), CardFormat.AGENTS)
    skills = card.text.split("## Skills\n", 1)[1]
    assert skills.startswith("- `/t0` porta de entrada") and "`slice-build`" in skills and "`slice-verify`" in skills


PLUGIN_SKILLS = Path(__file__).resolve().parents[2] / "plugin" / "skills"


@pytest.mark.parametrize("b", [None, bet(), replace(bet(), story=None), replace(bet(), state="proposed"),
                               replace(bet(), state="shipped")])
def test_card_names_only_real_skills(b):
    real = {p.parent.name for p in PLUGIN_SKILLS.glob("*/SKILL.md")}
    named = {re.match(r"`/?([a-z0-9-]+)", s).group(1) for s in card_skills(b)}
    assert named <= real, named - real


def test_json_format_is_parseable():
    card = compose(CardFacts(STAMP, WS, bet()), CardFormat.JSON)
    assert json.loads(card.text)["bet"]["story"] == "PAY-130"


def _concept(path, fm, body="", derived=None):
    return Concept(Document(BundlePath(path), fm, body, True, ""), None, derived or {}, ())


def test_render_from_view_resolves_active_story_acceptance():
    b = _concept("/products/payments/bets/BET-042/bet.md",
                 {"type": "Bet", "title": "Limites", "appetite": "P2W", "cycle_end": "2026-11-07"},
                 "# Bet\nCliente quer limite diário.\n", {"state": "active", "jira": "PAY-123"})
    s1 = _concept("/products/payments/bets/BET-042/slices/01-ledger.md",
                  {"type": "Slice", "title": "Ledger", "repo": "ledger"},
                  "## Critérios de aceite\n\n- saldo bloqueia\n", {"state": "done", "jira": "PAY-130"})
    s2 = _concept("/products/payments/bets/BET-042/slices/02-api.md",
                  {"type": "Slice", "title": "API", "repo": "api", "depends_on": ["01-ledger"]},
                  "## Criterios de aceite\n\n- retorna 422 acima do limite\n- loga a recusa\n\n## Como verificar\n\n- saldo bloqueia\n", {"state": "ready", "jira": "PAY-131"})
    other = _concept("/products/payments/bets/BET-051/slices/01-x.md", {"type": "Slice", "title": "X", "repo": "web"})
    view = View({c.doc.path.value: c for c in (b, s1, s2, other)}, {}, {}, (), "9f3c1e2", 0)
    card = render(view, WS, ResolvedBet(b, "PAY-131", "branch"), CardFormat.AGENTS, now="2026-10-27T10:00:00-03:00")
    assert "- retorna 422 acima do limite" in card.text and "- loga a recusa" in card.text
    assert "saldo bloqueia" not in card.text
    assert "Estado `active`" in card.text and "Feature PAY-123" in card.text
    assert "02-api `api` ready, depende de 01-ledger" in card.text
    assert "01-x" not in card.text
    assert "rule=branch" in card.text
