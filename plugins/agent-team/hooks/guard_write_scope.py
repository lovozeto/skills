#!/usr/bin/env python3
"""PreToolUse on Edit, Write and NotebookEdit: keep each agent inside its write scope.

Scopes live in the repo's .claude/agent-team.json under "write_scopes" (agent name -> globs
relative to the repo root; `**` crosses folders, `*` does not, a leading `!` excludes).
The agent comes from the payload's `agent_type`, with the plugin prefix dropped.
The main session and agents without an entry are not restricted; a repo without
agent-team.json is not touched.
reference-scout also may only add `proposed` entries to the reference board (Edit only).
Exit 2 blocks with the stderr reason; an unreadable payload or an internal error exits 0.
"""

import os
import re
import sys

sys.dont_write_bytecode = True  # no __pycache__ inside the plugin
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _shell import agent_name, block, load_config, project_root, read_payload, run


def glob_regex(pattern):
    parts = re.split(r"(\*\*/?|\*|\?)", pattern)
    pieces = {"**/": "(?:.*/)?", "**": ".*", "*": "[^/]*", "?": "[^/]"}
    return re.compile("".join(pieces.get(p, re.escape(p)) for p in parts) + r"\Z")


def in_scope(relative, globs):
    """Inside when a glob matches and no `!` glob (an exclusion) does."""
    excluded = [g[1:] for g in globs if g.startswith("!")]
    included = [g for g in globs if not g.startswith("!")]
    return (any(glob_regex(g).match(relative) for g in included)
            and not any(glob_regex(g).match(relative) for g in excluded))


def check():
    payload = read_payload()
    if not payload or payload.get("tool_name") not in ("Edit", "Write", "NotebookEdit"):
        return
    config = load_config(payload)
    if config is None:
        return
    agent = agent_name(payload.get("agent_type"))
    scopes = config.get("write_scopes") or {}
    if agent not in scopes:
        return
    tool_input = payload.get("tool_input") or {}
    path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    root = project_root(payload)
    # realpath resolves symlinks, so a link inside a scope cannot point out of it.
    relative = os.path.relpath(os.path.realpath(os.path.join(root, path)), root)
    if relative == ".." or relative.startswith("../") or not in_scope(relative, scopes[agent]):
        allowed = ", ".join(scopes[agent]) or "nothing (read-only agent)"
        block(f"Blocked: {agent} may only write {allowed}; "
              f"{relative} is outside its scope. Return the change to the orchestrator instead.")
    if agent == "reference-scout":
        check_proposals_only(payload.get("tool_name"), tool_input)


STATUS = re.compile(r"^\s*-?\s*\*{0,2}Status:\*{0,2}\s*(.*?)\s*$", re.MULTILINE | re.IGNORECASE)


def check_proposals_only(tool, tool_input):
    """reference-scout may only add `proposed` entries: every status in the old text must
    survive unchanged, and any new status must be `proposed`. Writing the whole file is off."""
    if tool != "Edit":
        block("Blocked: reference-scout adds entries to the reference board with Edit only.")
    remaining = STATUS.findall(tool_input.get("new_string") or "")
    for status in STATUS.findall(tool_input.get("old_string") or ""):
        if status not in remaining:
            block("Blocked: reference-scout may not change an existing status on the reference board; "
                  "approving and rejecting are the owners' call.")
        remaining.remove(status)
    if any(status.lower() != "proposed" for status in remaining):
        block("Blocked: reference-scout may only add entries with Status: proposed.")


if __name__ == "__main__":
    run(check)
