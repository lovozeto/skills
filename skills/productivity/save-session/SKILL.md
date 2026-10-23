---
name: save-session
description: "Keep session state and Claude Code memory current. Use when closing a session (QUICK-STATE.md must be updated before ending), when the user wants to log a PR, or to reconcile stale memory."
argument-hint: "close | pr | reconcile"
---

# save-session

Maintains cross-session working state, the repo's `CLAUDE.md`, and Claude Code auto-memory.
Effective skill: writes files. Show every write to the user and wait for their OK first.

Out of reach for this skill:
- The global and profile `CLAUDE.md` (`~/.claude/CLAUDE.md`, `profiles/*/CLAUDE.md`) and
  `opencode-instructions.md`. Only a repo's own `CLAUDE.md` is edited, through `doc-pruner`.
- The opencode session DB (`~/.local/share/opencode/opencode.db`).
- Any file inside a castandcrew repo (see scope rule).

Format in-context and skip `/delegate` here: the outputs are tiny and may be private.

## Scope rule

If cwd is under `~/GitHub/castandcrew/`: output `SCOPE_REJECTED` and stop. Company work keeps
no state here.

## Subcommand: close

Writes end-of-session state so the next session starts oriented, and keeps the repo's
`CLAUDE.md` lean.

1. Set `repo` = `git rev-parse --show-toplevel`. If cwd is not inside a git repo, write only
   `~/GitHub/QUICK-STATE.md` and skip steps 3–4. Run `git branch --show-current`,
   `git status --short`, `git log --oneline -5`, and
   `gh pr list --json number,title,state,headRefName --limit 10` (skip if `gh` is missing).
2. Draft `QUICK-STATE.md`: at most 25 lines, sections **What I did · What is next ·
   Blockers · Branch · Open PRs**. NEVER write credentials, company names, castandcrew IP, or
   anything already in `CLAUDE.md`: `QUICK-STATE.md` is plain text that is often committed.
   Done when all five sections are present and the draft is ≤ 25 lines.
3. Find the previous close. This assumes `QUICK-STATE.md` is committed with each session's
   work: `base` = `git log -1 --format=%H -- QUICK-STATE.md`. If the file was never committed
   or is gitignored, `base` = `none`, with that reason.
4. If `<repo>/CLAUDE.md` exists, spawn a general-purpose subagent with the Agent tool,
   `model: sonnet` (judgment work; equivalence: the strongest mid tier, under Codex
   `gpt-6.1-sol`; never a free delegated model, since a repo's `CLAUDE.md` may be private).
   Brief: "Read and follow `<absolute path of this skill's folder>/subagents/doc-pruner.md`.
   Read-only: do not use Write or Edit. repo=`<repo>`. base=`<sha or none: reason>`.
   session_rules=`<project rules this session established, one per line, or none>`." If there
   is no `CLAUDE.md`, recommend the user run `/init-project` and continue. Done when doc-pruner
   returned `PROPOSED`, `NO CHANGES`, `NO CLAUDE.md`, or `OUT OF SCOPE`, or `/init-project` was
   recommended.
5. Ask for two approvals: the `QUICK-STATE.md` draft, and doc-pruner's change list (when it
   returned `PROPOSED`), showing each `move` with its target file and the text to append. If
   the user approves only some changes, apply just those to the current `CLAUDE.md` and
   ignore `proposed_file`. Done when each draft is approved, partly approved, or declined.
6. Write what was approved: `<repo>/QUICK-STATE.md` (overwrite); `~/GitHub/QUICK-STATE.md`
   (overwrite with the same approved draft) when `<repo>` is not `~/GitHub`; the approved
   `CLAUDE.md` changes; and, for each approved `move`, append the line to its target file
   (create it if missing).
7. Show the user what was written, and remind them to commit `QUICK-STATE.md` with this
   session's work: the next doc-pruner diff starts from that commit. Done when every approved
   file is written and shown.

## Subcommand: pr

Appends one row per new PR to the running log.

1. Run `gh pr list --json number,title,state,url,headRefName,updatedAt,baseRefName --limit 20`.
   If `gh` is unavailable: output `gh not available — run gh auth login first` and stop.
2. Read `~/GitHub/PR-LOG.md` to find which PR numbers are already logged.
3. Draft one table row per new PR: `| date | repo | branch | PR# | title | state |`, with
   date = `updatedAt` as YYYY-MM-DD and repo = `gh repo view --json name -q .name`.
   Done when every row has 6 pipe-delimited columns.
4. Show the drafted rows and wait for an OK.
5. Append the approved rows to `~/GitHub/PR-LOG.md`; never overwrite or rewrite existing rows.
   Done when the approved rows are appended.

## Subcommand: reconcile

Detects stale or contradictory Claude Code auto-memory. Runs in the session's model.

1. Find all memory files: `find ~/.claude/projects/*/memory -name "*.md" | sort`.
2. Read each file and record: name, modified date, the cwd it belongs to, key claims.
3. For each memory file, check:
   - Is the cwd still an active repo? (`ls <cwd>`)
   - Is it older than 90 days with no recent git activity in that repo?
   - Does it contradict another memory file or the current `CLAUDE.md`?
4. Report three sections: proposed deletions (date + reason), proposed updates (what
   changed), current (no action).
5. Present the report and wait for explicit approval of each deletion or update.
6. For each approved deletion, remove the file; for each approved update, edit the file. Then
   update the `MEMORY.md` index. Done when every approved item is applied.

Cadence: on demand; monthly is a good rhythm.

## One-task rule (inherited by all subcommands)

Each subcommand has one task. Return the result or `SCOPE_REJECTED`. Never expand scope on
your own initiative.
