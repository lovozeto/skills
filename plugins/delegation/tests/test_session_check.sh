#!/usr/bin/env bash
# Seam: the SessionStart sensor's output.
source "$(dirname "$0")/lib.sh"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
mkdir -p "$T/bin" "$T/home/.agents/skills/prompt-master"
for b in python3 curl ollama opencode; do ln -s "$(command -v python3)" "$T/bin/$b"; done
ln -s "$(command -v find)" "$T/bin/find"; ln -s "$(command -v sed)" "$T/bin/sed"; ln -s "$(command -v head)" "$T/bin/head"

out="$(HOME="$T/home" PATH="$T/bin" /bin/bash "$PLUGIN/hooks/session_check.sh")"
expect_eq "all present -> silent" "$out" ""

rm "$T/bin/opencode"; rmdir "$T/home/.agents/skills/prompt-master"
out="$(HOME="$T/home" PATH="$T/bin" /bin/bash "$PLUGIN/hooks/session_check.sh")"
expect_contains "names missing opencode" "$out" "brew install opencode"
expect_contains "names missing prompt-master" "$out" "npx skills add nidhinjs/prompt-master"
expect_contains "is SessionStart context" "$out" '"hookEventName":"SessionStart"'
finish
