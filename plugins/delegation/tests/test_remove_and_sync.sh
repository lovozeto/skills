#!/usr/bin/env bash
# Seams: sync-ollama-to-opencode (add and --remove) and delegation-remove-ollama, in a temp HOME.
source "$(dirname "$0")/lib.sh"
T="$(mktemp -d)"
python3 "$PLUGIN/tests/stubs/fake_ollama.py" "$T/port" "$T/req" & SRV=$!
trap 'kill $SRV 2>/dev/null; rm -rf "$T"' EXIT
for _ in $(seq 50); do [[ -s "$T/port" ]] && break; sleep 0.1; done
export OLLAMA_HOST_URL="http://127.0.0.1:$(cat "$T/port")" FAKE_LOG="$T/log"; : > "$FAKE_LOG"

CFG="$T/opencode.json"; echo '{"provider": {"other": {"name": "keep me"}}}' > "$CFG"
"$PLUGIN/bin/sync-ollama-to-opencode" --opencode-json "$CFG" >/dev/null 2>&1
models="$(python3 -c 'import json,sys;d=json.load(open(sys.argv[1]));print(" ".join(sorted(d["provider"]["ollama"]["models"])), d["provider"]["ollama"]["models"]["tiny:1b"]["limit"]["context"], d["provider"]["other"]["name"])' "$CFG")"
expect_eq "every installed model registered with its num_ctx; other providers kept" "$models" "big-coder:30b mid:7b tiny:1b 16384 keep me"
"$PLUGIN/bin/sync-ollama-to-opencode" --opencode-json "$CFG" --remove >/dev/null 2>&1
expect_eq "--remove drops only the ollama provider" "$(python3 -c 'import json,sys;print(sorted(json.load(open(sys.argv[1]))["provider"]))' "$CFG")" "['other']"

H="$T/home"; mkdir -p "$H/.ollama/models" "$H/Library/Application Support/Ollama" "$H/Library/Caches/com.electron.ollama" "$H/Library/LaunchAgents" "$H/.config/opencode" "$T/Applications/Ollama.app"
echo blob > "$H/.ollama/models/blob"; echo '{"provider":{"ollama":{}}}' > "$H/.config/opencode/opencode.json"
RO="$PLUGIN/bin/delegation-remove-ollama"
out="$(HOME="$H" OLLAMA_APP="$T/Applications/Ollama.app" PATH="$PLUGIN/tests/stubs:$PATH" "$RO" 2>&1)"
expect_contains "list mode names the models folder" "$out" ".ollama"
expect_contains "list mode names Library leftovers" "$out" "Application Support/Ollama"
[[ -d "$H/.ollama" ]] && pass || fail "list mode moves nothing"

HOME="$H" OLLAMA_APP="$T/Applications/Ollama.app" PATH="$PLUGIN/tests/stubs:$PATH" "$RO" --apply >/dev/null 2>&1
bin="$(ls -d "$H"/.Trash/ollama-removed-* 2>/dev/null | head -1)"
[[ -n "$bin" && -f "$bin/.ollama/models/blob" ]] && pass || fail "models moved to the Trash, not deleted"
[[ ! -e "$H/.ollama" && ! -e "$H/Library/Caches/com.electron.ollama" && ! -e "$T/Applications/Ollama.app" ]] && pass || fail "leftovers gone from their places"
expect_contains "app uninstalled with brew" "$(cat "$FAKE_LOG")" "brew uninstall --cask ollama-app"
expect_eq "opencode ollama provider removed" "$(python3 -c 'import json,sys;print(sorted(json.load(open(sys.argv[1]))["provider"]))' "$H/.config/opencode/opencode.json")" "[]"
finish
