"""Compare one model's benchmark results with the other models in a results folder, and
decide whether it should replace the current model for a role.

Each <model>.tsv holds rows: date, model, class, task, seconds, result, note
(class: code | text | fit; result: pass | fail | skip). For each model and task, the rows
of the latest date count and are averaged, so three runs on one day score 0.0–1.0 each.

Decision for a candidate against the current model (one class), in order:
  keep      the candidate does not fit 100% on the GPU, or trails by more than one task
  finalist  either side has fewer than 3 runs per task: run both 3 times, then decide
  replace   it leads by at least one task on average, or ties (within one task) and its
            median time is at most 70% of the current model's
  keep      otherwise

CLI: python3 compare.py <results-dir> <candidate> [--current <model> --class code|text]
"""
import csv
import statistics
import sys
from pathlib import Path


def load(folder):
    """{model: {(class, task): [(result, seconds), ...]}} with only the latest date's rows."""
    raw = {}
    for path in sorted(Path(folder).glob("*.tsv")):
        with path.open(newline="") as fh:
            for row in csv.reader(fh, delimiter="\t"):
                if len(row) < 6 or row[0] == "date":
                    continue
                date, model, cls, task, secs, result = row[:6]
                raw.setdefault(model, {}).setdefault((cls, task), []).append(
                    (date, result, int(float(secs or 0))))
    models = {}
    for model, tasks in raw.items():
        for key, entries in tasks.items():
            latest = max(d for d, _, _ in entries)
            models.setdefault(model, {})[key] = [(r, s) for d, r, s in entries if d == latest]
    return models


def ran(runs):
    return [(r, s) for r, s in runs if r != "skip"]


def score(results, tasks):
    """(mean passes summed over tasks, median seconds, fewest runs on any task)."""
    passes, secs, counts = 0.0, [], []
    for t in tasks:
        runs = ran(results.get(t, []))
        if not runs:
            continue
        passes += sum(r == "pass" for r, _ in runs) / len(runs)
        secs += [s for _, s in runs]
        counts.append(len(runs))
    return passes, (statistics.median(secs) if secs else 0), (min(counts) if counts else 0)


def shared_tasks(models, a, b, cls):
    return sorted(t for t in models[a] if t[0] == cls and ran(models[a][t])
                  and t in models.get(b, {}) and ran(models[b][t]))


def compare(models, candidate):
    lines = []
    cand = models[candidate]
    for cls in sorted({c for c, _ in cand} - {"fit"}):
        own = sorted(t for t in cand if t[0] == cls)
        p, s, _ = score(cand, own)
        lines.append("## %s\n%s: %.1f/%d pass, median %ss (candidate)"
                     % (cls, candidate, p, len([t for t in own if ran(cand[t])]), s))
        for other in sorted(models):
            if other == candidate:
                continue
            shared = shared_tasks(models, candidate, other, cls)
            if not shared:
                continue
            cp, cs, _ = score(cand, shared)
            op, os_, _ = score(models[other], shared)
            verdict = "better" if cp >= op + 1 else "worse" if cp <= op - 1 else "close"
            lines.append("vs %s: %s (%.1f vs %.1f of %d shared; median %ss vs %ss)"
                         % (other, verdict, cp, op, len(shared), cs, os_))
    fit = {t: runs for t, runs in cand.items() if t[0] == "fit"}
    if fit:
        lines.append("## fit\n" + ", ".join("%s %s" % (t[1], runs[-1][0]) for t, runs in sorted(fit.items())))
    return "\n".join(lines)


def decide(models, candidate, current, cls):
    cand = models.get(candidate, {})
    gpu = cand.get(("fit", "gpu"))
    if not gpu or gpu[-1][0] != "pass":
        return "keep %s: %s does not fit 100%% on the GPU (or was not measured)" % (current, candidate)
    shared = shared_tasks(models, candidate, current, cls)
    if not shared:
        return "finalist: no shared %s tasks with %s yet; run both" % (cls, current)
    cp, cs, cruns = score(cand, shared)
    op, os_, oruns = score(models[current], shared)
    if cp < op - 1:
        return "keep %s: %s trails by %.1f tasks" % (current, candidate, op - cp)
    if min(cruns, oruns) < 3:
        return "finalist: run both 3 times (runs so far: %d vs %d)" % (cruns, oruns)
    if cp >= op + 1:
        return "replace %s with %s: %.1f vs %.1f passes" % (current, candidate, cp, op)
    if cp > op - 1 and os_ and cs <= 0.7 * os_:
        return "replace %s with %s: tie (%.1f vs %.1f), median %ss vs %ss" % (current, candidate, cp, op, cs, os_)
    return "keep %s: %.1f vs %.1f passes, median %ss vs %ss" % (current, cp, op, cs, os_)


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) not in (2, 6) or (len(args) == 6 and (args[2], args[4]) != ("--current", "--class")):
        sys.exit(__doc__)
    data = load(args[0])
    if args[1] not in data:
        sys.exit("compare: no results for %s in %s" % (args[1], args[0]))
    print(compare(data, args[1]))
    if len(args) == 6:
        print("\nDecision: " + decide(data, args[1], args[3], args[5]))
