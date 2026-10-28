"""Jira REST adapter skeleton. Not wired in v0.1: the flavor (Cloud or Data Center) is unknown
(DESIGN.md, Deferred). The flavor strategy is the only place that knows API versions and body formats.
"""
from __future__ import annotations

from dataclasses import dataclass

from .port import TrackerConfig

_NOT_WIRED = "JiraRest não está ligado na v0.1: falta a resposta 'Jira Cloud ou DC?'; use --tracker file:<dir>"


@dataclass(frozen=True)
class Flavor:
    name: str
    api_prefix: str          # '/rest/api/3' | '/rest/api/2'
    body_format: str         # 'adf' | 'wiki'
    user_field: str          # 'accountId' | 'name'
    auth: str                # 'basic-email-token' | 'bearer-pat'


CLOUD = Flavor("cloud", "/rest/api/3", "adf", "accountId", "basic-email-token")
DC = Flavor("dc", "/rest/api/2", "wiki", "name", "bearer-pat")
FLAVORS = {"jira-cloud": CLOUD, "jira-dc": DC}


class JiraRest:
    def __init__(self, cfg: TrackerConfig) -> None:
        self.cfg = cfg
        self.flavor = FLAVORS[cfg.kind]

    def _unwired(self, *_: object, **__: object) -> None:
        raise NotImplementedError(_NOT_WIRED)

    find = get = create = update = transition = link_blocks = comment = comments_since = intake = _unwired
