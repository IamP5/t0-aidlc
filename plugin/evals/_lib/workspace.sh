#!/usr/bin/env bash
# Case scaffold helper: `source "$(dirname "$0")/../_lib/workspace.sh" <pod>` copies the seed workspace for <pod>
# into the current directory and installs t0 inside it.
set -euo pipefail
_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
_SEED="$_ROOT/.eval/seed"
_PY=/opt/homebrew/bin/python3
[ -d "$_SEED/ws-$1" ] || { echo "rode plugin/evals/_lib/build-seed.sh antes" >&2; exit 1; }
cp -R "$_SEED/ws-$1/." .
mkdir -p .t0 && cp -R "$_SEED/t0lib" .t0/lib && cp -R "$_SEED/git" .t0/git
export PATH="$PWD/.t0/bin:$PATH"
# Same handle the agent gets inside the sandbox (no git user.name there, so t0 falls back to $USER).
export T0_HANDLE="${USER:-dev}"
# Identity for the KB and repo commits, set per repository (never --global: the scaffold runs as the real user).
for _r in kb */; do [ -d "$_r/.git" ] || [ -d "$_r.git" ] || continue; git -C "$_r" config user.email eval@t0; git -C "$_r" config user.name eval; done

# The human approval of a knowledge PR, with no forge: merge the KB branch into main.
approve() {
  local b; b=$(git -C kb branch --show-current)
  [ "$b" = main ] && return 0
  git -C kb checkout -q main && git -C kb merge -q --no-ff -m "aprovado: $b" "$b"
}
t0q() { ./.t0/bin/t0 "$@" >/dev/null; }

# IDEA-0004 in dev-tooling, prototyped with verdict segue.
state_idea() {
  t0q new idea --product dev-tooling --title "Flag --version no CLI do springboot-plugin" \
    --description "O CLI do springboot-plugin não diz qual versão está instalada; quem abre issue não sabe o que rodou."
  approve
}
state_prototyped() {
  state_idea
  t0q idea prototype IDEA-0004 --verdict segue --ref "springboot-plugin@proto/IDEA-0004:scripts/cli.mjs"
  approve
}
# BET-003 active (aposta approved), track bet, repo springboot-plugin.
state_bet() {
  state_prototyped
  t0q new bet --track bet IDEA-0004 --repo springboot-plugin --tier 1 --set appetite=P3D \
    --set "hypothesis=Com --version, issues chegam com a versão e a triagem cai pela metade." \
    --set "kill_criteria=Se ninguém usar a flag em 2 semanas, remove."
  t0q gate aposta BET-003
  approve
}
# BET-003 with an approved spec (copied fixture) and slice SBP-2 ready.
state_spec() {
  state_bet
  local d=kb/products/dev-tooling/bets/BET-003
  git -C kb checkout -q -B bet/BET-003/$T0_HANDLE
  cp "$_ROOT/plugin/evals/_lib/fixtures/spec-version.md" "$d/spec.md"
  t0q new slice BET-003 --repo springboot-plugin --tier 1 --title "Flag --version" \
    --body-file "$_ROOT/plugin/evals/_lib/fixtures/slice-version.md"
  git -C kb add -A && git -C kb commit -qm "spec + slice" || true
  t0q gate spec BET-003
  approve
  mkdir -p .t0/jira && t0q jira sync --tracker file:.t0/jira --apply
  approve_records
}
# Records lane approval with no forge: push the spool, merge the daily batch branch, then kb-render.
approve_records() {
  t0q kb push
  local r; r=$(git -C kb branch --list 'rec/*' --format='%(refname:short)' | tail -1)
  [ -n "$r" ] && git -C kb merge -q --no-ff -m "registros: $r" "$r"
  t0q kb render
}

# BET-003 active, its spec written on the bet branch, not yet approved (bet-slice picks up from here).
state_bet_with_spec_draft() {
  state_bet
  git -C kb checkout -q -B bet/BET-003/$T0_HANDLE
  cp "$_ROOT/plugin/evals/_lib/fixtures/spec-version.md" kb/products/dev-tooling/bets/BET-003/spec.md
  git -C kb add -A && git -C kb commit -qm "spec da BET-003"
}
# SBP-2 built on its branch, with a planted defect: --help does not list --version.
state_built() {
  state_spec
  local r=springboot-plugin
  git -C $r checkout -q -b SBP-2-flag-version
  "$_PY" - "$r/scripts/cli.mjs" <<'PYEOF'
import sys; p=sys.argv[1]; s=open(p).read()
s=s.replace("help: { type: 'boolean', short: 'h' }", "help: { type: 'boolean', short: 'h' }, version: { type: 'boolean' }")
s=s.replace("  if (!command || values.help) { console.log(help); return; }",
 "  if (values.version) { const pkg = JSON.parse(await (await import('node:fs/promises')).readFile(new URL('../package.json', import.meta.url))); console.log(JSON.stringify({ version: pkg.version })); return; }\n  if (!command || values.help) { console.log(help); return; }")
open(p,'w').write(s)
PYEOF
  cat > $r/tests/version.test.mjs <<'JS'
import test from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
test('--version prints the package version', () => {
  const out = JSON.parse(execFileSync('node', ['scripts/cli.mjs', '--version'], { encoding: 'utf8' }));
  assert.equal(out.version, JSON.parse(readFileSync('package.json', 'utf8')).version);
});
JS
  mkdir -p $r/.audit && printf 'ts\tphase\tdecision\twhy\tevidence\tresult\n2026-10-28T12:00:00Z\tbuild\t--version lê package.json em runtime\tspec\ttests/version.test.mjs\tok\n' > $r/.audit/SBP-2.tsv
  git -C $r add -A && git -C $r -c user.email=eval@t0 -c user.name=eval commit -qm "SBP-2: flag --version"
}
# A raw daily-pod transcript with PII, as the user would hand it over.
state_transcript() {
  mkdir -p notes && cat > notes/daily-pod.txt <<'TXT'
[09:31] Ana: bom, a BET-003 tá andando. O CPF do cliente de teste é 123.456.789-09, me manda no ana.souza@banco.com.br se precisar.
[09:32] Caio: decidimos que a versão vem do package.json em runtime, nada de build-time.
[09:33] Dani: ideia: o --version podia mostrar também a versão do Java detectado.
[09:34] Ana: fora do registro: o fornecedor atrasou de novo.
[09:35] Caio: bloqueio, o review do SBP-2 tá parado faz dois dias, alguém pega?
TXT
}
# HI-0002 accepted in harness health, no PR yet: the agent forgets `npm run validate` and the catalog drifts.
# The past mistake is a real commit in springboot-plugin history, so harness-fix can prove its check against it.
state_hi() {
  local r=springboot-plugin
  "$_PY" - "$r" <<'PYEOF'
import json, sys, pathlib
root = pathlib.Path(sys.argv[1])
f = next(p for p in sorted((root / "catalog").rglob("*.json")))
d = json.loads(f.read_text())
def poison(o):
    if isinstance(o, dict):
        for k in list(o):
            if isinstance(o[k], str) and k in ("id", "name"):
                o[k] = ""
                return True
            if poison(o[k]): return True
    if isinstance(o, list):
        for x in o:
            if poison(x): return True
    return False
poison(d)
f.write_text(json.dumps(d, indent=2) + "\n")
print(f)
PYEOF
  git -C $r add -A && git -C $r commit -qm "catalog: ajusta entrada (sem rodar validate)"
  local bad; bad=$(git -C $r rev-parse --short HEAD)
  git -C $r revert --no-edit HEAD >/dev/null
  t0q new harness --title "Agente esquece npm run validate antes do PR" \
    --description "PRs do springboot-plugin chegaram com o catálogo fora do schema porque o agente não rodou npm run validate." \
    --pattern "PR que mexe em catalog/ sem rodar npm run validate" --occurrence "springboot-plugin@$bad" \
    --set accepted=true
  approve
  approve_records
}
