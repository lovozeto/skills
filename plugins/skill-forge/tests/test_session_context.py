"""Seam: the SessionStart sensor's output for a stale / fresh / missing `kb`."""
import json
import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parent.parent / "hooks" / "session_context.sh"


def run(kb_output=None):
    """Run the hook with a fake `kb` on PATH (or none) and return its stdout."""
    with tempfile.TemporaryDirectory() as tmp:
        if kb_output is not None:
            fake = Path(tmp) / "kb"
            fake.write_text("#!/bin/sh\ncat <<'OUT'\n%s\nOUT\n" % kb_output)
            fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        env = {"PATH": "%s:/usr/bin:/bin" % tmp if kb_output is not None else "/usr/bin:/bin"}
        return subprocess.run(["bash", str(HOOK)], env=env, capture_output=True, text=True).stdout


class SessionContext(unittest.TestCase):
    def test_flags_only_agent_building_files(self):
        out = run("delegation/routing · expired 2026-11-28\n"
                  "agent-building/skills · expired 2026-11-23\n"
                  "agent-building/hooks · missing review_by")
        ctx = json.loads(out)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("agent-building/skills", ctx)
        self.assertIn("agent-building/hooks", ctx)
        self.assertNotIn("delegation", ctx)
        self.assertIn("/refresh-forge-kb", ctx)

    def test_silent_when_nothing_of_ours_is_stale(self):
        self.assertEqual(run("delegation/routing · expired 2026-11-28"), "")
        self.assertEqual(run(""), "")

    def test_silent_when_kb_is_missing(self):
        self.assertEqual(run(None), "")


if __name__ == "__main__":
    unittest.main()
