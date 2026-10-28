# Request from core to edges: five follow-ups after the v2 table

Core is in place (`profile/table.py` v2, `kb.py`, `write.py`, `cli.py`). These touch edge files, so they are yours.

1. **Tracks in `profile.md`.** `profile/table.py` exports `TRACKS` (rapida, bet) and keeps `BET_TYPES = TRACKS` only
   so `gen.profile_md` keeps importing. Please import `TRACKS`, rename the section `## Trilhas` with columns
   `trilha | gates | artefatos | apetite máximo | tier padrão | eval`, and tell core to drop the alias.
2. **Slice branch name (DESIGN §2, coordinator decision).** `ws.slice_start` builds `bet/<BET>/<KEY>-<slug>`.
   The contract is now `<KEY>-<slug>` in the product repo (KB work stays on `bet/BET-NNN/<handle>`). `BRANCH_RE`
   and `detect` need the same change: from a `<KEY>-slug` branch the story is the key, and the bet comes from
   `.t0/bet.json` or `KB.get(Ref(KEY))` (a Slice; `view.bet_of` gives its bet).
3. **`hooks.derived_keys`** can now call `REGISTRY.derived_keys(REGISTRY.type_named(name))` (same result: render keys
   plus decision-owned `state`/`verified`). `REGISTRY.render_keys` is the narrower kb-render set.
4. **`mcp_server.kb_record`.** `KB.record` returns `Plan | Refusal` (unknown bet, kill without bet, secret).
   `KB.apply(Refusal)` raises `ValueError` with the pt-BR reasons. Please turn a Refusal into
   `ToolError("recusado: ...")` before calling `apply`.
5. **`tracker.sync.plan_sync`** plans CREATE for an item whose KB already has `jira:` when the tracker cannot find it
   (a fresh `file:` tracker against `okf-template` re-creates BET-002 and the fold then reports
   `jira-key-changed`). A CONFLICT action ("KB tem EXE-21, o Jira não acha") is the safer plan there.
