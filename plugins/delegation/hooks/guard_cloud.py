#!/usr/bin/env python3
"""PreToolUse guard for delegation calls (a gate, not a sensor).

For a Bash command that runs ask-opencode:
  - deny a model outside opencode/*-free, google/gemini-*-flash* (free tier) and ollama/*:
    no pay-per-use models;
  - ask the user before --unsafe (it approves every tool permission, destructive ones too).
Everything else passes silently. ask-opencode enforces the same model list and also scans
for data before a cloud call; this hook stops the call before it starts and explains why.
"""
import json
import re
import sys
from fnmatch import fnmatch

ALLOWED = ("opencode/*-free", "google/gemini-*-flash*", "ollama/*")


def decision(kind, reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse", "permissionDecision": kind,
        "permissionDecisionReason": reason}}))


def main():
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return
    if event.get("tool_name") != "Bash":
        return
    command = (event.get("tool_input") or {}).get("command") or ""
    if "ask-opencode" not in command:
        return
    models = re.findall(r"--model[= ]+['\"]?([^\s'\"]+)", command)
    models += re.findall(r"ASK_OPENCODE_MODEL=['\"]?([^\s'\"]+)", command)
    blocked = [m for m in models if not any(fnmatch(m, p) for p in ALLOWED)]
    if blocked:
        decision("deny", "Model %s is not allowed for delegation. Use opencode/*-free, "
                 "google/gemini-*-flash* (free tier) or ollama/*: never a pay-per-use model."
                 % ", ".join(blocked))
    elif re.search(r"(^|\s)--unsafe(\s|$)", command):
        decision("ask", "ask-opencode --unsafe approves every tool permission for the delegated "
                 "model, destructive ones included. Allow it only if the user asked for it.")


if __name__ == "__main__":
    main()
