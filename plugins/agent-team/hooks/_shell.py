"""Shared helpers for the agent-team hooks: payload, repo config, Bash command splitting."""

import json
import os
import re
import shlex
import sys

OPERATOR_CHARS = ";&|()<>"
# Words that end a simple command. "$" is what shlex leaves of "$(".
SEPARATORS = {"\n", "$"}
WRAPPERS = {"env", "command", "builtin", "exec", "nohup", "time", "sudo", "xargs"}
# Shell keywords that can sit in front of a command (`then git commit`, `do cat x`).
KEYWORDS = {"if", "then", "else", "elif", "do", "while", "until", "!", "{", "}"}
SHELLS = {"sh", "bash", "zsh"}
ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
HEREDOC = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1[^\n]*\n.*?\n\s*\2\s*(?=\n|$)", re.S)


def run(check):
    """Run a hook's check; any unexpected error lets the call through (fail open)."""
    try:
        check()
    except Exception as error:  # SystemExit from block() is not an Exception
        print(f"guardrail hook error, call allowed: {error!r}", file=sys.stderr)
        sys.exit(0)


def read_payload():
    """Return the hook payload, or None when stdin is not a JSON object."""
    try:
        payload = json.load(sys.stdin)
    except (ValueError, OSError):
        return None
    return payload if isinstance(payload, dict) else None


def block(reason):
    print(reason, file=sys.stderr)
    sys.exit(2)


def tokens(command):
    """Shell words and operators, heredoc bodies removed. None if quoting is broken."""
    command = HEREDOC.sub("<<HEREDOC\n", command)
    lexer = shlex.shlex(command, posix=True, punctuation_chars=OPERATOR_CHARS + "\n")
    lexer.whitespace = " \t\r"
    lexer.whitespace_split = True
    try:
        return list(lexer)
    except ValueError:
        return None


def simple_commands(command):
    """Each simple command as a word list, with leading assignments and wrappers dropped.

    `bash -c "<script>"` is expanded into the commands of <script>.
    """
    words = tokens(command)
    if words is None:
        return None
    result, current = [], []
    for word in words + [";"]:
        # Operators and newline runs ("\n\n" after a blank line) end a command.
        if word in SEPARATORS or (word and set(word) <= set(OPERATOR_CHARS + "\n")):
            if current:
                result.extend(_unwrap(current))
            current = []
        else:
            current.append(word)
    return result


def _unwrap(words):
    while words and (ASSIGNMENT.match(words[0]) or words[0] in WRAPPERS or words[0] in KEYWORDS):
        wrapper = words[0] in WRAPPERS
        words = words[1:]
        while wrapper and words and words[0].startswith("-"):
            words = words[1:]  # the wrapper's own flags (env -i, time -p)
    if len(words) >= 3 and words[0].rsplit("/", 1)[-1] in SHELLS and "-c" in words:
        position = words.index("-c") + 1
        return (simple_commands(words[position]) or []) if position < len(words) else []
    return [words] if words else []


def project_root(payload):
    return os.path.realpath(os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd())


def load_config(payload):
    """The repo's .claude/agent-team.json as a dict, or None: without it the hooks do nothing."""
    path = os.path.join(project_root(payload), ".claude", "agent-team.json")
    try:
        with open(path, encoding="utf-8") as handle:
            config = json.load(handle)
    except (OSError, ValueError):
        return None
    return config if isinstance(config, dict) else None


def agent_name(payload_agent):
    """A launched or running agent's short name: `agent-team:qa` → `qa`."""
    return (payload_agent or "").rsplit(":", 1)[-1] or None
