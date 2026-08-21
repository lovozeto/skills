#!/usr/bin/env python3
"""Universal-dependency preflight hook (template).

Reads the artifact's declared universal dependencies and checks whether each is present on
the machine. It NEVER installs anything. It asks permission by surfacing what is missing and
blocking use until the user resolves it.

Wiring (see hooks.json.tmpl):
  - SessionStart: `python3 preflight-deps.py`        -> emits context listing missing deps.
  - PreToolUse:   `python3 preflight-deps.py --gate` -> denies the tool call while any dep is
                  missing, with a reason telling Claude to ask the user for permission to
                  install (Claude asks; the user installs; this hook never installs).

Declared deps live in `required-deps.json` next to this script:
  [
    {"name": "ffmpeg", "check": "ffmpeg", "explain": "converts audio/video", "install": "brew install ffmpeg"}
  ]
`check` is the executable to look up on PATH. If omitted, `name` is used.
"""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEPS_FILE = os.path.join(HERE, "required-deps.json")


def load_deps():
    try:
        with open(DEPS_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return []
    except (json.JSONDecodeError, OSError):
        return []


def missing_deps(deps):
    missing = []
    for dep in deps:
        check = dep.get("check") or dep.get("name")
        if not check:
            continue
        if shutil.which(check) is None:
            missing.append(dep)
    return missing


def emit_session_start(missing):
    if not missing:
        return
    lines = ["This plugin requires universal dependencies that are NOT installed:"]
    for dep in missing:
        lines.append(
            f"- {dep.get('name')}: {dep.get('explain', 'required tool')}. "
            f"Install hint: {dep.get('install', '(ask the user)')}."
        )
    lines.append(
        "You CANNOT use this plugin until they are installed. Ask the user for permission "
        "to install them (state name, purpose, and command). Never install without an "
        "explicit yes. If the user declines, tell them the plugin cannot be used."
    )
    context = "\n".join(lines)
    out = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }
    print(json.dumps(out))


def emit_gate(missing):
    if not missing:
        return  # allow by default (no output)
    names = ", ".join(d.get("name", "?") for d in missing)
    out = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                f"Missing required dependencies: {names}. This plugin cannot run until they "
                f"are installed. Ask the user for permission to install them; never install "
                f"without an explicit yes."
            ),
        }
    }
    print(json.dumps(out))


def main():
    gate = "--gate" in sys.argv[1:]
    missing = missing_deps(load_deps())
    if gate:
        emit_gate(missing)
    else:
        emit_session_start(missing)


if __name__ == "__main__":
    main()
