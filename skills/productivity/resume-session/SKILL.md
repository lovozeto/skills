---
name: resume-session
description: Load the session state at the start of a working session. Reads QUICK-STATE.md and orients on what was happening and what comes next.
argument-hint: "[path/to/QUICK-STATE.md]"
---

# resume-session — orient at the start of a session

Complement to `/save-session`. That one writes; this one reads and reorients.

## Steps

1. Find `QUICK-STATE.md`. Check in order:
   - The path given in `$ARGUMENTS` (if provided)
   - The current project root
   - `~/GitHub/QUICK-STATE.md` (global default)

   If none is found, say so and ask where it is. Do not guess.

2. Read the file and present a summary:
   - **Where things were left:** the last task, its status (done / in progress / blocked)
   - **What comes next:** the next step, any blockers flagged
   - **Open PRs or branches:** from the PR-LOG section if present
   - **Active objective:** the session goal, if written

3. Confirm the objective for this session in one sentence.
   If the state is stale (date is more than 3 days old), note it and ask whether to continue
   from there or start fresh.

## Rules

- Read-only. Never edit QUICK-STATE.md from this skill.
- Do not expand into related work not mentioned in the file.
- If the state file is empty or the last session ended without saving, say so directly.
