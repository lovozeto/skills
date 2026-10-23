#!/usr/bin/env bash
# skill-forge SessionStart guardrail (sensor only — emits context, no permission decision).
# One pointer line per session: the rules live in forge-wizard (model-invoked) and kb/,
# so repeating them here would only add always-loaded context.
set -euo pipefail

read -r -d '' CONTEXT <<'EOF' || true
skill-forge is installed: to create, fix, or review a skill, agent, or plugin, use the forge-wizard skill (its rules live there and in the plugin's kb/).
EOF

# Emit as additionalContext via hook JSON output.
printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":%s}}\n' \
  "$(printf '%s' "$CONTEXT" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')"
