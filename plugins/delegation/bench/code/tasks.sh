# Code benchmark tasks: 12 agentic tasks (write / fix / feature) in Python, React TSX,
# Swift, C++, Rust and shell. Each task has setup_<t> (fixture), P_<t> (prompt) and
# check_<t> (compiles and runs the result, checks nothing else changed; prints 1 or 0).
# Sourced by bin/bench-model and selftest.sh. Fixtures and prompts are the measured
# instruments: changing them breaks comparison with earlier results.

TSC="${TSC:-$(command -v tsc 2>/dev/null || true)}"
TASKS_ALL=(py py_bug tsx tsx_bug swift swift_bug cpp cpp_feat rust_bug rust_feat sh_bug sh_feat)

# Tools each task needs; a task whose tools are missing is skipped, not failed.
tools_for() {
  case "$1" in
    py|py_bug) echo python3 ;;
    tsx) echo tsc ;;
    tsx_bug) echo "tsc node" ;;
    swift|swift_bug) echo swiftc ;;
    cpp|cpp_feat) echo clang++ ;;
    rust_bug|rust_feat) echo rustc ;;
    sh_bug|sh_feat) echo bash ;;
  esac
}

setup_py() {
  printf 'def compute_total(items):\n    return sum(i["price"] for i in items)\n\n# compute_total is used by billing\n' > "$1/pricing.py"
  printf 'from pricing import compute_total\n\nprint(compute_total([{"price": 2}]))\nlabel = "compute_total"\n' > "$1/main.py"
}
P_py='In this directory, rename the Python function compute_total to calculate_total everywhere (definition, import and every call), in all .py files. Change nothing else: string literals and comments stay exactly as they are. When done, reply with exactly: DONE'
check_py() {
  local d=$1 ok=1
  grep -q '^def calculate_total(items):' "$d/pricing.py" || ok=0
  grep -q '^from pricing import calculate_total$' "$d/main.py" || ok=0
  grep -q '^print(calculate_total(\[{"price": 2}\]))$' "$d/main.py" || ok=0
  grep -q '^label = "compute_total"$' "$d/main.py" || ok=0
  grep -q '^# compute_total is used by billing$' "$d/pricing.py" || ok=0
  (cd "$d" && python3 main.py 2>/dev/null | grep -qx 2) || ok=0
  echo $ok
}

setup_tsx() {
  cat > "$1/Button.tsx" <<'X'
type ButtonProps = { label: string; onClick: () => void };

export function Button({ label, onClick }: ButtonProps) {
  return <button onClick={onClick}>{label}</button>;
}
X
  cat > "$1/App.tsx" <<'X'
import { Button } from "./Button";

export function App({ loading }: { loading: boolean }) {
  return <Button label="Send RSVP" onClick={() => console.log("sent")} />;
}
X
  printf 'declare namespace JSX { interface IntrinsicElements { [name: string]: any } }\n' > "$1/jsx.d.ts"
}
P_tsx='In this React + TypeScript project, add an optional boolean prop `disabled` to the Button component in Button.tsx and pass it through to the native <button> element. Then in App.tsx make the Button disabled while `loading` is true. Do not change anything else and do not touch jsx.d.ts. When done, reply with exactly: DONE'
check_tsx() {
  local d=$1 ok=1
  grep -q 'disabled?: boolean' "$d/Button.tsx" || ok=0
  grep -Eq '<button[^>]*disabled=\{disabled\}' "$d/Button.tsx" || ok=0
  grep -Eq 'disabled=\{loading\}' "$d/App.tsx" || ok=0
  grep -q 'label="Send RSVP"' "$d/App.tsx" || ok=0
  (cd "$d" && "$TSC" --noEmit --strict --jsx preserve --target es2020 --moduleResolution node Button.tsx App.tsx jsx.d.ts >/dev/null 2>&1) || ok=0
  echo $ok
}

setup_swift() {
  cat > "$1/Guest.swift" <<'X'
struct Guest {
    let name: String
    let age: Int
}

func adults(in guests: [Guest]) -> [Guest] {
    guests.filter { $0.age >= 18 }
}

let guests = [Guest(name: "Ana", age: 30), Guest(name: "Leo", age: 7)]
print(adults(in: guests).map(\.name).joined(separator: ","))
X
}
P_swift='In Guest.swift, add a computed property `isAdult: Bool` to the Guest struct (true when age is 18 or more), and change the adults(in:) function to use it instead of comparing the age directly. Keep the same output. Do not change anything else. When done, reply with exactly: DONE'
check_swift() {
  local d=$1 ok=1
  grep -Eq 'var isAdult: Bool' "$d/Guest.swift" || ok=0
  grep -Eq 'filter *\{ *\$0\.isAdult *\}|filter\(\\\.isAdult\)|filter *\{ *guest in guest\.isAdult *\}' "$d/Guest.swift" || ok=0
  [ "$(cd "$d" && swiftc Guest.swift -o g 2>/dev/null && ./g)" = "Ana" ] || ok=0
  echo $ok
}

setup_cpp() {
  cat > "$1/sum.cpp" <<'X'
#include <iostream>

// Returns 1 + 2 + ... + n.
int sum_to(int n) {
    int total = 0;
    for (int i = 1; i < n; ++i) {
        total += i;
    }
    return total;
}

int main() {
    std::cout << sum_to(4) << "\n";
    return 0;
}
X
}
P_cpp='sum.cpp has a bug: sum_to(n) should return 1 + 2 + ... + n but sum_to(4) prints 6 instead of 10. Find and fix the bug with the smallest possible change. Do not change anything else. When done, reply with exactly: DONE'
check_cpp() {
  local d=$1 ok=1
  grep -q '// Returns 1 + 2 + ... + n.' "$d/sum.cpp" || ok=0
  [ "$(cd "$d" && clang++ -std=c++17 sum.cpp -o s 2>/dev/null && ./s)" = "10" ] || ok=0
  echo $ok
}

setup_py_bug() {
  cat > "$1/stats.py" <<'X'
def average(values):
    """Mean of values; 0.0 for an empty list."""
    return sum(values) / len(values)


print(average([2, 4]))
print(average([]))
X
}
P_py_bug='Running stats.py crashes with ZeroDivisionError. Fix average() so it matches its docstring (0.0 for an empty list), with the smallest change. Do not change anything else. When done, reply with exactly: DONE'
check_py_bug() {
  local d=$1 ok=1
  grep -q '"""Mean of values; 0.0 for an empty list."""' "$d/stats.py" || ok=0
  [ "$(cd "$d" && python3 stats.py 2>/dev/null | tr '\n' ' ')" = "3.0 0.0 " ] || ok=0
  echo $ok
}

setup_tsx_bug() {
  cat > "$1/label.ts" <<'X'
// "1 guest", "2 guests", "0 guests"
export function guestLabel(count: number): string {
  return count + " guests";
}
X
}
P_tsx_bug='In label.ts, guestLabel(1) returns "1 guests" but should return "1 guest" (singular only for exactly 1; "0 guests" and "2 guests" stay plural). Fix it. Do not change anything else. When done, reply with exactly: DONE'
check_tsx_bug() {
  local d=$1 ok=1
  (cd "$d" && "$TSC" --strict --module commonjs --target es2020 --outDir out label.ts >/dev/null 2>&1) || { echo 0; return; }
  [ "$(cd "$d" && node -e 'const l=require("./out/label.js").guestLabel;console.log([0,1,2].map(l).join("|"))')" = "0 guests|1 guest|2 guests" ] || ok=0
  echo $ok
}

setup_swift_bug() {
  cat > "$1/Parse.swift" <<'X'
func parseAge(_ text: String) -> Int {
    return Int(text)!
}

print(parseAge("42"))
print(parseAge("abc"))
X
}
P_swift_bug='Parse.swift crashes at runtime on parseAge("abc") because of a force unwrap. Make parseAge return 0 when the text is not a number, without force unwrapping. Do not change anything else. When done, reply with exactly: DONE'
check_swift_bug() {
  local d=$1 ok=1
  grep -q 'Int(text)!' "$d/Parse.swift" && ok=0
  [ "$(cd "$d" && swiftc Parse.swift -o p 2>/dev/null && ./p | tr '\n' ' ')" = "42 0 " ] || ok=0
  echo $ok
}

setup_cpp_feat() {
  cat > "$1/math.cpp" <<'X'
#include <iostream>

// Returns 1 + 2 + ... + n.
int sum_to(int n) {
    int total = 0;
    for (int i = 1; i <= n; ++i) {
        total += i;
    }
    return total;
}

int main() {
    std::cout << sum_to(4) << "\n";
    return 0;
}
X
}
P_cpp_feat='In math.cpp, add a function `long long product_to(int n)` that returns 1 * 2 * ... * n (1 when n is 0), and in main print product_to(5) on its own line after the existing line. Do not change sum_to. When done, reply with exactly: DONE'
check_cpp_feat() {
  local d=$1 ok=1
  grep -q 'long long product_to(int n)' "$d/math.cpp" || ok=0
  [ "$(cd "$d" && clang++ -std=c++17 math.cpp -o m 2>/dev/null && ./m | tr '\n' ' ')" = "10 120 " ] || ok=0
  echo $ok
}

setup_rust_bug() {
  cat > "$1/main.rs" <<'X'
/// Largest value, or None for an empty slice.
fn largest(values: &[i32]) -> Option<i32> {
    let mut best = 0;
    for &v in values {
        if v > best {
            best = v;
        }
    }
    Some(best)
}

fn main() {
    println!("{:?}", largest(&[3, 9, 4]));
    println!("{:?}", largest(&[-5, -2]));
    println!("{:?}", largest(&[]));
}
X
}
P_rust_bug='In main.rs, largest() is wrong: for [-5, -2] it returns Some(0) and for an empty slice it returns Some(0); it should return Some(-2) and None, as its doc comment says. Fix it. Do not change main or the doc comment. When done, reply with exactly: DONE'
check_rust_bug() {
  local d=$1 ok=1
  grep -q '/// Largest value, or None for an empty slice.' "$d/main.rs" || ok=0
  [ "$(cd "$d" && rustc -O main.rs -o r 2>/dev/null && ./r | tr '\n' ' ')" = "Some(9) Some(-2) None " ] || ok=0
  echo $ok
}

setup_rust_feat() {
  cat > "$1/main.rs" <<'X'
struct Guest {
    name: String,
    age: u32,
}

fn main() {
    let g = Guest { name: String::from("Ana"), age: 30 };
    println!("{} {}", g.name, g.age);
}
X
}
P_rust_feat='In main.rs, add an impl block for Guest with a method `fn is_adult(&self) -> bool` (true when age is 18 or more), and in main print the result of g.is_adult() on its own line after the existing line. Do not change anything else. When done, reply with exactly: DONE'
check_rust_feat() {
  local d=$1 ok=1
  grep -q 'fn is_adult(&self) -> bool' "$d/main.rs" || ok=0
  [ "$(cd "$d" && rustc main.rs -o r 2>/dev/null && ./r | tr '\n' ' ')" = "Ana 30 true " ] || ok=0
  echo $ok
}

setup_sh_bug() {
  mkdir -p "$1/data"; : > "$1/data/a.txt b.txt"; : > "$1/data/c.txt"; : > "$1/data/d.log"
  cat > "$1/count.sh" <<'X'
#!/usr/bin/env bash
# Print how many .txt files are in DIR (default: current folder).
dir=${1:-.}
count=0
for f in $(ls $dir); do
  case $f in *.txt) count=$((count + 1)) ;; esac
done
echo $count
X
}
P_sh_bug='count.sh prints the wrong number when file names contain spaces: `bash count.sh data` prints 3 but data/ holds only 2 .txt files ("a.txt b.txt", one file with a space in its name, and "c.txt"). Fix the script so it handles spaces correctly. Keep the comment and the default folder. Do not change anything in data/. When done, reply with exactly: DONE'
check_sh_bug() {
  local d=$1 ok=1
  grep -q '^# Print how many .txt files are in DIR' "$d/count.sh" || ok=0
  [ "$(cd "$d" && bash count.sh data)" = "2" ] || ok=0
  [ -f "$d/data/a.txt b.txt" ] && [ -f "$d/data/d.log" ] || ok=0
  echo $ok
}

setup_sh_feat() {
  cat > "$1/greet.sh" <<'X'
#!/usr/bin/env bash
name=${1:-world}
echo "hello $name"
X
}
P_sh_feat='Add a -h flag to greet.sh: `bash greet.sh -h` must print exactly `usage: greet.sh [NAME]` and exit with status 0. Everything else must keep working as now (`bash greet.sh Ana` prints `hello Ana`, no argument prints `hello world`). When done, reply with exactly: DONE'
check_sh_feat() {
  local d=$1 ok=1
  [ "$(cd "$d" && bash greet.sh -h)" = "usage: greet.sh [NAME]" ] || ok=0
  (cd "$d" && bash greet.sh -h >/dev/null) || ok=0
  [ "$(cd "$d" && bash greet.sh Ana)" = "hello Ana" ] || ok=0
  [ "$(cd "$d" && bash greet.sh)" = "hello world" ] || ok=0
  echo $ok
}
