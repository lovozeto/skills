#!/usr/bin/env bash
# Seam: bench-model's command line, rows and comparison, with a fake agent and fixture tasks.
source "$(dirname "$0")/lib.sh"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
export DELEGATION_BENCH_DIR="$T" BENCH_ASK_OPENCODE="$PLUGIN/tests/stubs/fake-agent"
export DELEGATION_BENCH_TASKS="$PLUGIN/tests/fixtures/bench-tasks"
BM="$PLUGIN/bin/bench-model"

FAKE_AGENT=fix "$BM" cloud/x-free --tasks code >/dev/null 2>&1
expect_contains "a working fix passes" "$(cat "$T/cloud_x-free.tsv")" $'cloud/x-free\tcode\tsh_feat'
expect_contains "pass row" "$(cat "$T/cloud_x-free.tsv")" $'\tpass\t'

FAKE_AGENT=fix "$BM" good:1b --tasks code --only sh_feat >/dev/null 2>&1
expect_contains "bare name becomes ollama/<id>" "$(cat "$T/ollama_good_1b.tsv")" $'ollama/good:1b\tcode'
out="$("$BM" ollama/bad:1b --tasks code --runs 3 2>&1)"
expect_eq "--runs 3 writes three rows" "$(grep -c $'\tsh_feat\t' "$T/ollama_bad_1b.tsv")" 3
expect_contains "compares with earlier models" "$out" "vs ollama/good:1b: worse (0.0 vs 1.0 of 1 shared"

out="$("$BM" ollama/bad:1b --tasks code --current good:1b --class code 2>&1)"
expect_contains "decision line" "$out" "Decision: keep ollama/good:1b"

"$BM" x --tasks text >/dev/null 2>&1
expect_contains "text rows" "$(cat "$T/ollama_x.tsv")" $'\ttext\tT5\t'
expect_eq "T5 rewrite saved" "$(cat "$T/ollama_x_T5.txt")" "rewrite"

DELEGATION_BENCH_TASKS="$T/none" "$BM" x >/dev/null 2>&1; expect_eq "no tasks found -> exit 2" "$?" 2
"$BM" >/dev/null 2>&1; expect_eq "missing model -> exit 2" "$?" 2
"$BM" x --tasks nope >/dev/null 2>&1; expect_eq "bad --tasks -> exit 2" "$?" 2
"$BM" x --runs >/dev/null 2>&1; expect_eq "flag without value -> exit 2" "$?" 2
"$BM" x --current y >/dev/null 2>&1; expect_eq "--current without --class -> exit 2" "$?" 2
finish
