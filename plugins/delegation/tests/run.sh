#!/usr/bin/env bash
# Run every test of the plugin. Exit 0 when all pass.
set -uo pipefail
D="$(cd "$(dirname "$0")" && pwd)"; rc=0
for t in "$D"/test_*.sh; do bash "$t" || rc=1; done
for t in "$D"/test_*.py; do python3 "$t" 2>&1 | tail -1 | sed "s|^|$(basename "$t"): |"; python3 "$t" >/dev/null 2>&1 || rc=1; done
bash "$D/../bench/code/selftest.sh" >/dev/null && echo "bench selftest: ok" || { echo "bench selftest: FAILED"; rc=1; }
exit $rc
