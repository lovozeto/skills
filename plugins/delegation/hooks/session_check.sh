#!/usr/bin/env bash
# delegation SessionStart sensor (emits context only, never a permission decision).
# Silent when every dependency is present. Otherwise it states what is missing and the
# command that installs it; it installs nothing.
set -uo pipefail

missing=()
command -v python3 >/dev/null || missing+=("python3 (runs the wrappers' helpers; install: xcode-select --install)")
command -v curl >/dev/null || missing+=("curl (calls the Ollama API)")
command -v ollama >/dev/null || missing+=("ollama (local models for ask-local and private agents; install: brew install --cask ollama-app)")
command -v opencode >/dev/null || missing+=("opencode (agent for tasks that edit files; install: brew install opencode)")
if [[ -z "$(find "$HOME/.claude/skills" "$HOME/.agents/skills" -maxdepth 3 -name prompt-master -type d 2>/dev/null | head -1)" \
   && -z "$(find "$HOME/.claude/plugins/cache" -maxdepth 6 -type d -name prompt-master 2>/dev/null | head -1)" ]]; then
  missing+=("the prompt-master skill (write-for-model needs it; install: npx skills add nidhinjs/prompt-master -g -y -a claude-code)")
fi

((${#missing[@]})) || exit 0

CONTEXT="delegation plugin: missing $(printf '%s; ' "${missing[@]}" | sed 's/; $//'). Delegation routes that need these are unavailable until the user installs them; the rest still work."
printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":%s}}\n' \
  "$(printf '%s' "$CONTEXT" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')"
