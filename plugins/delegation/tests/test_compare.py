"""Seam: compare.py's scores and decision between a candidate and the current model."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "bench"))
from compare import compare, decide, load  # noqa: E402


def write(folder, name, rows):
    (Path(folder) / name).write_text("".join("\t".join(r) + "\n" for r in rows))


def rows(model, date, cls, results):
    """results: {task: [(result, secs), ...]} one tuple per run."""
    return [[date, model, cls, t, str(s), r, ""] for t, runs in results.items() for r, s in runs]


class Compare(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        write(self.dir, "cur.tsv", rows("ollama/cur", "2026-10-28", "code",
              {"py": [("pass", 60)], "rust_bug": [("fail", 70)], "tsx": [("pass", 50)]}))

    def test_more_passes_on_shared_tasks_is_better(self):
        write(self.dir, "new.tsv", rows("ollama/new", "2026-11-01", "code",
              {"py": [("pass", 20)], "rust_bug": [("pass", 30)], "tsx": [("skip", 0)]}))
        self.assertIn("vs ollama/cur: better (2.0 vs 1.0 of 2 shared", compare(load(self.dir), "ollama/new"))

    def test_runs_on_the_latest_date_are_averaged(self):
        write(self.dir, "new.tsv", rows("ollama/new", "2026-10-01", "code", {"py": [("fail", 9)]})
              + rows("ollama/new", "2026-11-01", "code", {"py": [("pass", 20), ("fail", 25), ("pass", 22)]}))
        self.assertIn("(0.7 vs 1.0 of 1 shared", compare(load(self.dir), "ollama/new"))

    def test_one_screening_run_is_never_enough_to_replace(self):
        new = rows("ollama/new", "2026-11-01", "code", {"py": [("pass", 20)], "rust_bug": [("pass", 30)], "tsx": [("pass", 9)]})
        write(self.dir, "new.tsv", new + rows("ollama/new", "2026-11-01", "fit", {"gpu": [("pass", 0)]}))
        self.assertTrue(decide(load(self.dir), "ollama/new", "ollama/cur", "code").startswith("finalist"))

    def test_three_runs_and_one_more_pass_replaces(self):
        three = lambda r, s: [(r, s)] * 3
        write(self.dir, "cur.tsv", rows("ollama/cur", "2026-11-01", "code",
              {"py": three("pass", 60), "rust_bug": three("fail", 70), "tsx": three("pass", 50)}))
        write(self.dir, "new.tsv", rows("ollama/new", "2026-11-01", "code",
              {"py": three("pass", 80), "rust_bug": three("pass", 90), "tsx": three("pass", 70)})
              + rows("ollama/new", "2026-11-01", "fit", {"gpu": [("pass", 0)]}))
        self.assertTrue(decide(load(self.dir), "ollama/new", "ollama/cur", "code").startswith("replace"))

    def test_clearly_worse_screening_is_dropped(self):
        write(self.dir, "new.tsv", rows("ollama/new", "2026-11-01", "code",
              {"py": [("fail", 20)], "rust_bug": [("fail", 30)], "tsx": [("fail", 9)]})
              + rows("ollama/new", "2026-11-01", "fit", {"gpu": [("pass", 0)]}))
        self.assertTrue(decide(load(self.dir), "ollama/new", "ollama/cur", "code").startswith("keep"))

    def test_decision_without_gpu_fit_keeps_current(self):
        new = rows("ollama/new", "2026-11-01", "code", {"py": [("pass", 20)], "rust_bug": [("pass", 30)], "tsx": [("pass", 9)]})
        write(self.dir, "new.tsv", new + rows("ollama/new", "2026-11-01", "fit", {"gpu": [("fail", 0)]}))
        self.assertTrue(decide(load(self.dir), "ollama/new", "ollama/cur", "code").startswith("keep"))

    def test_decision_close_result_needs_three_runs(self):
        write(self.dir, "new.tsv", rows("ollama/new", "2026-11-01", "code",
              {"py": [("pass", 20)], "rust_bug": [("fail", 30)], "tsx": [("pass", 9)]})
              + rows("ollama/new", "2026-11-01", "fit", {"gpu": [("pass", 0)]}))
        self.assertTrue(decide(load(self.dir), "ollama/new", "ollama/cur", "code").startswith("finalist"))

    def test_decision_tie_and_much_faster_replaces_after_three_runs(self):
        three = lambda r, s: [(r, s)] * 3
        write(self.dir, "cur.tsv", rows("ollama/cur", "2026-11-01", "code",
              {"py": three("pass", 60), "rust_bug": three("fail", 70), "tsx": three("pass", 50)}))
        write(self.dir, "new.tsv", rows("ollama/new", "2026-11-01", "code",
              {"py": three("pass", 20), "rust_bug": three("fail", 30), "tsx": three("pass", 9)})
              + rows("ollama/new", "2026-11-01", "fit", {"gpu": [("pass", 0)]}))
        self.assertTrue(decide(load(self.dir), "ollama/new", "ollama/cur", "code").startswith("replace"))


if __name__ == "__main__":
    unittest.main()
