"""Measure skill selection by hand with `claude -p` (see README.md).

usage: run_triggers.py <plugin-dir> <label> <model> [runs]
"""
import concurrent.futures as cf, json, pathlib, subprocess, sys

here = pathlib.Path(__file__).resolve().parent
plugin_dir, label, model = sys.argv[1:4]
runs = int(sys.argv[4]) if len(sys.argv) > 4 else 3
work = here / "workdir"
subprocess.run([sys.executable, str(here / "make_fixtures.py"), str(work)], check=True)
raw = here / "raw" / label
raw.mkdir(parents=True, exist_ok=True)
SYSTEM = "The session objective is the user's message; do not ask for it."


def one(job):
    skill, k, i, query = job
    for attempt in range(2):
        p = subprocess.run(
            ["claude", "-p", query, "--model", model, "--plugin-dir", plugin_dir,
             "--output-format", "stream-json", "--verbose", "--max-turns", "3",
             "--allowedTools", "Skill,Read", "--append-system-prompt", SYSTEM],
            capture_output=True, text=True, cwd=work, stdin=subprocess.DEVNULL, timeout=600)
        (raw / f"{skill}-{k:02d}-{i}.jsonl").write_text(p.stdout + p.stderr)
        events = [json.loads(l) for l in p.stdout.splitlines() if l.startswith("{")]
        result = next((e for e in events if e.get("type") == "result"), None)
        # A finished run ends in a result event; error_max_turns is a normal stop here.
        if result and (result.get("subtype") in ("success", "error_max_turns")):
            return [c["input"].get("skill", "") for e in events if e.get("type") == "assistant"
                    for c in e["message"].get("content", []) if c.get("type") == "tool_use" and c["name"] == "Skill"]
    return None  # invalid run: errored twice


summary = {}
for skill in ("delegate", "write-for-model"):
    ev = json.loads((here / f"{skill}.trigger.json").read_text())
    jobs = [(skill, k, i, e["query"]) for k, e in enumerate(ev) for i in range(runs)]
    with cf.ThreadPoolExecutor(4) as ex:
        sel = list(ex.map(one, jobs))
    rows = []
    for k, e in enumerate(ev):
        r = sel[k * runs:(k + 1) * runs]
        valid = [s for s in r if s is not None]
        hits = sum(any(x.split(":")[-1] == skill for x in s) for s in valid)
        rows.append({"query": e["query"], "should_trigger": e["should_trigger"], "valid": len(valid),
                     "hits": hits, "other_skills": sorted({x for s in valid for x in s if x.split(":")[-1] != skill})})
    summary[skill] = rows
    pos = [r for r in rows if r["should_trigger"]]
    neg = [r for r in rows if not r["should_trigger"]]
    print(f"{label} {skill}: positives {sum(r['hits'] for r in pos)}/{sum(r['valid'] for r in pos)}, "
          f"negatives {sum(r['valid'] - r['hits'] for r in neg)}/{sum(r['valid'] for r in neg)}, "
          f"invalid {sum(runs - r['valid'] for r in rows)}")
    for r in rows:
        if (r["hits"] < r["valid"]) if r["should_trigger"] else r["hits"]:
            print(f"   {r['hits']}/{r['valid']} {'+' if r['should_trigger'] else '-'} {r['query'][:80]} {r['other_skills']}")
(here / "raw" / f"{label}.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))
