import pytest

from t0.okf.document import BundlePath, Document, ParseError, actor, dump, duration, instant, parse

P = BundlePath("/x/y.md")


def test_timestamps_stay_strings_and_round_trip():
    d = parse(P, "---\ntype: X\nat: 2026-10-28T10:00:00-03:00\nday: 2026-10-28\n---\ncorpo\n")
    assert isinstance(d, Document)
    assert d.frontmatter == {"type": "X", "at": "2026-10-28T10:00:00-03:00", "day": "2026-10-28"}
    again = parse(P, dump(d.frontmatter, d.body))
    assert again.frontmatter == d.frontmatter and again.body == "corpo\n"


def test_no_frontmatter_is_body_only():
    d = parse(P, "# título\n")
    assert isinstance(d, Document) and not d.has_frontmatter and d.body == "# título\n"


@pytest.mark.parametrize("text", ["---\ntype: X\n", "---\n- a\n---\n", "---\n[]\n---\n", "---\n0\n---\n", "---\na: [\n---\n"])
def test_broken_frontmatter_is_a_parse_error(text):
    assert isinstance(parse(P, text), ParseError)


def test_bundle_path_grammar():
    assert BundlePath.parse("./a/b.md").value == "/a/b.md"
    assert BundlePath.parse("a/b.md").concept_id == "a/b"
    with pytest.raises(ValueError):
        BundlePath.parse("/a/../b.md")
    assert BundlePath("/a/index.md").is_reserved and not BundlePath("/a/b.md").is_reserved
    assert not BundlePath("/a/-b.md").segments_ok


def test_value_grammars():
    assert instant("2026-10-28T10:00:00Z") and not instant("2026-10-28") and not instant("2026-10-28T10:00:00")
    assert actor("human:ana") and actor("claude-code/opus-5.5") and not actor("ana")
    assert duration("P2W").days == 14 and duration("PT30M").seconds == 1800 and duration("P") is None
