#!/usr/bin/env python3
"""PreToolUse guard for skill-forge (a gate, not a sensor).

For Write, Edit, MultiEdit and NotebookEdit whose target path (realpath) is inside this
plugin's own kb/ directory: ask the user to confirm the change was approved. The KB is the
wizard's source of truth; only the refresh-forge-kb review gate should change it.
Everything else passes silently (no output).
"""
import json
import os
import sys

TOOLS = ("Write", "Edit", "MultiEdit", "NotebookEdit")


def kb_dir():
    root = os.environ.get("CLAUDE_PLUGIN_ROOT") or os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))
    return os.path.realpath(os.path.join(root, "kb"))


def main():
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return
    if event.get("tool_name") not in TOOLS:
        return
    tool_input = event.get("tool_input") or {}
    path = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not isinstance(path, str) or not path:
        return
    if not os.path.isabs(path):
        path = os.path.join(event.get("cwd") or os.getcwd(), path)
    target = os.path.realpath(path)
    kb = kb_dir()
    if target == kb or target.startswith(kb + os.sep):
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse", "permissionDecision": "ask",
            "permissionDecisionReason":
                "skill-forge KB write: confirm the change was approved."}}))


if __name__ == "__main__":
    main()
