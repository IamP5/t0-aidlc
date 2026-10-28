"""The facade. CLI, MCP server, hooks and rituals call only this.

Hides: where the KB is, parse, fold, spool overlay, id reservation, lane routing, gate checks, render.
Every mutating method returns Plan | Refusal. Knowledge planners first open the change's branch worktree
(`W.checkout`, skipped under dry-run) and read from it, so the plan is computed from the PR head it will
commit to. `root` is the main clone (spool, refs, derived lane); `tree` is where reads happen: the main
clone, the worktree the cwd is in, or the checkout a planner opened. `apply` is the one effect.
"""
from __future__ import annotations

import fcntl
import os
import re
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml

from . import gates as G
from . import write as W
from .check import CheckInput, Level, Report, Severity, check as run_check, kind_problem
from .context import Card, CardFormat, ResolvedBet, Section, parse_stamp, render as render_card
from .okf.document import Actor, BundlePath, Document, ParseError, actor, dump, parse, section
from .profile.spec import EventKind, Lane, StateOwner, TypeSpec
from .profile.table import ACCEPTANCE, RAPIDA_SLICE_BODY, REGISTRY, VERIFY
from .render import materialize, set_keys
from .view import Concept, Ref, View, bet_folder, fold
from .write import Applied, ApplyMode, KnowledgeChange, Plan, Refusal, RenderedDoc

# Keys t0 always writes itself; `--set` refuses them.
T0_KEYS = ("type", "uid", "state", "status", "verified", "generated")

UNAVAILABLE = "KB indisponível: rode `t0 ws sync` ou passe --kb. Pare."
_SEQ = {"Idea": r"ideas/IDEA-(\d+)", "Bet": r"/bets/BET-(\d+)/", "ADR": r"adr/ADR-(\d+)", "Harness Item": r"harness/HI-(\d+)"}


class Source(Enum):
    MAIN = "main"
    MAIN_PLUS_SPOOL = "main+spool"
    WORKTREE = "worktree"


class KBUnavailable(Exception):
    def __init__(self, msg: str = UNAVAILABLE) -> None:
        super().__init__(msg)


@dataclass(frozen=True)
class Hit:
    uid: str
    path: str
    type: str
    title: str
    description: str
    state: str | None
    snippet: str


@dataclass(frozen=True)
class Query:
    text: str | None = None
    type: str | None = None
    product: str | None = None
    bet: str | None = None
    state: str | None = None
    tags: tuple[str, ...] = ()
    limit: int = 20


def _is_kb(d: Path) -> bool:
    idx = d / "index.md"
    try:
        return idx.is_file() and "okf_version" in idx.read_text(encoding="utf-8")[:2000]
    except OSError:
        return False


def locate(cwd: Path | None = None) -> Path | None:
    cwd = (cwd or Path.cwd()).resolve()
    for d in (cwd, *cwd.parents):
        if (d / ".t0/workspace.json").is_file() and _is_kb(d / "kb"):
            return d / "kb"
        if _is_kb(d):
            return d
    cfg = Path.home() / ".t0/config.yaml"
    if cfg.is_file():
        data = yaml.safe_load(cfg.read_text(encoding="utf-8")) or {}
        if isinstance(data, dict) and data.get("kb") and _is_kb(Path(data["kb"]).expanduser()):
            return Path(data["kb"]).expanduser()
    return None


def handle() -> str:
    if os.environ.get("T0_HANDLE"):
        return W.slug(os.environ["T0_HANDLE"])
    cfg = Path.home() / ".t0/config.yaml"
    if cfg.is_file():
        data = yaml.safe_load(cfg.read_text(encoding="utf-8")) or {}
        if isinstance(data, dict) and data.get("handle"):
            return W.slug(str(data["handle"]))
    p = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True)
    return W.slug(p.stdout.strip() or os.environ.get("USER", "dev"))


def read_docs(root: Path) -> list[Document | ParseError]:
    out: list[Document | ParseError] = []
    for p in sorted(root.rglob("*.md")):
        rel = p.relative_to(root)
        if any(part.startswith(".") for part in rel.parts):
            continue
        out.append(parse(BundlePath("/" + rel.as_posix()), p.read_text(encoding="utf-8")))
    return out


def _yaml_value(raw: str) -> Any:
    try:
        return yaml.safe_load(raw)
    except yaml.YAMLError:
        return raw


class KB:
    def __init__(self, root: Path, *, source: Source = Source.MAIN_PLUS_SPOOL, dry: bool = False) -> None:
        self.tree = root.resolve()
        self.root = W.main_clone(self.tree) if W.is_git(self.tree) else self.tree
        self._checkout: W.Checkout | None = None
        self._ids: Any = None
        self.source = source
        self.dry = dry
        self.handle = handle()
        self.actor = Actor(f"human:{self.handle}")
        self._view: View | None = None
        self._docs: list[Document | ParseError] | None = None

    @classmethod
    def open(cls, kb_dir: Path | None = None, *, source: Source = Source.MAIN_PLUS_SPOOL, dry: bool = False) -> "KB":
        here = None if kb_dir else locate()
        d = kb_dir or (Path(os.environ["T0_KB"]) if os.environ.get("T0_KB") else None) or here
        if d is None or not Path(d).is_dir():
            raise KBUnavailable()
        if not _is_kb(Path(d)):
            raise KBUnavailable(f"{d} não é um KB OKF (sem index.md com okf_version). Pare.")
        kb = cls(Path(d), source=source, dry=dry)
        if here is not None and here.resolve() != kb.tree and W.is_git(here) and W.main_clone(here.resolve()) == kb.root:
            kb.tree = here.resolve()
        return kb

    # ------------------------------------------------------------- read

    @property
    def now(self) -> str:
        return W.now_instant()

    def docs(self) -> list[Document | ParseError]:
        if self._docs is None:
            self._docs = read_docs(self.tree)
        return self._docs

    def _spool_docs(self, landed: set[str]) -> list[Document]:
        sp = W.spool_dir(self.root)
        out = []
        for p in sorted(sp.rglob("*.md")) if sp.is_dir() else []:
            rel = "/" + p.relative_to(sp).as_posix()
            if rel in landed:
                continue
            d = parse(BundlePath(rel), p.read_text(encoding="utf-8"))
            if isinstance(d, Document):
                out.append(d)
        return out

    def view(self) -> View:
        if self._view is None:
            docs = [d for d in self.docs() if isinstance(d, Document)]
            overlay = self._spool_docs({d.path.value for d in docs}) if self.source is Source.MAIN_PLUS_SPOOL else []
            self._view = fold(docs, kb_sha=self.sha(), overlay=overlay)
        return self._view

    def reload(self) -> None:
        self._view = self._docs = None

    def sha(self, tree: Path | None = None) -> str:
        tree = tree or self.tree
        if not W.is_git(tree):
            return "worktree"
        return W.git(tree, "rev-parse", "--short", "HEAD", check=False) or "worktree"

    def get(self, ref: Ref) -> Concept | None:
        """`ref` as a planner will see it. Before a planner opens its checkout, reads move to an open knowledge
        worktree (edits or commits not yet on main): the one of this person's bet branch for a concept in a bet
        folder, else the first that holds a `ref` the tree in use lacks."""
        c = self.view().resolve(ref)
        if self._checkout is not None or not W.is_git(self.root):
            return c
        home = self.tree
        folder = bet_folder(c.path) if c is not None else None
        if c is not None and (home != self.root or folder is None):
            return c
        branch = self._bet_branch(folder.rsplit("/", 1)[1]) if folder else None
        for co in W.open_checkouts(self.root):
            if co.path == home or branch and co.branch != branch:
                continue
            self.tree = co.path
            self.reload()
            if (found := self.view().resolve(ref)) is not None:
                return found
        if self.tree != home:
            self.tree = home
            self.reload()
        return c

    def find(self, q: Query) -> list[Hit]:
        hits: list[Hit] = []
        needle = (q.text or "").lower()
        for c in sorted(self.view().concepts.values(), key=lambda c: c.path):
            if q.type and c["type"] != q.type or q.state and c.state != q.state:
                continue
            if q.product and not c.path.startswith(f"/products/{q.product}/"):
                continue
            if q.bet and f"/bets/{q.bet}/" not in c.path:
                continue
            if q.tags and not set(q.tags) <= set(c["tags"] or []):
                continue
            hay = f"{c['title']}\n{c['description']}\n{c.doc.body}".lower()
            if needle and needle not in hay:
                continue
            snip = next((l.strip() for l in c.doc.body.splitlines() if needle and needle in l.lower()), "")
            hits.append(Hit(c.uid, c.path, str(c["type"]), str(c["title"] or ""), str(c["description"] or ""), c.state, snip[:200]))
            if len(hits) >= q.limit:
                break
        return hits

    def check(self, level: Level = Level.L1, *, changed_from: str | None = None, lane: Lane | None = None) -> Report:
        docs = self.docs()
        good = [d for d in docs if isinstance(d, Document)]
        view = fold(good, kb_sha=self.sha())
        changed = base = base_view = None
        if changed_from:
            if not W.is_git(self.tree):
                raise ValueError("--changed-from precisa de um KB em git")
            names = W.git(self.tree, "diff", "--name-only", changed_from).splitlines()
            names += W.git(self.tree, "ls-files", "--others", "--exclude-standard").splitlines()
            changed = frozenset("/" + n for n in names if n.endswith(".md") and not n.startswith("."))
            base = {}
            for n in W.git(self.tree, "ls-tree", "-r", "--name-only", changed_from).splitlines():
                if n.endswith(".md") and not n.startswith("."):
                    d = parse(BundlePath("/" + n), W.git(self.tree, "show", f"{changed_from}:{n}"))
                    if isinstance(d, Document):
                        base[d.path.value] = d
            base_view = fold(base.values(), kb_sha=changed_from)
        return run_check(CheckInput(docs, view, self.now, changed, base, base_view), level)

    def context(self, ref: Ref | None, fmt: CardFormat) -> Card | None:
        from . import ws

        w = self.workspace()
        facts = w.facts() if w else None
        if ref is not None:
            c = self.get(ref)
            if c is None:
                return render_card(self.view(), facts, None, fmt, now=self.now,
                                   changed=frozenset({Section.BET}) if fmt in (CardFormat.DELTA, CardFormat.HOOK) else frozenset())
            bet = c if c["type"] == "Bet" else self.view().bet_of(c)
            resolved = ResolvedBet(bet, c["jira"] if c["type"] == "Slice" else None, "ref") if bet else None
        else:
            resolved = ws.detect_bet(self, Path.cwd())
        changed: frozenset[Section] = frozenset()
        if fmt in (CardFormat.DELTA, CardFormat.HOOK):
            agents = (w.root / "AGENTS.md") if w else None
            stamp = parse_stamp(agents.read_text(encoding="utf-8")) if agents and agents.is_file() else None
            if stamp is None or stamp[0] != self.view().kb_sha:
                changed = frozenset({Section.BET, Section.REPOS})
        return render_card(self.view(), facts, resolved, fmt, changed=changed, now=self.now)

    # ------------------------------------------------------------- helpers

    def checkout(self, branch: str) -> Refusal | None:
        """Open `branch`'s worktree and read from it. Refuses a bet branch while the main clone holds
        uncommitted edits in that bet's folder: they would stay out of the PR."""
        if self.dry or not W.is_git(self.root):
            return None
        m = re.match(r"bet/(BET-\d+)/", branch)
        stray = [p for p in W.dirty(self.root) if m and f"/bets/{m.group(1)}/" in "/" + p]
        if stray:
            return Refusal((f"mudanças sem commit no clone principal do KB ({', '.join(stray)}); mova para o worktree "
                            f"{W.worktree_root(self.root) / branch} ou descarte, e rode de novo",))
        try:
            self._checkout = W.checkout(self.root, branch)
        except W.ApplyError as e:
            return Refusal((str(e),))
        self.tree = self._checkout.path
        self.reload()
        return None

    def _branch_here_or(self, fallback: str) -> str:
        cur = W.current_branch(self.tree)
        return cur if cur and cur.startswith(("bet/", "kb/")) else fallback

    def _bet_branch(self, bet_id: str) -> str:
        return f"bet/{bet_id}/{self.handle}"

    def _hold_ids(self) -> None:
        """Ids are one sequence across every branch: hold the KB's id lock from reservation until `apply`
        commits, so two sessions on one clone never reserve the same number."""
        if self.dry or self._ids is not None or not W.is_git(self.root):
            return
        self._ids = open(self.root / ".git" / "t0-ids.lock", "a")
        fcntl.flock(self._ids, fcntl.LOCK_EX)

    def _next(self, type_name: str, *, folder: str | None = None) -> int:
        self._hold_ids()
        paths = [d.path.value for d in self.docs()]
        if W.is_git(self.root):
            refs = W.git(self.root, "for-each-ref", "--format=%(refname)", "refs/heads", "refs/remotes").splitlines()
            for r in refs:
                paths += ["/" + n for n in W.git(self.root, "ls-tree", "-r", "--name-only", r, check=False).splitlines()]
        if folder is not None:
            rx = re.compile(re.escape(folder) + r"/slices/(\d+)-")
        else:
            rx = re.compile(_SEQ[type_name])
        nums = [int(m.group(1)) for p in paths if (m := rx.search(p))]
        return max(nums, default=0) + 1

    def _template_body(self, spec: TypeSpec) -> str:
        t = next((c for c in self.view().of_type("Template") if c["template_for"] == spec.name), None)
        return t.doc.body.lstrip("\n") if t is not None and t.doc.body.strip() else spec.template_body_pt

    def _concept(self, spec: TypeSpec, fm: Mapping[str, Any], body: str) -> str:
        out: dict[str, Any] = {"type": spec.name}
        given = dict(fm)
        given.setdefault("owner", self.actor)
        given.setdefault("generated", {"by": self.actor, "at": self.now})
        if spec.states:
            st = given.get("state") or spec.states.initial
            given["state"] = st
            given["status"] = spec.states.status_of[st].value
        for f in REGISTRY.fields(spec):
            if f.name in given:
                out[f.name] = given.pop(f.name)
        out.update(given)
        return dump(out, body if body.endswith("\n") else body + "\n")

    def _sets(self, spec: TypeSpec, sets: Sequence[str]) -> dict[str, Any] | Refusal:
        names = {f.name: f for f in REGISTRY.fields(spec)}
        states = tuple(spec.states.status_of) if spec.states else ()
        out: dict[str, Any] = {}
        bad = []
        for s in sets:
            k, sep, v = s.partition("=")
            k = k.strip()
            if not sep or k not in names or names[k].derived or k in T0_KEYS:
                bad.append(f"--set {s}: `{k}` não é chave editável de {spec.name} (veja `t0 new {spec.slug} --help`)")
                continue
            val = _yaml_value(v)
            if (prob := kind_problem(names[k], val, states if k == "state" else ())):
                bad.append(f"--set {s}: `{k}` precisa ser {prob}")
                continue
            out[k] = val
        return Refusal(tuple(bad)) if bad else out

    def _upd(self, c: Concept, updates: Mapping[str, Any], body_append: str = "") -> RenderedDoc:
        text = set_keys(c.doc.raw, updates)
        if body_append and body_append.strip() not in text:
            text = text.rstrip("\n") + "\n\n" + body_append.strip() + "\n"
        return RenderedDoc(c.path, text)

    def _state(self, c: Concept, to: str) -> dict[str, Any]:
        return {"state": to, "status": c.spec.states.status_of[to].value}

    # ------------------------------------------------------------- new

    def new(self, slug: str, *, title: str | None = None, description: str | None = None, body: str | None = None,
            sets: Sequence[str] = (), ref: str | None = None, track: str | None = None, product: str | None = None,
            repo: str | None = None, tier: int | None = None, pattern: str | None = None,
            occurrence: str | None = None, depends_on: Sequence[str] = ()) -> Plan | Refusal:
        spec = REGISTRY.type_for_slug(slug)
        if spec is None:
            return Refusal((f"`t0 new {slug}` não existe; tipos: idea, bet, spec, slice, adr, harness",))
        extra = self._sets(spec, sets)
        if isinstance(extra, Refusal):
            return extra
        fn = {"idea": self._new_idea, "bet": self._new_bet, "spec": self._new_spec, "slice": self._new_slice,
              "adr": self._new_adr, "harness": self._new_harness}.get(slug)
        if fn is None:
            return Refusal((f"`t0 new {slug}` não está na v0.1; edite o arquivo e rode `t0 kb propose`",))
        return fn(title=title, description=description, body=body, extra=extra, ref=ref, track=track, product=product,
                  repo=repo, tier=tier, pattern=pattern, occurrence=occurrence, depends_on=tuple(depends_on))

    def _idea_doc(self, n: int, title: str, description: str, extra: Mapping[str, Any], body: str | None,
                  state: str = "new") -> RenderedDoc:
        spec = REGISTRY.type_named("Idea")
        fm = {"title": title, "description": description, "uid": f"idea-{n:04d}", "source": "human", **extra, "state": state}
        return RenderedDoc(f"/ideas/IDEA-{n:04d}.md", self._concept(spec, fm, body or self._template_body(spec)))

    def _dup_idea(self, title: str) -> Concept | None:
        key = W.slug(title, 200)
        return next((c for c in self.view().of_type("Idea") if W.slug(str(c["title"] or ""), 200) == key), None)

    def _new_idea(self, *, title, description, body, extra, **_: Any) -> Plan | Refusal:
        if not title:
            return Refusal(("`t0 new idea` precisa de --title (e de preferência --description)",))
        dup = self._dup_idea(title)
        if dup is not None:
            return Refusal((f"já existe {dup.kb_id} com esse título ({dup.state}); use ela",))
        n = self._next("Idea")
        branch = f"kb/{self.handle}/IDEA-{n:04d}"
        if (r := self.checkout(branch)):
            return r
        doc = self._idea_doc(n, title, description or title, extra, body)
        return Plan(knowledge=KnowledgeChange(branch, f"Ideia IDEA-{n:04d}: {title}",
                                              "Ideia nova. Aprovar este PR registra a ideia no KB.", (doc,)),
                    messages_pt=(f"IDEA-{n:04d} reservada",))

    def _new_bet(self, *, title, description, body, extra, ref, track, product, repo, tier, **_: Any) -> Plan | Refusal:
        tr = REGISTRY.track(track or "")
        if tr is None:
            return Refusal(("`t0 new bet` precisa de --track rapida|bet",))
        view = self.view()
        idea = view.resolve(Ref(ref)) if ref and re.fullmatch(r"IDEA-\d+", ref) else None
        if ref and re.fullmatch(r"IDEA-\d+", ref) and idea is None:
            return Refusal((f"{ref} não existe no KB",))
        if tr.name == "bet":
            if idea is None:
                return Refusal(("a trilha bet parte de uma IDEA existente: `t0 new bet --track bet IDEA-NNNN`",))
            if idea["verdict"] not in ("segue", "ajusta"):
                return Refusal((f"{idea.kb_id} sem veredito segue|ajusta: rode o protótipo e `t0 idea prototype`",))
        if idea is not None and idea.state in ("promoted", "killed"):
            return Refusal((f"{idea.kb_id} está `{idea.state}`" + (f" (bet {idea['bet']})" if idea["bet"] else ""),))
        free = ref if ref and idea is None else None
        title = title or (str(idea["title"]) if idea else free)
        if not title:
            return Refusal(("dê --title ou um texto: `t0 new bet --track rapida \"o que muda\"`",))
        product = product or (str(idea["product"]) if idea and idea["product"] else None) or self._ws_product()
        if not product or not (self.tree / "products" / product).is_dir():
            return Refusal((f"--product precisa ser uma pasta de /products/ (veio {product!r})",))
        n = self._next("Bet")
        if tr.name == "rapida" and free:
            n_idea = self._next("Idea")
        bet_id = f"BET-{n:03d}"
        branch = self._bet_branch(bet_id)
        if (r := self.checkout(branch)):
            return r
        view = self.view()
        idea = view.resolve(Ref(idea.kb_id)) if idea is not None else None
        folder = f"/products/{product}/bets/{bet_id}"
        bspec = REGISTRY.type_named("Bet")
        desc = description or (str(idea["description"]) if idea else title)
        fm: dict[str, Any] = {"title": title, "description": desc, "uid": f"bet-{n:03d}", "track": tr.name,
                              "appetite": tr.appetite_max, "pods": [product],
                              "decision_by": next(iter(G.pod_holders(view, "bet-owner", product, self.now)), self.actor)}
        if tier is not None:
            fm["tier"] = tier
        puts: list[RenderedDoc] = []
        if idea is not None:
            fm["idea"] = idea.kb_id
            fm["relations"] = {"from_idea": idea.path}
            puts.append(self._upd(idea, {**self._state(idea, "promoted"), "bet": bet_id}))
        elif free:
            ipath = f"/ideas/IDEA-{n_idea:04d}.md"
            fm["idea"] = f"IDEA-{n_idea:04d}"
            fm["relations"] = {"from_idea": ipath}
            puts.append(self._idea_doc(n_idea, title, desc, {"product": product, "bet": bet_id}, None, state="promoted"))
        fm.update(extra)
        puts.insert(0, RenderedDoc(f"{folder}/bet.md", self._concept(bspec, fm, body or self._template_body(bspec))))
        msgs = [f"{bet_id} reservada na trilha {tr.name}; complete o corpo e rode `t0 gate aposta {bet_id}`"]
        if tr.name == "rapida":
            sspec = REGISTRY.type_named("Slice")
            sfm = {"title": title, "description": desc, "uid": f"bet-{n:03d}-slice-01", "bet": bet_id,
                   "repo": repo or "", "tier": tier if tier is not None else tr.tier_default}
            puts.append(RenderedDoc(f"{folder}/slices/01-{W.slug(title, 30)}.md", self._concept(sspec, sfm, RAPIDA_SLICE_BODY)))
            msgs.append("slice único criado: preencha atual, esperado, não muda e o teste")
        return Plan(knowledge=KnowledgeChange(branch, f"Aposta {bet_id}: {title}",
                                              f"PR da aposta de {bet_id} (trilha {tr.name}). Aprovar este PR é a decisão.",
                                              tuple(puts), (self.actor,)), messages_pt=tuple(msgs))

    def workspace(self) -> Any:
        """The workspace around cwd, else the one holding this KB (so `T0_KB` works from any cwd)."""
        from . import ws

        return ws.locate(Path.cwd()) or ws.locate(self.root)

    def _ws_product(self) -> str | None:
        w = self.workspace()
        return w.product if w else None

    def _bet(self, ref: str | None) -> Concept | Refusal:
        if not ref:
            from . import ws

            d = ws.detect(Path.cwd())
            ref = d.bet or d.story
        c = self.get(Ref(ref)) if ref else None
        bet = c if c is not None and c["type"] == "Bet" else (self.view().bet_of(c) if c is not None else None)
        return bet if bet is not None else Refusal((f"bet {ref!r} não encontrada no KB",))

    def _new_spec(self, *, ref, body, extra, **_: Any) -> Plan | Refusal:
        bet = self._bet(ref)
        if isinstance(bet, Refusal):
            return bet
        if bet["track"] == "rapida":
            return Refusal((f"{bet.kb_id} é da trilha rápida: não tem spec",))
        branch = self._bet_branch(bet.kb_id)
        if (r := self.checkout(branch)):
            return r
        bet = self._bet(bet.kb_id)
        if isinstance(bet, Refusal):
            return bet
        if self.view().spec_of(bet) is not None:
            return Plan(messages_pt=(f"{bet.kb_id} já tem spec.md",))
        spec = REGISTRY.type_named("Spec")
        fm = {"title": f"Spec da {bet.kb_id}: {bet['title']}", "description": str(bet["description"]),
              "uid": f"{bet.uid}-spec", "bet": bet.kb_id, "seams": [],
              "tier": bet["tier"] if isinstance(bet["tier"], int) else 1, "markers_open": 0, **extra}
        doc = RenderedDoc(bet_folder(bet.path) + "/spec.md", self._concept(spec, fm, body or self._template_body(spec)))
        return Plan(knowledge=KnowledgeChange(branch, f"Spec {bet.kb_id}", "Spec e slices no mesmo PR; aprovar é o gate spec.",
                                              (doc,), (Actor(str(bet["decision_by"])),)),
                    messages_pt=(f"spec criado; feche os [PRECISA ESCLARECER] e rode `t0 gate spec {bet.kb_id}`",))

    def _new_slice(self, *, ref, title, description, body, extra, repo, tier, depends_on, **_: Any) -> Plan | Refusal:
        bet = self._bet(ref)
        if isinstance(bet, Refusal):
            return bet
        if not title or not repo:
            return Refusal(("`t0 new slice <BET>` precisa de --title e --repo",))
        if bet["track"] == "rapida" and self.view().children(bet, "Slice"):
            return Refusal((f"{bet.kb_id} é rápida e já tem o slice único",))
        branch = self._bet_branch(bet.kb_id)
        if (r := self.checkout(branch)):
            return r
        bet = self._bet(bet.kb_id)
        if isinstance(bet, Refusal):
            return bet
        folder = bet_folder(bet.path)
        nn = self._next("Slice", folder=folder)
        spec = REGISTRY.type_named("Slice")
        fm = {"title": title, "description": description or title, "uid": f"{bet.uid}-slice-{nn:02d}", "bet": bet.kb_id,
              "repo": repo, "tier": tier if tier is not None else (bet["tier"] if isinstance(bet["tier"], int) else 1),
              "depends_on": list(depends_on), **extra}
        doc = RenderedDoc(f"{folder}/slices/{nn:02d}-{W.slug(title, 30)}.md", self._concept(spec, fm, body or self._template_body(spec)))
        return Plan(knowledge=KnowledgeChange(branch, f"Spec {bet.kb_id}", "Spec e slices no mesmo PR; aprovar é o gate spec.", (doc,)),
                    messages_pt=(f"slice {nn:02d} criado em {bet.kb_id}",))

    def _new_adr(self, *, title, description, body, extra, product, **_: Any) -> Plan | Refusal:
        if not title:
            return Refusal(("`t0 new adr` precisa de --title",))
        n = self._next("ADR")
        branch = self._branch_here_or(f"kb/{self.handle}/ADR-{n:04d}")
        if (r := self.checkout(branch)):
            return r
        folder = f"/products/{product}/adr" if product else "/methodology/adr"
        spec = REGISTRY.type_named("ADR")
        fm = {"title": title, "description": description or title, "uid": f"adr-{n:04d}", "number": n,
              "deciders": [self.actor], **extra}
        doc = RenderedDoc(f"{folder}/ADR-{n:04d}-{W.slug(title, 40)}.md", self._concept(spec, fm, body or self._template_body(spec)))
        return Plan(knowledge=KnowledgeChange(branch, f"ADR-{n:04d}: {title}", "ADR proposto.", (doc,)),
                    messages_pt=(f"ADR-{n:04d} proposto",))

    def _new_harness(self, *, title, description, body, extra, pattern, occurrence, **_: Any) -> Plan | Refusal:
        pattern = pattern or title
        if not pattern:
            return Refusal(("`t0 new harness` precisa de --pattern (o erro do agente em uma frase)",))
        same = next((c for c in self.view().of_type("Harness Item")
                     if c.state == "open" and W.slug(str(c["pattern"]), 200) == W.slug(pattern, 200)), None)
        n = int(same.kb_id[3:]) if same is not None else self._next("Harness Item")
        branch = self._branch_here_or(f"kb/{self.handle}/HI-{n:04d}")
        if same is not None:
            occ = list(same["occurrences"] or [])
            if not occurrence or occurrence in occ:
                return Plan(messages_pt=(f"{same.kb_id} já registra esse erro" + (f" e a ocorrência {occurrence}" if occurrence else ""),))
            if (r := self.checkout(branch)):
                return r
            same = self.view().resolve(Ref(same.kb_id))
            occ = list(same["occurrences"] or []) + [occurrence]
            msg = f"{same.kb_id}: {len(occ)}ª ocorrência" + ("; suba a escada do harness" if len(occ) >= 2 else "")
            return Plan(knowledge=KnowledgeChange(branch, f"{same.kb_id}: nova ocorrência", msg, (self._upd(same, {"occurrences": occ}),)),
                        messages_pt=(msg,))
        if (r := self.checkout(branch)):
            return r
        spec = REGISTRY.type_named("Harness Item")
        fm = {"title": title or pattern[:72], "description": description or pattern, "uid": f"hi-{n:04d}", "pattern": pattern,
              "occurrences": [occurrence] if occurrence else [], **extra}
        doc = RenderedDoc(f"/harness/HI-{n:04d}.md", self._concept(spec, fm, body or self._template_body(spec)))
        return Plan(knowledge=KnowledgeChange(branch, f"HI-{n:04d}: {title or pattern[:60]}", "Harness Item novo.", (doc,)),
                    messages_pt=(f"HI-{n:04d} aberto",))

    # ------------------------------------------------------------- idea prototype

    def idea_prototype(self, ref: str, verdict: str, prototype_ref: str | None) -> Plan | Refusal:
        c = self.get(Ref(ref))
        if c is None or c["type"] != "Idea":
            return Refusal((f"{ref} não é uma Idea do KB",))
        if verdict not in ("segue", "ajusta", "mata"):
            return Refusal(("--verdict é segue, ajusta ou mata",))
        if c.state in ("promoted", "killed") and not (c.state == "killed" and verdict == "mata"):
            return Refusal((f"{c.kb_id} está `{c.state}`",))
        if c["verdict"] == verdict and (prototype_ref is None or c["prototype_ref"] == prototype_ref):
            return Plan(messages_pt=(f"{c.kb_id} já tem o veredito {verdict}",))
        branch = self._branch_here_or(f"kb/{self.handle}/{c.kb_id}")
        if (r := self.checkout(branch)):
            return r
        c = self.view().resolve(Ref(c.kb_id))
        if c is None:
            return Refusal((f"{ref} não está no branch {branch}",))
        upd: dict[str, Any] = {"verdict": verdict, "decided_at": self.now, **self._state(c, "killed" if verdict == "mata" else "prototyped")}
        if prototype_ref:
            upd["prototype_ref"] = prototype_ref
        nxt = {"segue": f"próximo: `t0 new bet --track bet {c.kb_id}`", "ajusta": "ajuste e prototipe de novo, ou aposte",
               "mata": "ideia morta; o registro impede que volte sem fato novo"}[verdict]
        return Plan(knowledge=KnowledgeChange(branch, f"{c.kb_id}: protótipo {verdict}", f"Veredito do protótipo: {verdict}.",
                                              (self._upd(c, upd),)), messages_pt=(nxt,))

    # ------------------------------------------------------------- adr accept

    def adr_accept(self, ref: str) -> Plan | Refusal:
        """`t0 adr accept <ADR>`: knowledge-lane edit to `state: accepted`, proposed as a draft PR to the deciders."""
        c = self.get(Ref(ref))
        if c is None or c["type"] != "ADR":
            return Refusal((f"{ref} não é um ADR do KB",))
        if c.state == "accepted":
            return Plan(messages_pt=(f"{c.kb_id} já está `accepted`",))
        if not c.spec.states.allows(str(c.state), "accepted"):
            return Refusal((f"{c.kb_id} está `{c.state}`; só ADR `proposed` vira `accepted`",))
        short = c.kb_id.split("-", 2)
        branch = self._branch_here_or(f"kb/{self.handle}/{short[0]}-{short[1]}")
        if (r := self.checkout(branch)):
            return r
        c = self.view().resolve(Ref(ref))
        if c is None:
            return Refusal((f"{ref} não está no branch {branch}",))
        deciders = tuple(Actor(str(a)) for a in c["deciders"] or ())
        upd = {**self._state(c, "accepted"), "decided_at": self.now}
        return Plan(knowledge=KnowledgeChange(branch, f"{c.kb_id}: aceito", f"Aceite do {c.kb_id}. Aprovar este PR é a decisão.",
                                              (self._upd(c, upd),), deciders),
                    messages_pt=(f"{c.kb_id} `accepted` no PR" + (f"; aprovadores: {', '.join(deciders)}" if deciders else ""),))

    # ------------------------------------------------------------- gate

    def decide(self, gate_id: str, ref: Ref) -> G.GateDecision | Refusal:
        gate = REGISTRY.gate(gate_id)
        if gate is None:
            return Refusal((f"gate {gate_id!r} não existe; v0.1 tem aposta e spec (degrau é v0.2)",))
        c = self.get(ref)
        if c is None:
            return Refusal((f"{ref.raw} não encontrado no KB",))
        d = G.evaluate(self.view(), gate, c, now=self.now)
        return Refusal((d,)) if isinstance(d, str) else d

    def gate(self, gate_id: str, ref: Ref, *, ci: bool = False) -> Plan | Refusal:
        d = self.decide(gate_id, ref)
        if isinstance(d, Refusal):
            return d
        if ci:
            lines = d.lines_pt()
            return Plan(messages_pt=tuple(lines)) if d.ok else Refusal(tuple(lines))
        if d.already:
            return Plan(messages_pt=(f"{d.target.primary.kb_id} já está `{d.already}`",))
        if not d.ok:
            return Refusal(tuple(d.lines_pt()))
        bet = d.target.bet
        branch = self._bet_branch(bet.kb_id) if bet else self._branch_here_or(f"kb/{self.handle}/{gate_id}")
        if (r := self.checkout(branch)):
            return r
        d = self.decide(gate_id, ref)
        if isinstance(d, Refusal):
            return d
        if d.already:
            return Plan(messages_pt=(f"{d.target.primary.kb_id} já está `{d.already}` no branch {branch}",))
        if not d.ok:
            return Refusal(tuple(d.lines_pt()))
        puts = [self._upd(c, self._state(c, to)) for c, to in d.target.moves]
        body = "\n".join([f"Decisão `{gate_id}` de {d.target.primary.kb_id}. Aprovar este PR é a decisão.", ""]
                         + [f"- {l}" for l in d.lines_pt()])
        folder = bet_folder(d.target.primary.path)
        include = tuple(p for p in W.dirty(self.tree) if folder and ("/" + p).startswith(folder + "/")) if W.is_git(self.tree) else ()
        return Plan(knowledge=KnowledgeChange(branch, f"Gate {gate_id}: {d.target.primary.kb_id}", body, tuple(puts), d.approvers,
                                              include=tuple("/" + p for p in include)),
                    messages_pt=(f"decisão {gate_id} pronta no PR; aprovadores: {', '.join(d.approvers)}",))

    # ------------------------------------------------------------- records

    def _record(self, kind: EventKind, text: str, *, folder: str | None, fields: Mapping[str, Any],
                dedup: str | None = None, by: Actor | None = None) -> W.AddRecord:
        repo = os.environ.get("T0_REPO") or "kb"
        return W.new_record(kind, type_name="Step", fields=fields, body=text, actor=by or self.actor, handle=self.handle,
                            where={"repo": repo, **({"bet_folder": folder} if folder else {})}, dedup=dedup)

    def record(self, kind: EventKind, text: str, *, bet: Ref | None = None, story: str | None = None,
               refs: Sequence[str] = (), target: Ref | None = None, to: str | None = None) -> Plan | Refusal:
        from . import ws

        det = ws.detect(Path.cwd())
        bet_ref = bet.raw if bet else (det.bet or det.story)
        story = story or (det.story if not bet else None)
        bet_c = None
        if bet_ref:
            r = self._bet(bet_ref)
            if isinstance(r, Refusal):
                return r
            bet_c = r
        if kind is EventKind.KILL and bet_c is None:
            return Refusal(("`t0 log kill` precisa de --bet BET-NNN",))
        tgt = self.view().resolve(target) if target else None
        fields: dict[str, Any] = {"kind": kind.value, "bet": bet_c.kb_id if bet_c else None, "story": story,
                                  "refs": list(refs), "target": tgt.uid if tgt else None, "to": to}
        try:
            rec = self._record(kind, text, folder=bet_folder(bet_c.path) if bet_c else None, fields=fields)
        except W.SecretFound as e:
            return Refusal((str(e),))
        if kind is not EventKind.KILL:
            return Plan(records=(rec,), messages_pt=(f"{kind.value} registrado no spool; `t0 kb push` leva ao KB",))
        if bet_c.state in ("shipped", "killed"):
            return Refusal((f"{bet_c.kb_id} já está `{bet_c.state}`",))
        branch = self._bet_branch(bet_c.kb_id)
        if (r := self.checkout(branch)):
            return r
        bet_c = self._bet(bet_c.kb_id)
        if isinstance(bet_c, Refusal):
            return bet_c
        owner = Actor(str(bet_c["decision_by"] or self.actor))
        upd = self._upd(bet_c, self._state(bet_c, "killed"), f"## Kill\n\n{text}")
        return Plan(records=(rec,), knowledge=KnowledgeChange(branch, f"Kill {bet_c.kb_id}", f"Kill: {text}", (upd,), (owner,)),
                    messages_pt=(f"kill de {bet_c.kb_id} no PR; aprovar é a decisão de {owner}",))

    # ------------------------------------------------------------- slice / ci / ship

    def _slice(self, key: str) -> Concept | Refusal:
        c = self.view().resolve(Ref(key))
        if c is None or c["type"] not in ("Slice",):
            return Refusal((f"nenhum slice {key!r} no KB (chave Jira, BET-NNN/NN ou uid)",))
        return c

    def wip_limit(self) -> tuple[int, str]:
        p = self.view().at("/methodology/policies/wip.md")
        th = (p["thresholds"] or {}) if p is not None else {}
        n = th.get("slices_building_per_person") if isinstance(th, dict) else None
        return (int(n), "Policy wip") if isinstance(n, int) else (2, "padrão (Policy wip sem número)")

    def slice_dor(self, key: str) -> Plan | Refusal:
        s = self._slice(key)
        if isinstance(s, Refusal):
            return s
        view = self.view()
        bet = view.bet_of(s)
        probs = G.acceptance_problems(s)
        probs += [] if str(s["repo"] or "").strip() else ["falta `repo`"]
        probs += G.empty_sections(s, VERIFY)
        probs += [] if isinstance(s["tier"], int) else ["`tier` não é 0, 1 ou 2"]
        if bet is None or bet.state != "active":
            probs.append(f"bet `{bet.state if bet else '?'}`: a aposta não foi aprovada")
        elif bet["track"] == "rapida":
            probs += G.rapida_problems(s)
        else:
            sp = view.spec_of(bet)
            if sp is None or sp.state != "approved":
                probs.append(f"spec `{sp.state if sp else 'ausente'}`: o gate spec não passou")
            elif sp["markers_open"]:
                probs.append(f"spec com {sp['markers_open']} [PRECISA ESCLARECER]")
        if not s["jira"]:
            probs.append("sem chave Jira: o `t0 jira sync` grava depois do merge do spec")
        if s.state not in ("ready", "building"):
            probs.append(f"slice `{s.state}`")
        limit, src = self.wip_limit()
        mine = [c for c in view.of_type("Slice") if c.state == "building" and c["builder"] == self.actor and c.uid != s.uid]
        if len(mine) >= limit:
            probs.append(f"WIP: {self.actor} já tem {len(mine)} slice(s) em construção, limite {limit} ({src}); "
                         "PR esperando review vem antes de slice novo")
        if probs:
            return Refusal(tuple(f"DoR: {p}" for p in probs))
        return Plan(messages_pt=(f"DoR ok: {s['jira'] or s.kb_id} {s['title']} (WIP {len(mine) + 1}/{limit})",))

    def ci(self, key: str, *, pr: str, state: str, approvals: Sequence[str] = (), audit: str | None = None,
           author: str | None = None) -> Plan | Refusal:
        """`t0 ci <KEY|ref>`: CI evidence -> records kb-render folds.
        Slice or Harness Item: draft -> pr-opened; ready -> + ci-gate (needs .audit/<KEY>.tsv); merged -> + pr-merged
        (needs tier approvals). Decision-owned type (Bet, Spec, ADR...): merged decision PR -> pr-merged with the
        approvals, from which kb-render derives `verified`."""
        c = self.view().resolve(Ref(key))
        if state not in ("draft", "ready", "merged"):
            return Refusal(("--state é draft, ready ou merged",))
        by = Actor("process:t0-ci") if os.environ.get("CI") else self.actor
        if c is not None and c.spec is not None and c.spec.states and c.spec.states.owner is StateOwner.DECISION:
            return self._ci_decision(c, pr=pr, state=state, approvals=approvals, by=by)
        if c is None or c["type"] not in ("Slice", "Harness Item"):
            return Refusal((f"{key} não é slice, Harness Item nem decisão do KB",))
        on_behalf = Actor(author) if author and actor(author) else None
        folder = bet_folder(c.path)
        human = [a for a in approvals if a.startswith("human:")]
        if c["type"] == "Slice" and state == "ready":
            path = Path(audit or f".audit/{key}.tsv")
            if not path.is_file():
                return Refusal((f"DoD: falta {path} commitado no PR",))
        if c["type"] == "Slice" and state == "merged":
            tier = c["tier"] if isinstance(c["tier"], int) else 1
            bet = self.view().bet_of(c)
            need = {0: 0, 1: 1}.get(tier, 2)
            probs = [f"Tier {tier} pede {need} aprovação(ões) humana(s); veio {len(human)}"] if len(human) < need else []
            if tier == 2 and bet is not None and str(bet["decision_by"]) not in human:
                probs.append(f"Tier 2 pede o Bet Owner {bet['decision_by']} entre os aprovadores")
            if probs:
                return Refusal(tuple(probs))
        chain = {"draft": ["pr-opened"], "ready": ["pr-opened", "ci-gate"], "merged": ["pr-opened", "pr-merged"]}[state]
        if c["type"] == "Slice" and state == "merged" and c.state == "in-review":
            chain = ["pr-merged"]
        if c["type"] == "Harness Item":
            chain = ["pr-opened"] + (["pr-merged"] if state == "merged" else [])
        recs = []
        for k in chain:
            payload: dict[str, Any] = {"pr": pr}
            if k == "ci-gate":
                payload["audit"] = audit or f".audit/{key}.tsv"
            if k == "pr-merged":
                payload["approvals"] = human
            fields = {"kind": k, "target": c.uid, "story": c["jira"], "refs": [pr], "payload": payload,
                      "to": "in-review" if k == "ci-gate" else None, "on_behalf_of": on_behalf if k == "pr-opened" else None}
            recs.append(self._record(EventKind(k), f"{key}: {k} {pr}", folder=folder, fields=fields,
                                     dedup=f"{k}:{c.uid}:{pr}", by=by))
        msgs = [f"{key}: {', '.join(chain)} ({pr})"]
        if c["type"] == "Slice" and state == "merged":
            bet = self.view().bet_of(c)
            rest = [s for s in self.view().children(bet, "Slice") if s.uid != c.uid and s.state != "done"] if bet else []
            if bet is not None and not rest:
                msgs.append(f"último slice da {bet.kb_id}: rode `t0 bet ship {bet.kb_id}`")
        return Plan(records=tuple(recs), messages_pt=tuple(msgs))

    def _decision_approvers(self, c: Concept) -> tuple[Actor, ...]:
        """Who must approve the PR that moved `c` to its current state: the gate's approvers, the Bet Owner for a kill."""
        sm = c.spec.states
        gate_id = next((t.via_gate for t in sm.transitions if t.to == c.state and t.via_gate), None)
        if gate_id is not None:
            gate = REGISTRY.gate(gate_id)
            t = G.resolve_target(self.view(), gate, c)
            return () if isinstance(t, str) else G.resolve_approvers(self.view(), gate, t, self.now)[0]
        if c["type"] == "Bet" and c.state == "killed" and c["decision_by"]:
            return (Actor(str(c["decision_by"])),)
        return ()

    def _ci_decision(self, c: Concept, *, pr: str, state: str, approvals: Sequence[str], by: Actor) -> Plan | Refusal:
        if state != "merged":
            return Plan(messages_pt=(f"{c.kb_id}: PR de decisão só vira registro no merge",))
        human = [a for a in approvals if a.startswith("human:")]
        need = self._decision_approvers(c)
        probs = [f"falta a aprovação de {a}" for a in need if a not in human] or ([] if human else ["decisão pede uma aprovação humana"])
        if probs:
            return Refusal(tuple(probs))
        rec = self._record(EventKind.PR_MERGED, f"{c.kb_id}: decisão mergeada {pr}", folder=bet_folder(c.path),
                           fields={"kind": EventKind.PR_MERGED.value, "target": c.uid, "refs": [pr],
                                   "payload": {"pr": pr, "approvals": human}},
                           dedup=f"pr-merged:{c.uid}:{pr}", by=by)
        return Plan(records=(rec,), messages_pt=(f"{c.kb_id}: `verified` de {', '.join(human)} via kb-render",))

    def bet_ship(self, ref: str) -> Plan | Refusal:
        bet = self._bet(ref)
        if isinstance(bet, Refusal):
            return bet
        if bet.state == "shipped":
            return Plan(messages_pt=(f"{bet.kb_id} já está shipped",))
        if bet.state != "active":
            return Refusal((f"{bet.kb_id} está `{bet.state}`; só bet ativa vai para shipped",))
        open_ = [s for s in self.view().children(bet, "Slice") if s.state != "done"]
        if open_ or not self.view().children(bet, "Slice"):
            return Refusal(tuple([f"{s.kb_id} está `{s.state}`" for s in open_] or ["bet sem slices"]))
        branch = self._bet_branch(bet.kb_id)
        if (r := self.checkout(branch)):
            return r
        view = self.view()
        bet = self._bet(bet.kb_id)
        if isinstance(bet, Refusal):
            return bet
        if bet.state == "shipped":
            return Plan(messages_pt=(f"{bet.kb_id} já está shipped no branch {branch}",))
        puts = [self._upd(bet, self._state(bet, "shipped"))]
        sp = view.spec_of(bet)
        if sp is not None and sp.state == "approved":
            puts.append(self._upd(sp, self._state(sp, "frozen")))
        acceptance = list(section(sp.doc.body, ACCEPTANCE).bullets) if sp is not None else [a for s in view.children(bet, "Slice") for a in section(s.doc.body, ACCEPTANCE).bullets]
        product = view.at(bet.path.split("/bets/")[0] + "/product.md")
        if product is not None:
            head = f"### {bet.kb_id} {bet['title']}"
            add = "" if "## Spec vivo" in product.doc.body else "## Spec vivo\n\n"
            block = add + head + "\n\n" + "\n".join(f"- {a}" for a in acceptance) + "\n"
            if head not in product.doc.body:
                puts.append(RenderedDoc(product.path, product.doc.raw.rstrip("\n") + "\n\n" + block))
        return Plan(knowledge=KnowledgeChange(branch, f"Ship {bet.kb_id}", "Último slice em done: bet shipped, spec congelado, spec vivo atualizado.",
                                              tuple(puts), (Actor(str(bet["decision_by"])),)),
                    messages_pt=(f"{bet.kb_id} shipped; spec vivo atualizado em {product.path if product else '(sem product.md)'}",))

    # ------------------------------------------------------------- propose / render / apply

    def propose(self, msg: str) -> Plan | Refusal:
        """Commit hand edits as a knowledge PR. In a worktree: that branch. From the main clone: its edits move to a
        new branch (the bet's when they touch one bet folder); with a clean main, the one worktree that has edits."""
        if not W.is_git(self.root):
            return Refusal(("`t0 kb propose` precisa de um KB em git",))
        branch = W.current_branch(self.tree)
        move: list[str] = []
        if self.tree == self.root:
            if branch not in (None, W.MAIN):
                return Refusal((f"o clone principal do KB está em {branch}; volte com `git -C {self.root} switch main`",))
            move = W.dirty(self.root)
            if move:
                bets = {m.group(1) for p in move if (m := re.search(r"/bets/(BET-\d+)/", "/" + p))}
                branch = self._bet_branch(bets.pop()) if len(bets) == 1 else f"kb/{self.handle}/{W.slug(msg, 40)}"
                if W.ref_exists(self.root, f"refs/heads/{branch}"):
                    return Refusal((f"mudanças sem commit no clone principal do KB e o branch {branch} já existe; mova-as "
                                    f"para o worktree {W.worktree_root(self.root) / branch} e rode `t0 kb propose` de lá",))
            else:
                edited = [co for co in W.checkouts(self.root) if W.dirty(co.path)]
                if not edited:
                    return Plan(messages_pt=("nada para propor: árvore limpa no main e nos worktrees",))
                if len(edited) > 1:
                    return Refusal(("mudanças em mais de um worktree; rode `t0 kb propose` de dentro de um deles: "
                                    + ", ".join(str(co.path) for co in edited),))
                self.tree, branch = edited[0].path, edited[0].branch
                self.reload()
        if branch in (None, W.MAIN):
            return Refusal((f"{self.tree} não está num branch de conhecimento",))
        changed = W.dirty(self.tree)
        rep = self.check(Level.L1, changed_from=W.base_ref(self.tree))
        touched = {"/" + p for p in changed}
        if not move:
            touched |= {"/" + n for n in W.git(self.tree, "diff", "--name-only", W.base_ref(self.tree)).splitlines()}
        errs = [f for f in rep.findings if f.severity is Severity.ERROR and (f.path in touched or f.rule.startswith(("L0.", "LANE.")))]
        if errs:
            return Refusal(tuple(f"{f.rule} {f.path}: {f.message_pt}" for f in errs))
        if move and not self.dry and (r := self._move_main_edits(move, branch)):
            return r
        return Plan(knowledge=KnowledgeChange(branch, msg, f"Proposta de conhecimento: {msg}", (), commit_all=True),
                    messages_pt=tuple(f"incluído: /{p}" for p in changed) or ("sem mudança nova; PR do branch",))

    def _move_main_edits(self, changed: Sequence[str], branch: str) -> Refusal | None:
        """Carry the main clone's edits to a new branch's worktree and restore them on main."""
        try:
            self._checkout = W.checkout(self.root, branch)
        except W.ApplyError as e:
            return Refusal((str(e),))
        dst = self._checkout.path
        for rel in changed:
            src, out = self.root / rel, dst / rel
            if src.is_file():
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(src.read_bytes())
            elif out.is_file():
                out.unlink()
        tracked = set(W.git(self.root, "ls-files", "--", *changed).splitlines())
        if tracked:
            W.git(self.root, "checkout", "-q", "--", *sorted(tracked))
        for rel in set(changed) - tracked:
            (self.root / rel).unlink(missing_ok=True)
            for d in (self.root / rel).parents:
                if d == self.root or any(d.iterdir()):
                    break
                d.rmdir()
        self.tree = dst
        self.reload()
        return None

    def render(self) -> Plan:
        docs = [d for d in read_docs(self.root) if isinstance(d, Document)]
        view = fold(docs, kb_sha=self.sha(self.root))
        derived = materialize(view, docs)
        from . import gen

        ctx = gen.GenContext(self.root, gen.Scope.KB)
        rendered = gen.generate(ctx)
        drift = {d.path for d in gen.check_drift(ctx, rendered)}
        extra = tuple(RenderedDoc("/" + p, t) for p, t in rendered.items() if p in drift)
        puts = derived.puts + extra
        if not puts:
            return Plan(messages_pt=("derivados em dia",))
        return Plan(derived=W.derived_change(puts))

    def apply(self, plan: Plan | Refusal, *, mode: ApplyMode = ApplyMode.LOCAL) -> Applied:
        if isinstance(plan, Refusal):
            raise ValueError("; ".join(plan.reasons_pt))
        known = frozenset(e.dedup for e in self.view().events)
        try:
            out = W.apply(plan, mode=mode, kb_dir=self.root, known_dedup=known)
        finally:
            if self._ids is not None:
                self._ids.close()
                self._ids = None
        self.reload()
        return out

    def records_mode(self) -> str:
        p = self.view().at("/methodology/policies/records-lane.md")
        return str(p["mode"]) if p is not None and p["mode"] in ("batch", "auto") else "batch"

    def push(self, *, if_due: bool = False) -> tuple[Applied, list[str]]:
        sp = W.spool_dir(self.root)
        if if_due and sp.is_dir():
            files = list(sp.rglob("*.md"))
            import time

            if not files or min(time.time() - f.stat().st_mtime for f in files) < 600:
                return Applied(), ["spool recente; push depois"]
        landed = frozenset(d.path.value for d in self.docs() if isinstance(d, Document))
        return W.push_spool(kb_dir=self.root, handle=self.handle, mode=self.records_mode(), landed=landed)
