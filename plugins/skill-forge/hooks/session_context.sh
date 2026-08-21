#!/usr/bin/env bash
# skill-forge SessionStart guardrail (sensor only — emits context, no permission decision).
# Reminds the operating rules whenever a session starts with this plugin installed.
set -euo pipefail

read -r -d '' CONTEXT <<'EOF' || true
skill-forge is installed. When creating, fixing, or reviewing an agent/skill/plugin, follow the forge-wizard flow:
- Zero-hole definition: maintain a Definition Ledger; do NOT fill fields from memory; suggest, never assume; block generation while any field is PENDING.
- Architecture: every generated skill has a master orchestrator + single-task specialized subagents (one task per agent).
- Hooks always: every generated artifact ships guardrail hooks scaled to its complexity.
- KB + maintainer: any knowledge-bearing artifact ships its own KB (provenance + tier) plus single-task maintainer agents.
- Mandatory model: every agent/orchestrator declares its model(s), with an equivalence fallback when the recommended one is unavailable.
- HTML approval view: render an HTML workflow view and get user approval BEFORE building.
- Internal files in English; reply to the user in their language.
Source of truth for best practices and models: the plugin's kb/ (pointer, never copy).
EOF

# Emit as additionalContext via hook JSON output.
printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":%s}}\n' \
  "$(printf '%s' "$CONTEXT" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')"
