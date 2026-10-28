#!/usr/bin/env bash
# Proves every checker: it must fail (0) on the untouched fixture and pass (1) on a
# hand-written fix. Tasks whose tools are missing are reported as skipped.
# Usage: selftest.sh            exit 0 when every runnable checker behaves.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=tasks.sh
source "$HERE/tasks.sh"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT

# edit FILE OLD NEW: literal replace; fails loudly if OLD is absent.
edit() {
  python3 - "$@" <<'PY'
import sys
path, old, new = sys.argv[1:4]
text = open(path).read()
if old not in text:
    sys.exit("selftest: pattern not found in " + path)
open(path, "w").write(text.replace(old, new))
PY
}

fix_py() { edit "$1/pricing.py" "def compute_total" "def calculate_total"
  edit "$1/main.py" "import compute_total" "import calculate_total"
  edit "$1/main.py" "print(compute_total" "print(calculate_total"; }
fix_tsx() { edit "$1/Button.tsx" "onClick: () => void }" "onClick: () => void; disabled?: boolean }"
  edit "$1/Button.tsx" "{ label, onClick }" "{ label, onClick, disabled }"
  edit "$1/Button.tsx" "<button onClick={onClick}>" "<button onClick={onClick} disabled={disabled}>"
  edit "$1/App.tsx" 'onClick={() => console.log("sent")} />' 'onClick={() => console.log("sent")} disabled={loading} />'; }
fix_swift() { edit "$1/Guest.swift" "    let age: Int" $'    let age: Int\n    var isAdult: Bool { age >= 18 }'
  edit "$1/Guest.swift" '$0.age >= 18' '$0.isAdult'; }
fix_cpp() { edit "$1/sum.cpp" "i < n" "i <= n"; }
fix_py_bug() { edit "$1/stats.py" "    return sum(values) / len(values)" $'    if not values:\n        return 0.0\n    return sum(values) / len(values)'; }
fix_tsx_bug() { edit "$1/label.ts" '  return count + " guests";' '  return count + (count === 1 ? " guest" : " guests");'; }
fix_swift_bug() { edit "$1/Parse.swift" "Int(text)!" "Int(text) ?? 0"; }
fix_cpp_feat() { edit "$1/math.cpp" "int main() {" $'long long product_to(int n) {\n    long long r = 1;\n    for (int i = 2; i <= n; ++i) r *= i;\n    return r;\n}\n\nint main() {'
  edit "$1/math.cpp" 'sum_to(4) << "\n";' $'sum_to(4) << "\\n";\n    std::cout << product_to(5) << "\\n";'; }
fix_rust_bug() { edit "$1/main.rs" $'    let mut best = 0;\n    for &v in values {\n        if v > best {\n            best = v;\n        }\n    }\n    Some(best)' "    values.iter().copied().max()"; }
fix_rust_feat() { edit "$1/main.rs" "fn main() {" $'impl Guest {\n    fn is_adult(&self) -> bool {\n        self.age >= 18\n    }\n}\n\nfn main() {'
  edit "$1/main.rs" 'g.name, g.age);' $'g.name, g.age);\n    println!("{}", g.is_adult());'; }
fix_sh_bug() { edit "$1/count.sh" $'for f in $(ls $dir); do\n  case $f in' $'for f in "$dir"/*; do\n  case "$f" in'; }
fix_sh_feat() { edit "$1/greet.sh" "name=" $'if [ "${1:-}" = "-h" ]; then echo "usage: greet.sh [NAME]"; exit 0; fi\nname='; }

bad=0
for t in "${TASKS_ALL[@]}"; do
  missing=""; for tool in $(tools_for "$t"); do
    [[ "$tool" == tsc ]] && { [[ -n "$TSC" ]] || missing+="tsc "; continue; }
    command -v "$tool" >/dev/null || missing+="$tool "; done
  if [[ -n "$missing" ]]; then echo "$t skip (missing: ${missing% })"; continue; fi
  mkdir -p "$T/$t/raw" "$T/$t/fix"; "setup_$t" "$T/$t/raw"; "setup_$t" "$T/$t/fix"; "fix_$t" "$T/$t/fix"
  raw=$("check_$t" "$T/$t/raw" 2>/dev/null); fix=$("check_$t" "$T/$t/fix" 2>/dev/null)
  echo "$t raw=$raw fix=$fix"
  [[ "$raw" == 0 && "$fix" == 1 ]] || bad=1
done
exit $bad
