#!/usr/bin/env python3
"""PreToolUse guard for knowledge-base (a gate, not a sensor).

For Write, Edit, MultiEdit and NotebookEdit: when the target path (realpath) is inside the
global KB root (realpath of ${KB_ROOT:-$HOME/dev/claude-kb}) and not inside a `.raw/` folder,
ask the user. KB files are knowledge every session trusts; a write there must follow an
approved gate. `.raw/` intermediates (kb-extractor output) pass silently, and so does every
path outside the KB.
"""
import json
import os
import sys

TOOLS = ("Write", "Edit", "MultiEdit", "NotebookEdit")


def kb_root():
    root = os.environ.get("KB_ROOT") or os.path.join(os.path.expanduser("~"), "dev", "claude-kb")
    return os.path.realpath(os.path.expanduser(root))


def main():
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return
    if event.get("tool_name") not in TOOLS:
        return
    tool_input = event.get("tool_input") or {}
    path = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not path:
        return
    path = os.path.expanduser(path)
    if not os.path.isabs(path):
        path = os.path.join(event.get("cwd") or os.getcwd(), path)
    target, root = os.path.realpath(path), kb_root()
    if os.path.commonpath([target, root]) != root:
        return
    if ".raw" in os.path.relpath(target, root).split(os.sep)[:-1]:
        return
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse", "permissionDecision": "ask",
        "permissionDecisionReason": "This writes to the knowledge base (%s) outside .raw/; "
        "allow it only if the user approved this change at a gate." % target}}))


if __name__ == "__main__":
    main()
