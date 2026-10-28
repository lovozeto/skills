#!/usr/bin/env python3
"""SessionStart: in a repo with .claude/agent-team.json, name any missing dependency.

Silent when the repo is not set up for agent-team or when everything is present. It never
installs anything: it tells the session what is missing and what it costs.
"""

import os
import shutil
import sys

sys.dont_write_bytecode = True  # no __pycache__ inside the plugin
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _shell import load_config, read_payload, run

DEPENDENCIES = (
    ("gh", "GitHub CLI: run-task opens and labels the ticket issues", "brew install gh"),
    ("kb", "knowledge CLI: guard_knowledge checks freshness with `kb stale`", "the kb repo's README"),
)


def check():
    payload = read_payload() or {}
    if load_config(payload) is None:
        return
    missing = [f"- `{name}` ({why}); install: {how}" for name, why, how in DEPENDENCIES
               if not shutil.which(name)]
    if missing:
        print("agent-team: this repo uses run-task, but some tools are missing. Tell the owner and "
              "ask before installing anything:\n" + "\n".join(missing))


if __name__ == "__main__":
    run(check)
