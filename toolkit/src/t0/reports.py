"""Read-only folds over the View. v0.1 ships the daily-time digest (methodology §4.1: merges, reviews
stale for more than 24h, blockers). No per-person volume metrics: per person, only what is in progress or blocked.
"""
from __future__ import annotations

from datetime import timedelta

from .okf.document import to_dt
from .view import View

REVIEW_STALE = timedelta(hours=24)


def digest(view: View, now: str, *, since: str) -> list[str]:
    t_now, t_since = to_dt(now), to_dt(since)
    merges, blockers = [], []
    for ev in view.events:
        try:
            at = to_dt(ev.at)
        except ValueError:
            continue
        if at < t_since:
            continue
        c = view.concepts.get(ev.target) or (view.concepts.get(view.by_jira.get(ev.target, "")) if ev.target else None)
        if ev.kind.value == "pr-merged":
            merges.append(f"- {ev.payload.get('pr') or ev.target}" + (f" ({c.kb_id} {c['title']})" if c else ""))
        elif ev.kind.value == "blocker":
            src = view.at(ev.source.value)
            blockers.append(f"- {src['title'] if src else ev.target} ({ev.actor})")
    stale = []
    for s in view.of_type("Slice"):
        if s.state != "in-review" or not s.history:
            continue
        last = s.history[-1].at
        if t_now - to_dt(last) > REVIEW_STALE:
            stale.append(f"- {s['jira'] or s.kb_id} {s['title']}: PR {s['pr'] or '?'} parado desde {last[:16]}")
    blocked = [f"- {s['jira'] or s.kb_id} {s['title']}" + (f" (por {s['blocked_by']})" if s["blocked_by"] else "")
               for s in view.of_type("Slice") if s.state == "blocked"]
    return (["## Digest", "", f"### Merges desde {since[:16]}"] + (merges or ["- nenhum"])
            + ["", "### Review parado há mais de 24h"] + (stale or ["- nenhum"])
            + ["", "### Bloqueios"] + ((blockers + blocked) or ["- nenhum"]))
