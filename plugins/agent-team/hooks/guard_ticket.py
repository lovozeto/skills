#!/usr/bin/env python3
"""PreToolUse on agent-team tickets: the in-flight working files (.scratch/**/issues/*.md)
and the GitHub issue's approval label. Repos without .claude/agent-team.json are not touched.

Edit and Write: checks the working file's header (the lines above the first `## ` heading)
as it would look after the edit:
- `Stage:` is one of planned, building, qa, done;
- `Stage: done` needs `QA: PASS` and `VQA: PASS` or `n/a`;
- once a ticket has a QA line, only the qa agent changes it (VQA: only vqa), and those
  agents change nothing else; a verdict (PASS/FAIL) is never written by anyone else.
Bash:
- `gh issue edit … --add-label ready-for-agent` (or `gh issue create … --label
  ready-for-agent`) is the owner's approval, so the owner is asked;
- a command that writes to a working file is blocked, so every change goes through the
  checks above; reading, `git` and `gh` pass, `mv` of a `draft-*` working file to a new
  working file passes (the draft's rename), and `rm` passes once the ticket is done.
Exit 2 blocks with the stderr reason; an "ask" decision goes to stdout as JSON.
An unreadable payload or an internal error exits 0.
"""

import json
import os
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # no __pycache__ inside the plugin
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _shell import agent_name, block, load_config, read_payload, run, simple_commands

APPROVED = "ready-for-agent"
STAGES = {"planned", "building", "qa", "done"}
# A header field in any markdown form: `**QA:** x`, `QA: x`, `- Stage: x`, indented.
FIELD = re.compile(r"^[ \t]*(?:[-*+>][ \t]+)?\*{0,2}(Stage|QA|VQA)\*{0,2}:\*{0,2}[ \t]*(.*?)[ \t]*$", re.M | re.I)
VERDICT_OWNERS = {"QA": "qa", "VQA": "vqa"}
READ_ONLY = {"cat", "head", "tail", "less", "grep", "rg", "wc", "ls", "diff", "stat", "file", "echo", "nl", "uniq"}
INTERPRETERS = {"python", "python3", "node", "perl", "ruby", "deno", "bun"}
GH_FLAGS_WITH_VALUE = {"-R", "--repo", "--hostname"}
SED_WRITE = re.compile(r"(^|[;}\s/])w\s")  # sed's `w file` command writes a file


def is_ticket(path):
    # Real, lower-cased path: macOS names are case-insensitive and symlinks resolve.
    parts = Path(os.path.realpath(path)).parts
    lowered = [part.lower() for part in parts]
    return lowered[-1].endswith(".md") and ".scratch" in lowered and "issues" in lowered[:-1]


def header(text):
    return re.split(r"^## ", text or "", maxsplit=1, flags=re.M)[0]


def fields(text):
    found = {}
    for name, value in FIELD.findall(header(text)):
        found.setdefault(name.upper() if name.lower() != "stage" else "Stage", value)
    return found


def duplicated(text):
    """Header fields written more than once: the gate reads one, so a second is a way around it."""
    names = [name.lower() for name, _ in FIELD.findall(header(text))]
    return sorted({name for name in names if names.count(name) > 1})


def normalized(value):
    return (value or "").strip("`* ").lower()


def first_word(value):
    return normalized(value).split(" ", 1)[0].strip(".,;:—-")


def without_line(text, name):
    return re.sub(rf"^\*{{0,2}}{name}:.*$", "", text, flags=re.M)


def after_edit(tool, tool_input, before):
    """The ticket text after the edit, or None when the edit cannot apply."""
    if tool == "Write":
        return tool_input.get("content") or ""
    old, new = tool_input.get("old_string") or "", tool_input.get("new_string") or ""
    if not old or old not in before:
        return None
    return before.replace(old, new) if tool_input.get("replace_all") else before.replace(old, new, 1)


def ask(reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse", "permissionDecision": "ask", "permissionDecisionReason": reason,
    }}))
    sys.exit(0)


def edits_in_place(words):
    """sed writes the file only with -i / --in-place (also inside -ni, -ie)."""
    return any(w.startswith("--in-place") or (w.startswith("-") and not w.startswith("--") and "i" in w[1:])
               for w in words[1:])


def gh_args(words):
    """gh's arguments with its global flags (`-R owner/repo`) dropped."""
    args, skip = [], False
    for word in words[1:]:
        if skip:
            skip = False
        elif word in GH_FLAGS_WITH_VALUE:
            skip = True
        elif not any(word.startswith(flag + "=") for flag in GH_FLAGS_WITH_VALUE):
            args.append(word)
    return args


def adds_approval(words):
    """`gh issue edit … --add-label …ready-for-agent…`, `gh issue create … --label …`, or a
    `gh api` call that names the label."""
    if not words or os.path.basename(words[0]) != "gh":
        return False
    args = gh_args(words)
    if args[:1] == ["api"]:
        return any(APPROVED in word for word in args)
    words = ["gh"] + args
    if len(words) < 3 or words[1] != "issue":
        return False
    flags = {"edit": ("--add-label",), "create": ("--label", "-l")}.get(words[2], ())
    for index, word in enumerate(words):
        name, _, inline = word.partition("=")
        if name in flags:
            value = inline or (words[index + 1] if index + 1 < len(words) else "")
            if APPROVED in [label.strip() for label in value.split(",")]:
                return True
    return False


def is_done(path):
    try:
        return normalized(fields(Path(path).read_text()).get("Stage")) == "done"
    except OSError:
        return False


def holds_open_ticket(path):
    """A folder (`rm -r .scratch`) that holds a working file not yet at Stage: done."""
    if not os.path.isdir(path):
        return False
    for folder, _, names in os.walk(path):
        for name in names:
            ticket = os.path.join(folder, name)
            if is_ticket(ticket) and not is_done(ticket):
                return True
    return False


def check_bash(command, cwd):
    for words in simple_commands(command) or []:
        if adds_approval(words):
            ask(f"Approve this ticket? Adding the {APPROVED} label lets run-task start it.")
        name = os.path.basename(words[0])
        if words[0] in READ_ONLY or name in ("git", "gh"):
            continue
        if name in INTERPRETERS and any(".scratch" in word.lower() for word in words[1:]):
            block("Blocked: change tickets with the Edit or Write tool, so the ticket gate can check "
                  "the change (a script that names .scratch/ could write one).")
        paths = [w for w in words[1:] if not w.startswith("-")]
        if (words[0] == "mv" and len(paths) == 2 and all(is_ticket(os.path.join(cwd, p)) for p in paths)
                and os.path.basename(paths[0]).startswith("draft-") and not os.path.exists(os.path.join(cwd, paths[1]))):
            continue  # renaming a draft to its issue number keeps its content
        if words[0] == "sed" and not edits_in_place(words) and not any(SED_WRITE.search(w) for w in words[1:]):
            continue
        for word in words:
            target = os.path.join(cwd, word)
            if word.startswith("-"):
                continue
            if words[0] == "rm" and holds_open_ticket(target):
                block(f"Blocked: {word} holds a ticket still in flight; delete a working file only "
                      "once it reaches Stage: done.")
            if is_ticket(target):
                if words[0] == "rm" and is_done(target):
                    continue
                block("Blocked: change tickets with the Edit or Write tool, so the ticket "
                      f"gate can check the change ({word}).")


def check_edit(tool, tool_input, agent):
    path = tool_input.get("file_path") or ""
    if not is_ticket(path):
        return
    ticket = Path(path)
    before_text = ticket.read_text() if ticket.is_file() else ""
    after_text = after_edit(tool, tool_input, before_text)
    if after_text is None:
        return
    before, after = fields(before_text), fields(after_text)
    twice = duplicated(after_text)
    if twice:
        block(f"Blocked: a ticket header holds each field once ({', '.join(twice)} appears twice).")

    for line, owner in VERDICT_OWNERS.items():
        changed = after.get(line) != before.get(line)
        verdict = first_word(after.get(line)) in ("pass", "fail")
        if changed and agent != owner and (line in before or verdict):
            block(f"Blocked: only the {owner} agent changes the {line} line of a ticket "
                  f"(this edit came from {agent or 'the main session'}).")
        if agent == owner and without_line(after_text, line) != without_line(before_text, line):
            block(f"Blocked: the {owner} agent changes only the {line} line of a ticket.")

    stage = normalized(after.get("Stage")) if "Stage" in after else None
    if stage is not None and stage not in STAGES:
        block(f"Blocked: Stage must be one of {', '.join(sorted(STAGES))} (got '{after['Stage']}').")
    if stage == "done":
        if first_word(after.get("QA")) != "pass":
            block("Blocked: a ticket closes (Stage: done) only after QA: PASS. "
                  "Run the qa agent first; its verdict goes in the ticket.")
        if first_word(after.get("VQA")) not in ("pass", "n/a"):
            block("Blocked: a ticket closes only with VQA: PASS, or VQA: n/a when no UI changed.")


def check():
    payload = read_payload()
    if not payload or load_config(payload) is None:
        return
    tool = payload.get("tool_name")
    tool_input = payload.get("tool_input") or {}
    if tool == "Bash":
        check_bash(tool_input.get("command") or "", payload.get("cwd") or os.getcwd())
    elif tool in ("Edit", "Write"):
        check_edit(tool, tool_input, agent_name(payload.get("agent_type")))


if __name__ == "__main__":
    run(check)
