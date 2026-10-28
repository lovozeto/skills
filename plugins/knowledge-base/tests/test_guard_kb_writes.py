"""Seam: the PreToolUse hook's decision for a write tool and a target path."""
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parent.parent / "hooks" / "guard_kb_writes.py"


def decide(path, tool="Write", kb_root=None, cwd=None, key="file_path"):
    env = dict(os.environ)
    if kb_root is not None:
        env["KB_ROOT"] = kb_root
    payload = {"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": {key: path}}
    if cwd:
        payload["cwd"] = cwd
    out = subprocess.run(["python3", str(HOOK)], input=json.dumps(payload), env=env,
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)["hookSpecificOutput"]["permissionDecision"] if out.strip() else None


class Guard(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = os.path.join(self.tmp.name, "kb")
        os.makedirs(os.path.join(self.root, "ux", ".raw"))

    def tearDown(self):
        self.tmp.cleanup()

    def test_kb_file_asks(self):
        for tool in ("Write", "Edit", "MultiEdit"):
            self.assertEqual(decide(self.root + "/ux/forms.md", tool, self.root), "ask", tool)
        self.assertEqual(decide(self.root + "/INDEX.md", kb_root=self.root), "ask")
        self.assertEqual(decide(self.root + "/ux/n.ipynb", "NotebookEdit", self.root,
                                key="notebook_path"), "ask")

    def test_raw_intermediates_pass(self):
        self.assertIsNone(decide(self.root + "/ux/.raw/apple-hig.md", kb_root=self.root))

    def test_outside_kb_passes(self):
        self.assertIsNone(decide(self.tmp.name + "/other/file.md", kb_root=self.root))
        self.assertIsNone(decide(self.root + "-sibling/file.md", kb_root=self.root))

    def test_other_tools_pass(self):
        self.assertIsNone(decide(self.root + "/ux/forms.md", "Read", self.root))

    def test_relative_and_symlinked_paths_resolve(self):
        self.assertEqual(decide("ux/forms.md", kb_root=self.root, cwd=self.root), "ask")
        link = os.path.join(self.tmp.name, "link")
        os.symlink(self.root, link)
        self.assertEqual(decide(link + "/ux/forms.md", kb_root=self.root), "ask")
        self.assertEqual(decide(self.root + "/ux/forms.md", kb_root=link), "ask")

    def test_dotdot_out_of_raw_asks(self):
        self.assertEqual(decide(self.root + "/ux/.raw/../forms.md", kb_root=self.root), "ask")

    def test_bad_input_is_silent(self):
        out = subprocess.run(["python3", str(HOOK)], input="not json",
                             capture_output=True, text=True, check=True).stdout
        self.assertEqual(out, "")


if __name__ == "__main__":
    unittest.main()
