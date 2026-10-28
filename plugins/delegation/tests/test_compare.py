"""Seam: compare.py's verdict between a candidate and the baseline models."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "bench"))
from compare import compare, load  # noqa: E402


def write(folder, name, rows):
    (Path(folder) / name).write_text("".join("\t".join(r) + "\n" for r in rows))


class Compare(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        write(self.dir, "base.tsv", [
            ["2026-10-28", "ollama/base", "code", "py", "60", "pass", ""],
            ["2026-10-28", "ollama/base", "code", "rust_bug", "70", "fail", ""],
            ["2026-10-28", "ollama/base", "code", "tsx", "50", "pass", ""],
        ])

    def test_more_passes_on_shared_tasks_is_better(self):
        write(self.dir, "new.tsv", [
            ["2026-11-01", "ollama/new", "code", "py", "20", "pass", ""],
            ["2026-11-01", "ollama/new", "code", "rust_bug", "30", "pass", ""],
            ["2026-11-01", "ollama/new", "code", "tsx", "0", "skip", "missing tsc"],
        ])
        out = compare(load(self.dir), "ollama/new")
        self.assertIn("vs ollama/base: better (2 vs 1 of 2 shared", out)

    def test_latest_row_per_task_counts(self):
        write(self.dir, "new.tsv", [
            ["2026-11-01", "ollama/new", "code", "py", "20", "pass", ""],
            ["2026-11-02", "ollama/new", "code", "py", "25", "fail", ""],
        ])
        self.assertIn("worse (0 vs 1 of 1 shared", compare(load(self.dir), "ollama/new"))

    def test_same_passes_is_equal(self):
        write(self.dir, "new.tsv", [["2026-11-01", "ollama/new", "code", "py", "20", "pass", ""]])
        self.assertIn("equal (1 vs 1 of 1 shared", compare(load(self.dir), "ollama/new"))


if __name__ == "__main__":
    unittest.main()
