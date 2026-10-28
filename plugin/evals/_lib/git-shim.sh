#!/bin/sh
# git inside the eval sandbox: a relocated Apple git in <workspace>/.t0/git.
d=$(cd "$(dirname "$0")/.." && pwd)
GIT_EXEC_PATH="$d/git/libexec/git-core" GIT_TEMPLATE_DIR="$d/git/share/git-core/templates" exec "$d/git/bin/git" "$@"
