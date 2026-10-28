#!/usr/bin/env bash
# Seam: the ask-local command line against a fake Ollama API.
source "$(dirname "$0")/lib.sh"
AL="$PLUGIN/bin/ask-local"
T="$(mktemp -d)"
python3 "$PLUGIN/tests/stubs/fake_ollama.py" "$T/port" "$T/req" & SRV=$!
trap 'kill $SRV 2>/dev/null; rm -rf "$T"' EXIT
for _ in $(seq 50); do [[ -s "$T/port" ]] && break; sleep 0.1; done
export OLLAMA_HOST_URL="http://127.0.0.1:$(cat "$T/port")"
unset ASK_LOCAL_MODEL

expect_eq "no model -> smallest installed" "$("$AL" "hi")" "model=tiny:1b"
expect_eq "ASK_LOCAL_MODEL wins over smallest" "$(ASK_LOCAL_MODEL=mid:7b "$AL" "hi")" "model=mid:7b"
expect_eq "--model wins over env" "$(ASK_LOCAL_MODEL=mid:7b "$AL" --model big-coder:30b "hi")" "model=big-coder:30b"
expect_eq "prompt from stdin" "$(echo "hi" | "$AL")" "model=tiny:1b"

"$AL" --format json "x" >/dev/null
expect_eq "--format json reaches the API" "$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["format"])' "$T/req")" "json"
"$AL" --format '{"type":"object"}' --think high --system "S" --temperature 0.2 "x" >/dev/null
expect_eq "schema, think, system, temperature reach the API" \
  "$(python3 -c 'import json,sys;r=json.load(open(sys.argv[1]));print(r["format"]["type"],r["think"],r["messages"][0]["content"],r["options"]["temperature"])' "$T/req")" "object high S 0.2"

OLLAMA_HOST_URL="http://127.0.0.1:9" "$AL" "x" >/dev/null 2>&1
expect_eq "server down on a custom URL -> exit 2" "$?" 2
"$AL" >/dev/null 2>&1 </dev/null; expect_eq "missing prompt -> exit 2" "$?" 2
"$AL" --model >/dev/null 2>&1; expect_eq "--model without value -> exit 2" "$?" 2
out="$("$AL" --model missing "x" 2>&1)"; rc=$?
expect_eq "missing model -> exit 2" "$rc" 2
expect_contains "Ollama's own error reaches the user" "$out" "model 'missing' not found"
big="$(python3 -c 'print("word " * 20000)')"
out="$(printf '%s' "$big" | "$AL" --model mid:7b 2>&1)"; rc=$?
expect_eq "prompt over num_ctx -> exit 2, not a silent cut" "$rc" 2
expect_contains "says why" "$out" "16384"
out="$("$AL" --model nopin:7b "hi" 2>&1)"
expect_contains "warns when num_ctx is not pinned" "$out" "no pinned num_ctx"
"$AL" --format '{not json' "x" >/dev/null 2>&1; expect_eq "malformed --format -> exit 2" "$?" 2
"$AL" --bogus "x" >/dev/null 2>&1; expect_eq "unknown flag -> exit 2" "$?" 2
"$AL" two words >/dev/null 2>&1; expect_eq "two positional arguments -> exit 2" "$?" 2
finish
