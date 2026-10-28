#!/usr/bin/env bash
# Run every test of the plugin. Exit 0 when all pass.
set -uo pipefail
D="$(cd "$(dirname "$0")" && pwd)"; rc=0
for t in "$D"/test_*.sh; do bash "$t" || rc=1; done
for t in "$D"/test_*.py; do
  if out="$(python3 -W ignore "$t" 2>&1)"; then echo "$(basename "$t"): OK"; else echo "$out" | tail -5; rc=1; fi
done
exit $rc
