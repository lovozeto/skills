#!/usr/bin/env bash
# Preflight dependency check for the inspecting-photo-archives skill.
#
# Prints a JSON object describing which tools are available and, when something
# is missing, the exact Homebrew command that would install it.
#
# This script NEVER installs anything. Installing changes the user's system, so
# it is gated on explicit confirmation in SKILL.md.
#
# Exit codes: 0 = all required tools present · 3 = something is missing.

set -uo pipefail

have() {
  if command -v "$1" >/dev/null 2>&1; then echo true; else echo false; fi
}

exiftool_ok=$(have exiftool)   # required: reads photo AND video metadata
ffprobe_ok=$(have ffprobe)     # required for video: identifies the codec inside a container
python3_ok=$(have python3)     # required: runs summarize_scan.py
brew_ok=$(have brew)           # needed only to install the missing ones
sips_ok=$(have sips)           # ships with macOS; weak fallback if exiftool is absent

missing=()
[ "$exiftool_ok" = false ] && missing+=("exiftool")
[ "$ffprobe_ok" = false ] && missing+=("ffmpeg")

printf '{\n'
printf '  "exiftool": %s,\n' "$exiftool_ok"
printf '  "ffprobe": %s,\n'  "$ffprobe_ok"
printf '  "python3": %s,\n'  "$python3_ok"
printf '  "sips": %s,\n'     "$sips_ok"
printf '  "brew": %s,\n'     "$brew_ok"

printf '  "missing": ['
first=true
for m in ${missing[@]+"${missing[@]}"}; do
  if [ "$first" = true ]; then first=false; else printf ', '; fi
  printf '"%s"' "$m"
done
printf '],\n'

if [ ${#missing[@]} -gt 0 ]; then
  printf '  "install_command": "brew install %s"\n' "${missing[*]}"
else
  printf '  "install_command": null\n'
fi
printf '}\n'

[ ${#missing[@]} -gt 0 ] && exit 3
exit 0
