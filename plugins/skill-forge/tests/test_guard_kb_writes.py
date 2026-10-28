"""Seam: the PreToolUse hook's decision for writes to the plugin's kb/."""
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
HOOK = PLUGIN / "hooks" / "guard_kb_writes.py"


def decide(path, tool="Write", key="file_path", root=PLUGIN):
    payload = {"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": {key: str(path)}}
    env = dict(os.environ, CLAUDE_PLUGIN_ROOT=str(root))
    out = subprocess.run(["python3", str(HOOK)], input=json.dumps(payload),
                         capture_output=True, text=True, check=True, env=env).stdout
    return json.loads(out)["hookSpecificOutput"]["permissionDecision"] if out.strip() else None


class GuardKb(unittest.TestCase):
    def test_kb_writes_ask(self):
        for tool in ("Write", "Edit", "MultiEdit"):
            self.assertEqual(decide(PLUGIN / "kb" / "INDEX.md", tool), "ask", tool)
        self.assertEqual(decide(PLUGIN / "kb" / "best-practices" / "new.md"), "ask")
        self.assertEqual(decide(PLUGIN / "kb" / "n.ipynb", "NotebookEdit", "notebook_path"), "ask")

    def test_other_paths_pass_silently(self):
        self.assertIsNone(decide(PLUGIN / "README.md"))
        self.assertIsNone(decide(PLUGIN / "kb-notes" / "x.md"))
        self.assertIsNone(decide(PLUGIN / "kb" / "INDEX.md", tool="Read"))

    def test_symlink_into_kb_asks(self):
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp) / "alias"
            link.symlink_to(PLUGIN / "kb")
            self.assertEqual(decide(link / "INDEX.md"), "ask")

    def test_bad_input_is_silent(self):
        out = subprocess.run(["python3", str(HOOK)], input="not json", capture_output=True, text=True)
        self.assertEqual((out.returncode, out.stdout), (0, ""))


if __name__ == "__main__":
    unittest.main()
