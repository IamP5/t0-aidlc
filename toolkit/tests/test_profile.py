from t0.gates import CHECKS
from t0.profile.spec import CheckId, StateOwner
from t0.profile.table import DOMAIN_TYPES, GATES, REGISTRY, TRACKS, TYPES

V2_TYPES = {"Idea", "Bet", "Spec", "Slice", "ADR", "Ritual", "Ritual Record", "Transcript", "Harness Item", "Product",
            "Workspace", "Eval Suite", "Adoption Report", "Policy", "Template", "Person", "Role", "Rotation",
            "Glossary Term", "Step"}


def test_table_has_the_twenty_v2_types_and_nothing_removed():
    assert set(DOMAIN_TYPES) == V2_TYPES and len(DOMAIN_TYPES) == 20
    assert not {t.name for t in TYPES} & {"Plan", "Assessment", "Bugfix", "Cycle Record", "Contract", "Gate"}


def test_v2_gates_and_tracks():
    assert [g.id for g in GATES] == ["aposta", "spec"]
    assert [t.name for t in TRACKS] == ["rapida", "bet"]
    assert all(set(t.gates) <= {g.id for g in GATES} for t in TRACKS)


def test_state_machines_are_total_and_gates_are_legal():
    for t in TYPES:
        if not t.states:
            continue
        sm = t.states
        assert sm.initial in sm.status_of
        for tr in sm.transitions:
            assert tr.from_states <= set(sm.status_of) and tr.to in sm.status_of, t.name
            assert sum(x is not None for x in (tr.via_gate, tr.via_event, tr.via_command)) == 1, t.name
            assert tr.via_gate is None or REGISTRY.gate(tr.via_gate), t.name
    for g in GATES:
        for mv in g.moves:
            spec = REGISTRY.type_named(mv.type_name)
            assert any(tr.via_gate == g.id and tr.to == mv.to for tr in spec.states.transitions)


def test_every_check_has_an_implementation():
    assert set(CHECKS) == set(CheckId)


def test_path_to_type_is_a_function():
    samples = {"/ideas/IDEA-0001.md": "Idea", "/products/p/bets/BET-001/bet.md": "Bet",
               "/products/p/bets/BET-001/spec.md": "Spec", "/products/p/bets/BET-001/slices/01-a.md": "Slice",
               "/products/p/bets/BET-001/steps/x.md": "Step", "/rituals/demo/ritual.md": "Ritual",
               "/rituals/demo/2026-10-28.md": "Ritual Record", "/harness/HI-0001.md": "Harness Item",
               "/team/rotations/flow-steward.md": "Rotation", "/profile.md": "OKF Profile"}
    for path, name in samples.items():
        assert REGISTRY.type_for_path(path)[0].name == name, path


def test_derived_keys_split_render_from_decision():
    slice_, bet = REGISTRY.type_named("Slice"), REGISTRY.type_named("Bet")
    assert slice_.states.owner is StateOwner.RENDER and {"state", "pr", "jira", "status"} <= REGISTRY.render_keys(slice_)
    assert "state" not in REGISTRY.render_keys(bet) and "state" in REGISTRY.derived_keys(bet)
    assert {"pr", "state"} <= REGISTRY.render_keys(REGISTRY.type_named("Harness Item"))
