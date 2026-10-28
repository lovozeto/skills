---
name: track-work
description: "Keep the GitHub issue and its Projects board column current while you work. Use when starting any change in a repo (find or create its issue, move it to In progress), when opening a PR (Closes #N, In review), when work lands or is dropped (close it, Done), and when you find out-of-scope work (new Backlog issue)."
---

# track-work

The board must show, at any moment, what is being done and what is next. Rules and `gh`
commands: `~/dev/claude-kb/agent-skills/issue-tracker.md` → "Keeping the board current"
(read that section only). Move columns with `track-status <owner/repo> <n> "<column>"`.

## Steps

1. **Before the first edit:** find the issue (`gh issue list --state open --json number,title --search "<words>"`). None: create it with one track label (`dev`, `design`, `discovery`) and one triage label, then use it. Done when the work has an issue number.
2. **Start:** assign it to `@me` and move it to In progress. Done when the board shows it there.
3. **PR:** put `Closes #<n>` in the PR body; move the issue to In review. Done when both are true.
4. **Land or drop:** close the issue with one line (what landed and the PR, or why it was dropped) and move it to Done. Done when it is closed and in Done.
5. **Along the way:** out-of-scope work becomes a new issue in Backlog; a blocker becomes a comment on the issue saying what unblocks it.

Repos without a board: say so and suggest `setup-tracking <owner/repo>`; do not create boards unasked.
Save tokens: ask `gh` only for the fields you need (`--json number,title`).
