---
name: save-session
description: "Keep session state and Claude Code memory current. Use when the user wants to close a session with a state update, log a PR, or reconcile stale memory."
argument-hint: "close | pr | reconcile"
disable-model-invocation: true
---

# memory-keeper

Maintains cross-session working state and Claude Code auto-memory freshness.
Effective skill: writes files. Gate before every write.

Does NOT touch:
- Layer A (identity files: CLAUDE.md, opencode-instructions.md)
- opencode session DB (~/.local/share/opencode/opencode.db)
- Any file inside a castandcrew repo (see scope rule below)

Delegation routing: task-to-model map lives in ~/dev/claude-kb/delegation.md.
Read hardware.md to confirm what is available on this machine before routing.

## Scope rule

If cwd is under ~/GitHub/castandcrew/: output SCOPE_REJECTED and stop.
Do not write any state for company work.

## Subcommand: close

Writes end-of-session state so the next session starts oriented.

Steps:
1. Run: git branch --show-current, git status --short, git log --oneline -5
2. Run: gh pr list --json number,title,state,headRefName --limit 10 (if gh is available)
3. Delegate formatting to Apple FM:
   - Command: ask-apple "<git output>"
   - Task: format into QUICK-STATE.md (max 25 lines, sections: What I did | What is next | Blockers | Branch | Open PRs)
   - QA: verify output has <= 25 lines and contains all four section headers; if not, redo in-context
   - Fallback if ask-apple exits non-zero: format in-context (Sonnet)
4. Write ~/GitHub/QUICK-STATE.md (always, overwrite — do not append)
5. If cwd is a project repo (not ~/GitHub): also write <cwd>/QUICK-STATE.md (overwrite)
6. Show the written content to the user

Never write: company names, castandcrew IP, credentials, content already in CLAUDE.md.

## Subcommand: pr

Appends one row per new PR to the running log.

Steps:
1. Run: gh pr list --json number,title,state,url,headRefName,updatedAt,baseRefName --limit 20
   - If gh is unavailable: output "gh not available — run gh auth login first" and stop
2. Read ~/GitHub/PR-LOG.md to find which PR numbers are already logged
3. Delegate formatting of new entries to Apple FM:
   - Command: ask-apple "<new PRs JSON>"
   - Task: produce one markdown table row per new PR: | date | repo | branch | PR# | title | state |
   - QA: verify each row has 6 pipe-delimited columns; if not, redo in-context
   - Fallback if ask-apple exits non-zero: format in-context
4. Append new rows to ~/GitHub/PR-LOG.md (never overwrite, never rewrite history)
5. Show appended rows to the user

## Subcommand: reconcile

Detects stale or contradictory Claude Code auto-memory. Requires judgment — not delegated to local models.

Steps:
1. Find all memory files: find ~/.claude/projects/*/memory -name "*.md" | sort
2. Read each file and record: name, modified date, cwd it belongs to, key claims
3. For each memory file, check:
   - Is the cwd still an active repo? (ls <cwd>)
   - Is the modified date > 90 days ago with no recent git activity in that repo?
   - Does the content contradict another memory file or the current CLAUDE.md?
4. Produce a report:
   - Section 1: entries proposed for deletion (date + reason)
   - Section 2: entries proposed for update (what changed)
   - Section 3: entries that look current (no action)
5. Present the report. Do not delete or modify anything without explicit user approval.
6. For each approved deletion: use the Bash tool to remove the file, then update MEMORY.md index

Model: claude-haiku-4-5-20251001 (runs as the current session's model tier — no separate subagent needed;
Sonnet handles this subcommand directly if haiku is not the session model).

Cadence: on demand. Run monthly.

**QA contract for delegated outputs**
Every output from ask-apple or ask-local is verified before use:
- Format check: expected structure present (sections, columns)
- Sanity check: no hallucinated content, no credentials, no company names
If a check fails, redo in-context (Sonnet). Do not assume the caller already verified.

**One-task rule (inherited by all subcommands)**
Each subcommand has one task. Return the result or SCOPE_REJECTED.
Never expand scope on your own initiative.
