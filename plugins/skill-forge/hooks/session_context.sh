#!/usr/bin/env bash
# skill-forge SessionStart sensor (emits context only, never a permission decision).
# Silent unless a kb/ file has expired: forge-wizard is model-invoked, so its description
# already tells the agent when to use it. This hook only adds what the description cannot:
# that the KB the wizard relies on needs a refresh.
set -uo pipefail

KB="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}/kb"
TODAY="$(date +%F)"
expired=()
while IFS= read -r f; do
  rb="$(grep -m1 '^review_by:' "$f" 2>/dev/null | awk '{print $2}' | tr -d '"')"
  [[ -n "$rb" && ! "$rb" > "$TODAY" ]] && expired+=("${f#"$KB"/}")
done < <(find "$KB" -name '*.md' 2>/dev/null)

((${#expired[@]})) || exit 0

CONTEXT="skill-forge KB expired (${expired[*]}): forge-wizard's prompting rules are unverified until the user types /refresh-forge-kb."
printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":%s}}\n' \
  "$(printf '%s' "$CONTEXT" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')"
