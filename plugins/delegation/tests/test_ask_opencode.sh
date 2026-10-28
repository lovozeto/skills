#!/usr/bin/env bash
# Seam: the ask-opencode command line (exit codes and what reaches opencode).
source "$(dirname "$0")/lib.sh"
export PATH="$PLUGIN/tests/stubs:$PATH"
unset ASK_OPENCODE_MODEL
AO="$PLUGIN/bin/ask-opencode"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT

out="$("$AO" "hi" 2>&1)"; rc=$?
expect_eq "no model -> exit 2" "$rc" 2
expect_contains "no model -> lists free models" "$out" "opencode/deepseek-v4.1-flash-free"

out="$("$AO" --model opencode/beam-free "Summarize this" 2>&1)"; rc=$?
expect_eq "free cloud model, clean prompt -> runs" "$rc" 0
expect_contains "prompt reaches opencode" "$out" "prompt=Summarize this"

out="$(ASK_OPENCODE_MODEL=opencode/beam-free "$AO" "x" 2>&1)"
expect_contains "ASK_OPENCODE_MODEL is used" "$out" "model=opencode/beam-free"

"$AO" --model anthropic/claude-x "x" >/dev/null 2>&1; expect_eq "paid provider -> exit 4" "$?" 4
"$AO" --model opencode/big-paid "x" >/dev/null 2>&1; expect_eq "non-free opencode id -> exit 4" "$?" 4
"$AO" --model google/gemini-4-argon "x" >/dev/null 2>&1; expect_eq "Gemini non-Flash -> exit 4" "$?" 4
"$AO" --model google/gemini-3.1-flash-lite "Write a hello world in Go" >/dev/null 2>&1; expect_eq "Gemini Flash -> allowed" "$?" 0

out="$("$AO" --model opencode/beam-free "Email ana.perez@gmail.com about it" 2>&1)"; rc=$?
expect_eq "email in prompt -> exit 3" "$rc" 3
expect_contains "data block names the reason" "$out" "email"
echo "Call me at +57 300 123 4567" | "$AO" --model opencode/beam-free >/dev/null 2>&1; expect_eq "phone via stdin -> exit 3" "$?" 3
"$AO" --model opencode/beam-free "token eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.abc123def" >/dev/null 2>&1; expect_eq "JWT -> exit 3" "$?" 3
"$AO" --model opencode/beam-free "key sk-abcdefghijklmnopqrstuvwxyz123456" >/dev/null 2>&1; expect_eq "API key -> exit 3" "$?" 3
"$AO" --model opencode/beam-free "account 123456789012" >/dev/null 2>&1; expect_eq "long digit run -> exit 3" "$?" 3
"$AO" --model opencode/beam-free "mail dev@example.com in the docs" >/dev/null 2>&1; expect_eq "example.com email -> allowed" "$?" 0

mkdir -p "$T/repo/src" "$T/repo/node_modules/x"; echo "print(1)" > "$T/repo/src/a.py"
"$AO" --model opencode/beam-free --dir "$T/repo" "rename x" >/dev/null 2>&1; expect_eq "clean repo -> allowed" "$?" 0
touch "$T/repo/node_modules/x/data.csv"
"$AO" --model opencode/beam-free --dir "$T/repo" "rename x" >/dev/null 2>&1; expect_eq "data file inside node_modules ignored" "$?" 0
touch "$T/repo/src/.env.local"
out="$("$AO" --model opencode/beam-free --dir "$T/repo" "rename x" 2>&1)"; rc=$?
expect_eq ".env in --dir -> exit 3" "$rc" 3
expect_contains "names the file" "$out" ".env.local"
rm "$T/repo/src/.env.local"; touch "$T/repo/src/guests.sqlite3"
"$AO" --model opencode/beam-free --dir "$T/repo" "rename x" >/dev/null 2>&1; expect_eq "sqlite in --dir -> exit 3" "$?" 3

out="$("$AO" --model ollama/devstral-small-2:24b --dir "$T/repo" "Email ana.perez@gmail.com" 2>&1)"; rc=$?
expect_eq "local model skips the data check" "$rc" 0
"$AO" --model >/dev/null 2>&1; expect_eq "--model without value -> exit 2" "$?" 2
expect_contains "text mode: no bash" "$("$AO" --model ollama/qwen3:14b "x" 2>&1)" "bash=False"
mkdir -p "$T/clean"; expect_contains "cloud agent: no bash" "$("$AO" --model opencode/beam-free --dir "$T/clean" "x" 2>&1)" "bash=False"
expect_contains "local agent keeps bash" "$("$AO" --model ollama/qwen3:14b --dir "$T/repo" "x" 2>&1)" "bash=True"
finish
