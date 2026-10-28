#!/bin/sh
# Instala a CLI t0 a partir deste repo e roda `t0 install`.
# Uso: ./install.sh --kb <remote do KB> [--handle H] [--product P ...] [--link]
# --link: CLI editável e plugin carregado direto deste clone (~/.claude/skills/t0), sem marketplace;
# um git pull aqui atualiza os dois.
set -eu

here=$(cd "$(dirname "$0")" && pwd -P)

die() {
    echo "install.sh: $*" >&2
    exit 1
}

command -v git >/dev/null 2>&1 || die "precisa de git"
command -v python3 >/dev/null 2>&1 || die "precisa de python3 3.11 ou mais novo"
python3 -c 'import sys; sys.exit(sys.version_info < (3, 11))' || die "precisa de python3 3.11 ou mais novo (achei $(python3 -V 2>&1))"

editable=
for arg in "$@"; do
    [ "$arg" = "--link" ] && editable=--editable
done

if command -v uv >/dev/null 2>&1; then
    uv tool install --force $editable "$here/toolkit"
    bindir=$(uv tool dir --bin)
elif command -v pipx >/dev/null 2>&1; then
    pipx install --force $editable "$here/toolkit"
    bindir=$(pipx environment --value PIPX_BIN_DIR)
else
    die "instale o uv (https://docs.astral.sh/uv/) ou o pipx e rode de novo"
fi

t0="$bindir/t0"
[ -x "$t0" ] || die "a instalação não deixou $t0"
if [ "$(command -v t0 || true)" != "$t0" ]; then
    echo "install.sh: ponha $bindir no começo do PATH (uv tool update-shell ou pipx ensurepath); os hooks chamam \`t0\`" >&2
fi

exec "$t0" install --plugin-source "$here" "$@"
