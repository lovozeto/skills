#!/usr/bin/env bash
# skill-forge SessionStart sensor (emits context only, never a permission decision).
# Silent unless an `agent-building` KB file has expired: forge-wizard is model-invoked, so its
# description already tells the agent when to use it. This hook only adds what the description
# cannot: that the KB the wizard relies on needs a refresh. Also silent when `kb` is missing.
set -uo pipefail

command -v kb >/dev/null 2>&1 || exit 0

# `kb stale` prints "<base>/<file> · expired <date>" (or "missing review_by"), one per line.
expired=()
while IFS= read -r line; do
  [[ "$line" == agent-building/* ]] && expired+=("${line%% *}")
done < <(kb stale 2>/dev/null)

((${#expired[@]})) || exit 0

CONTEXT="skill-forge KB expired (${expired[*]}): forge-wizard's prompting rules are unverified until the user types /refresh-forge-kb."
printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":%s}}\n' \
  "$(printf '%s' "$CONTEXT" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')"
