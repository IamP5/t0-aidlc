"""The one writer of derived content. Runs only in the KB's kb-render workflow (serialized).

materialize(view) produces, for the whole bundle (cheap: a KB is O(10^3) files):
  - derived keys on every concept (state, status, verified, jira, pr, audit, markers_open, ...)
  - every index.md (OKF §8 shape: '# <index_section_pt>' groups from REGISTRY, entries reuse description;
    root index keeps ONLY `okf_version: "0.2"` - fixes reference issue #25)
  - each bet's log.md (type: Log; '## YYYY-MM-DD' newest first; '**Verbo** por <actor>: o quê (link)')
    and the bundle /log.md (team events only)
  - each bet's changeset.md from pr-* and integration records
  - /profile.md from REGISTRY (version, common keys, type table, gates table, bet-type table)
Re-running on an unchanged main yields an empty DerivedChange (byte-equal outputs are dropped).
"""
from __future__ import annotations

from .view import View
from .write import DerivedChange


def materialize(view: View) -> DerivedChange:
    raise NotImplementedError


def render_log_line(event: object) -> str:
    """Same function used by render and by `t0 kb status` preview, so the preview equals the result."""
    raise NotImplementedError
