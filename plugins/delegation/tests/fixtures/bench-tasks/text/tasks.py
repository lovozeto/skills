"""Test fixture: text tasks in the format bench-model expects (one TSV row per task)."""
import sys

if __name__ == "__main__" and sys.argv[1] == "run":
    if len(sys.argv) > 5:
        open(sys.argv[5], "w").write("rewrite")
    print("T4\t3\tpass\t")
    print("T5\t2\tpass\ttone: human review")
