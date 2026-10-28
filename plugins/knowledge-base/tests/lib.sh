# Minimal test helpers. Source from a test file; call `finish` at the end.
PLUGIN="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAILS=0; PASSES=0
pass() { PASSES=$((PASSES + 1)); }
fail() { FAILS=$((FAILS + 1)); echo "FAIL: $1" >&2; }
expect_eq() { [[ "$2" == "$3" ]] && pass || fail "$1 (expected '$3', got '$2')"; }
expect_contains() { [[ "$2" == *"$3"* ]] && pass || fail "$1 (missing '$3' in: ${2:0:200})"; }
finish() { echo "$(basename "$0"): $PASSES passed, $FAILS failed"; [[ $FAILS -eq 0 ]]; }
