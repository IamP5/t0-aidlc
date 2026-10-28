#!/bin/sh
# Plugin hook launcher. Finds t0 on PATH, or pinned in a workspace at .t0/bin/t0 (walking up from cwd).
# On session start it exports that bin dir, and T0_KB=<workspace>/kb when that dir exists, through
# CLAUDE_ENV_FILE, so the agent's shell finds `t0` and the KB even after it cds out of the workspace.
# With no t0 installed the hooks are a no-op with a warning, the same as a missing command.
event="$1"; shift
pinned=""
workspace=""
d=$PWD
while [ "$d" != "/" ]; do
  if [ -z "$workspace" ] && [ -f "$d/.t0/workspace.json" ]; then workspace="$d"; fi
  if [ -x "$d/.t0/bin/t0" ]; then pinned="$d/.t0/bin"; workspace="${workspace:-$d}"; break; fi
  d=$(dirname "$d")
done
if [ -n "$pinned" ]; then t0="$pinned/t0"; else t0=$(command -v t0 || true); fi
if [ -z "$t0" ]; then
  echo "t0 não está instalado: os hooks do plugin t0 estão desligados (rode t0 doctor)" >&2
  exit 0
fi
if [ "$event" = "session-start" ] && [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  if [ -n "$pinned" ]; then echo "export PATH=\"$pinned:\$PATH\"" >> "$CLAUDE_ENV_FILE"; fi
  if [ -n "$workspace" ] && [ -d "$workspace/kb" ]; then echo "export T0_KB=\"$workspace/kb\"" >> "$CLAUDE_ENV_FILE"; fi
fi
exec "$t0" hook "$event" "$@"
