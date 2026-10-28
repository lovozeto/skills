#!/usr/bin/env python3
"""PreToolUse on Agent (and the legacy Task): block launching an agent whose knowledge is stale.

The repo's .claude/agent-team.json maps an agent to its knowledge files, one file each,
never a folder:
  "knowledge": {"ux": {"kb": ["ux/forms"], "repo": ["brand/guidelines"]}}
"kb" refs are global KB files ($CLAUDE_KB_DIR, default ~/dev/claude-kb) without `.md`;
"repo" refs are files under the repo's .claude/knowledge/, without `.md`.
Freshness comes from `kb stale --json`, run in the repo: a mapped file it lists (expired or
without review_by) blocks the launch with the refresh to run. A mapped file that does not
exist blocks too. Files nobody maps never block.
An agent absent from the map passes silently; one mapped to nothing, a machine without the
global KB, or a `kb` that is missing or fails, passes with a note for the main session: the
agent's advice is not KB-backed.
Exit 2 blocks with the stderr reason; an unreadable payload or an internal error exits 0.
"""

import json
import os
import subprocess
import sys

sys.dont_write_bytecode = True  # no __pycache__ inside the plugin
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _shell import agent_name, block, load_config, project_root, read_payload, run


def note(text):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": text}}))
    sys.exit(0)


def stale_refs(project):
    """{ref: reason} from `kb stale --json`, or None when kb is missing or fails."""
    command = os.environ.get("AGENT_TEAM_KB") or "kb"
    try:
        result = subprocess.run([command, "stale", "--json"], cwd=project, capture_output=True,
                                text=True, timeout=8)
        rows = json.loads(result.stdout) if result.returncode == 0 else None
    except (OSError, ValueError, subprocess.SubprocessError):
        return None
    if not isinstance(rows, list):
        return None
    return {row.get("ref", ""): row.get("reason", "stale") for row in rows if isinstance(row, dict)}


def check():
    payload = read_payload()
    if not payload or payload.get("tool_name") not in ("Agent", "Task"):
        return
    config = load_config(payload)
    if config is None:
        return
    agent = (payload.get("tool_input") or {}).get("subagent_type") or ""
    knowledge = {key.lower(): value for key, value in (config.get("knowledge") or {}).items()}
    short = (agent_name(agent) or "").lower()
    if short not in knowledge:
        return
    entry = knowledge[short] or {}
    kb_refs, repo_refs = list(entry.get("kb") or []), list(entry.get("repo") or [])
    if not kb_refs and not repo_refs:
        note(f"{agent} has no knowledge files mapped yet (.claude/agent-team.json): its advice "
             "is not KB-backed, so it says the KB does not cover a topic instead of answering from memory.")

    project = project_root(payload)
    kb_root = os.path.expanduser(os.environ.get("CLAUDE_KB_DIR") or "~/dev/claude-kb")
    if kb_refs and not os.path.isdir(kb_root):
        note(f"The global KB was not found on this machine ({kb_root}): {agent}'s advice is not "
             "KB-backed, so it says the KB does not cover a topic. Set CLAUDE_KB_DIR if the KB lives elsewhere.")

    problems, bases, repo_files = [], set(), False
    for ref in kb_refs:
        if not os.path.isfile(os.path.join(kb_root, ref + ".md")):
            problems.append(f"{ref} is mapped but does not exist in the KB")
    for ref in repo_refs:
        if not os.path.isfile(os.path.join(project, ".claude", "knowledge", ref + ".md")):
            problems.append(f".claude/knowledge/{ref}.md is mapped but does not exist")

    stale = stale_refs(project)
    if stale is None:
        if problems:
            block(f"Blocked: fix the knowledge map of {agent} first: {'; '.join(problems)}.")
        note(f"`kb stale` could not run here, so {agent}'s knowledge freshness is unchecked: "
             "its advice is not KB-backed until it runs.")
    for ref in kb_refs:
        if ref in stale:
            problems.append(f"{ref} ({stale[ref]})")
            bases.add(ref.split("/", 1)[0])
    for ref in repo_refs:
        # A project file is listed as "<project>:<ref>"; the project name depends on the folder.
        hit = next((key for key in stale if ":" in key and key.split(":", 1)[1] == ref), None)
        if hit:
            problems.append(f".claude/knowledge/{ref}.md ({stale[hit]})")
            repo_files = True
    if problems:
        steps = []
        if bases:
            steps.append(f"run /knowledge-base:kb-pipeline --refresh {' '.join(sorted(bases))} (it asks before writing)")
        if repo_files or not bases:
            steps.append("review those repo files and update their review_by")
        refresh = " and ".join(steps)
        block(f"Blocked: refresh the knowledge of {agent} first: {'; '.join(problems)}. "
              f"To refresh, {refresh}, then run {agent} again.")


if __name__ == "__main__":
    run(check)
