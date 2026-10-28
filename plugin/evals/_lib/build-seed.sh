#!/usr/bin/env bash
# Builds .eval/seed: the t0 toolkit installed for the eval sandbox's python, plus one workspace per pod
# (kb/ from okf-template with the pod's repos registered, the repo clones, .t0/workspace.json, .t0/bin/t0, .t0/bin/git).
# Run before `claude plugin eval`; case scaffolds copy a workspace from here.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
SEED="$ROOT/.eval/seed"
PY=/opt/homebrew/bin/python3
rm -rf "$SEED" && mkdir -p "$SEED"
# The eval sandbox can't read Xcode, so /usr/bin/git fails there: ship a relocated copy.
XD=/Applications/Xcode.app/Contents/Developer
mkdir -p "$SEED/git/bin" "$SEED/git/libexec" "$SEED/git/share"
cp "$XD/usr/bin/git" "$SEED/git/bin/" && cp -R "$XD/usr/libexec/git-core" "$SEED/git/libexec/" && cp -R "$XD/usr/share/git-core" "$SEED/git/share/"
"$PY" -m pip install --quiet --target "$SEED/t0lib" "$ROOT/toolkit"
t0() { PYTHONPATH="$SEED/t0lib" "$PY" -m t0.cli "$@"; }

t0 kb init "$SEED/kb" >/dev/null
"$PY" - "$SEED/kb" <<'PYEOF'
import re, sys
from pathlib import Path
kb = Path(sys.argv[1])
pods = {
  "dev-tooling": [("t0-harness", "harness de agente: AGENTS.md, issues como estado, skills"), ("springboot-plugin", "skills do Copilot para Java 25 e Spring Boot 4")],
  "paco": [("aidlc-local-e2e", "repo descartável para e2e local de AI-DLC")],
  "portal-metricas": [("quicklist-angular", "app Angular 17 de checklists, base do portal")],
}
for pod, repos in pods.items():
    ws = kb / "products" / pod / "workspace.md"
    block = "\n".join(f"    - {{ name: {n}, url: \"https://github.com/IamP5/{n}\", role: \"{r}\", kind: app, optional: false, tier: 1, depends_on: [] }}" for n, r in repos)
    t = ws.read_text().replace("  repos: []", "  repos:\n" + block)
    if pod == "dev-tooling":
        t = t.replace("  jira_project: null", "  jira_project: SBP")
    ws.write_text(t)
    prod = kb / "products" / pod / "product.md"
    t = prod.read_text()
    t = re.sub(r"^repos: \[.*\]$", "repos: [" + ", ".join(n for n, _ in repos) + "]", t, flags=re.M)
    prod.write_text(t)
# The eval user (sandbox handle = $USER) is a Builder and the Bet Owner of the three real pods.
import os
h = os.environ.get("USER", "dev")
(kb / "team/people" / f"{h}.md").write_text(f"""---
type: Person
title: "{h}"
description: "Bet Owner dos pods dev-tooling, paco e portal-metricas no KB de avaliação."
uid: person-{h}
owner: human:{h}
tags: [pessoa, eval]
generated: {{ by: human:{h}, at: 2026-10-28T09:00:00-03:00 }}
handle: {h}
pods: [dev-tooling, paco, portal-metricas]
junior: false
state: active
status: stable
---

# {h}

Bet Owner dos três pods no KB de avaliação.
""")
bo = kb / "team/roles/bet-owner.md"
t = bo.read_text()
t = re.sub(r"^holders: \[(.*)\]$", lambda m: f"holders: [{m.group(1)}, human:{h}]" if m.group(1) else f"holders: [human:{h}]", t, flags=re.M) if re.search(r"^holders:", t, re.M) else t.replace("\n---\n", f"\nholders: [human:{h}]\n---\n", 1)
bo.write_text(t)
PYEOF
git -C "$SEED/kb" init -q -b main
git -C "$SEED/kb" add -A
git -C "$SEED/kb" -c user.email=eval@t0 -c user.name=eval commit -qm "kb seed"

for pod in dev-tooling paco portal-metricas; do
  W="$SEED/ws-$pod"; mkdir -p "$W/.t0/bin"
  cp -R "$SEED/kb" "$W/kb"
  repos=$(PYTHONPATH="$SEED/t0lib" "$PY" -c "from pathlib import Path;from t0.ws import read_manifest;print(' '.join(r.name for r in read_manifest(Path('$W/kb'),'$pod').repos))")
  for r in $repos; do cp -R "$ROOT/.eval/repos/$r" "$W/$r"; git -C "$W/$r" remote set-url --push origin no-push://disabled; done
  printf '{"product": "%s", "repos": []}\n' "$pod" > "$W/.t0/workspace.json"
  cp "$ROOT/plugin/evals/_lib/t0-shim.sh" "$W/.t0/bin/t0"
  cp "$ROOT/plugin/evals/_lib/git-shim.sh" "$W/.t0/bin/git"; chmod +x "$W/.t0/bin/"*
  cp "$ROOT/plugin/evals/_lib/CLAUDE.md" "$W/CLAUDE.md"
  (cd "$W" && T0_LIB="$SEED/t0lib" ./.t0/bin/t0 context --format agents > AGENTS.md 2>/dev/null || true)
done
echo "seed ok: $SEED"
