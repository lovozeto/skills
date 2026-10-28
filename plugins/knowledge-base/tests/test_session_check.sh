#!/usr/bin/env bash
# Seam: the SessionStart sensor's output.
source "$(dirname "$0")/lib.sh"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
mkdir -p "$T/bin"

out="$(PATH="$T/bin" /bin/bash "$PLUGIN/hooks/session_check.sh")"
expect_contains "kb missing -> names the fix" "$out" "kb CLI is not on PATH"
expect_contains "is SessionStart context" "$out" '"hookEventName":"SessionStart"'
/usr/bin/python3 -c 'import json,sys; json.loads(sys.argv[1])' "$out" && pass || fail "output is valid JSON"

printf '#!/bin/sh\nexit 0\n' > "$T/bin/kb"; chmod +x "$T/bin/kb"
out="$(PATH="$T/bin" /bin/bash "$PLUGIN/hooks/session_check.sh")"
expect_eq "kb present -> silent" "$out" ""
finish
