#!/usr/bin/env bash
# Seams: delegation-machine-info, delegation-pull-model, delegation-ollama-env, with fake CLIs.
source "$(dirname "$0")/lib.sh"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
export FAKE_LOG="$T/log"; : > "$FAKE_LOG"

out="$("$PLUGIN/bin/delegation-machine-info")"
for k in UUID CHIP RAM_GB MACOS DISK_FREE_GB BREW OLLAMA OPENCODE; do expect_contains "machine-info has $k" "$out" "$k="; done
[[ "$(grep '^RAM_GB=' <<<"$out" | cut -d= -f2)" =~ ^[0-9]+$ ]] && pass || fail "RAM_GB is an integer"

PM="$PLUGIN/bin/delegation-pull-model"
PATH="$PLUGIN/tests/stubs:$PATH" FAKE_LIST="have:1b" "$PM" have:1b 8192 have:1b >/dev/null 2>&1
expect_eq "model on disk -> nothing pulled" "$(grep -c 'pull' "$FAKE_LOG")" 0
: > "$FAKE_LOG"
PATH="$PLUGIN/tests/stubs:$PATH" "$PM" short:7b 32768 hf.co/org/Long-GGUF:Q5_K_M >/dev/null 2>&1
expect_contains "hf source pulled" "$(cat "$FAKE_LOG")" "ollama pull hf.co/org/Long-GGUF:Q5_K_M"
expect_contains "created under the short name" "$(cat "$FAKE_LOG")" "ollama create short:7b"
expect_contains "long name removed" "$(cat "$FAKE_LOG")" "ollama rm hf.co/org/Long-GGUF:Q5_K_M"
expect_contains "num_ctx pinned" "$(cat "$FAKE_LOG.modelfile")" "PARAMETER num_ctx 32768"
expect_eq "old num_ctx dropped" "$(grep -c 'num_ctx 4096' "$FAKE_LOG.modelfile")" 0
: > "$FAKE_LOG"
PATH="$PLUGIN/tests/stubs:$PATH" "$PM" qwen3:14b 32768 qwen3:14b >/dev/null 2>&1
expect_eq "library source equal to name is not removed" "$(grep -c 'ollama rm' "$FAKE_LOG")" 0
: > "$FAKE_LOG"
PATH="$PLUGIN/tests/stubs:$PATH" "$PM" oss:20b 65536 https://example.org/m.gguf >/dev/null 2>&1
expect_contains "direct gguf downloaded" "$(cat "$FAKE_LOG")" "curl https://example.org/m.gguf"
expect_contains "gguf imported with num_ctx" "$(cat "$FAKE_LOG.modelfile")" "PARAMETER num_ctx 65536"
"$PM" x 1 >/dev/null 2>&1; expect_eq "missing argument -> exit 2" "$?" 2

OE="$PLUGIN/bin/delegation-ollama-env"; : > "$FAKE_LOG"
mkdir -p "$T/home/Library/LaunchAgents"; touch "$T/home/Library/LaunchAgents/com.lobomorir.ollama-env.plist"
HOME="$T/home" PATH="$PLUGIN/tests/stubs:$PATH" "$OE" install >/dev/null 2>&1
expect_contains "plist written" "$(cat "$T/home/Library/LaunchAgents/com.delegation.ollama-env.plist")" "OLLAMA_KV_CACHE_TYPE q8_0"
expect_contains "env applied now" "$(cat "$FAKE_LOG")" "launchctl setenv OLLAMA_FLASH_ATTENTION 1"
[[ ! -e "$T/home/Library/LaunchAgents/com.lobomorir.ollama-env.plist" ]] && pass || fail "old label replaced"
: > "$FAKE_LOG"; HOME="$T/home" PATH="$PLUGIN/tests/stubs:$PATH" "$OE" remove >/dev/null 2>&1
[[ ! -e "$T/home/Library/LaunchAgents/com.delegation.ollama-env.plist" ]] && pass || fail "remove deletes the plist"
expect_contains "env unset" "$(cat "$FAKE_LOG")" "launchctl unsetenv OLLAMA_KV_CACHE_TYPE"
finish
