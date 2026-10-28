"""Compare one model's benchmark results against every other model in a results folder.

Each <model>.tsv holds rows: date, model, class, task, seconds, result, note
(result: pass | fail | skip). For each model and task the latest row counts.
A candidate is better / equal / worse than another model by passes on the tasks both ran;
speed (median seconds) breaks no ties, it is reported next to the verdict.

CLI: python3 compare.py <results-dir> <candidate-model>
"""
import csv
import statistics
import sys
from pathlib import Path


def load(folder):
    """{model: {(class, task): (result, seconds)}} keeping the latest row per task."""
    models = {}
    for path in sorted(Path(folder).glob("*.tsv")):
        with path.open(newline="") as fh:
            for row in csv.reader(fh, delimiter="\t"):
                if len(row) < 6 or row[0] == "date":
                    continue
                date, model, cls, task, secs, result = row[:6]
                models.setdefault(model, {})[(cls, task)] = (result, int(float(secs or 0)))
    return models


def summary(results, tasks):
    ran = [results[t] for t in tasks if t in results and results[t][0] != "skip"]
    passes = sum(1 for r, _ in ran if r == "pass")
    secs = statistics.median([s for _, s in ran]) if ran else 0
    return passes, len(ran), secs


def compare(models, candidate):
    lines = []
    cand = models[candidate]
    for cls in sorted({c for c, _ in cand}):
        lines.append("## %s" % cls)
        tasks = sorted(t for t in cand if t[0] == cls)
        p, n, s = summary(cand, tasks)
        lines.append("%s: %d/%d pass, median %ss (candidate)" % (candidate, p, n, s))
        for other in sorted(models):
            if other == candidate:
                continue
            shared = [t for t in tasks if t in models[other]
                      and models[other][t][0] != "skip" and cand[t][0] != "skip"]
            if not shared:
                continue
            cp, _, cs = summary(cand, shared)
            op, on, os_ = summary(models[other], shared)
            verdict = "better" if cp > op else "worse" if cp < op else "equal"
            lines.append("vs %s: %s (%d vs %d of %d shared; median %ss vs %ss)"
                         % (other, verdict, cp, op, on, cs, os_))
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    data = load(sys.argv[1])
    if sys.argv[2] not in data:
        sys.exit("compare: no results for %s in %s" % (sys.argv[2], sys.argv[1]))
    print(compare(data, sys.argv[2]))
