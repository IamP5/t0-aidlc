#!/bin/sh
# t0 inside the eval sandbox: the toolkit lives in <workspace>/.t0/lib, beside this .t0/bin.
d=$(cd "$(dirname "$0")/.." && pwd)
PYTHONPATH="${T0_LIB:-$d/lib}" exec /opt/homebrew/bin/python3 -m t0.cli "$@"
