#!/usr/bin/env bash
# knowledge-base SessionStart sensor (emits context only, never a permission decision).
# Silent when the kb CLI is on PATH. Otherwise one line naming the fix; it installs nothing.
set -uo pipefail

command -v kb >/dev/null && exit 0

CONTEXT="knowledge-base plugin: the kb CLI is not on PATH (install it from https://github.com/lovozeto/kb and put it on PATH); until then the KB skills read \${KB_ROOT:-~/dev/claude-kb}/INDEX.md instead."
printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$CONTEXT"
