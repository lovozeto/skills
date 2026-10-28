#!/usr/bin/env bash
# Seam: bench-model's command line, rows and comparison, with a fake agent.
source "$(dirname "$0")/lib.sh"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
export DELEGATION_BENCH_DIR="$T" BENCH_ASK_OPENCODE="$PLUGIN/tests/stubs/fake-agent"
BM="$PLUGIN/bin/bench-model"

out="$(FAKE_AGENT=fix "$BM" good:1b --tasks code --only sh_feat 2>&1)"
expect_contains "bare name becomes ollama/<id>" "$(cat "$T/ollama_good_1b.tsv")" $'ollama/good:1b\tcode\tsh_feat'
expect_contains "a working fix passes" "$(cat "$T/ollama_good_1b.tsv")" $'\tpass\t'

out="$("$BM" ollama/bad:1b --tasks code --only sh_feat 2>&1)"
expect_contains "no change fails" "$(cat "$T/ollama_bad_1b.tsv")" $'\tfail\t'
expect_contains "compares with the earlier model" "$out" "vs ollama/good:1b: worse (0 vs 1 of 1 shared"

"$BM" >/dev/null 2>&1; expect_eq "missing model -> exit 2" "$?" 2
"$BM" x --tasks nope >/dev/null 2>&1; expect_eq "bad --tasks -> exit 2" "$?" 2
"$BM" full:1b --tasks code >/dev/null 2>&1
expect_eq "a full code run writes 12 rows" "$(grep -c $'\tcode\t' "$T/ollama_full_1b.tsv")" 12
finish
