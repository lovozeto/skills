---
name: init-project
description: Initialize a repo for AI-assisted work (ai-deps.yml, CLAUDE.md, QUICK-STATE.md). Use when a repo has no CLAUDE.md or QUICK-STATE.md yet, or the user asks to set up a project for Claude.
allowed-tools: Read, Write, Bash(cat), Bash(ls), Bash(which), Bash(preflight*)
---

# init-project — initialize a repo for AI-assisted work

Effective skill. Reads the project, proposes the scaffold, writes only after confirmation.

Template location: `~/dev/claude-kb/templates/project-scaffold/` (default, set by profile).
If the template directory does not exist, say so in step 2 and draft each file from the
fallback given beside it in step 3.

## Step 1 — Discover (do not assume)

Read what already exists: `package.json`, `pyproject.toml`, `docker-compose.yml`, README,
any spec file in the root, and whether `CLAUDE.md`, `QUICK-STATE.md`, `ai-deps.yml`,
`.claude/knowledge/INDEX.md`, or `VERIFIED.md` already exist.

Determine:
- Stack (language, frameworks, runtimes)
- Binaries the project actually needs
- Whether there is an authoritative spec document

Done when stack, binaries, and spec each have an answer with its source file, or "none found".

## Step 2 — Propose (GATE)

First ask whether to create `.claude/knowledge/INDEX.md` and `VERIFIED.md`. Then present every
file you will write: the `ai-deps.yml` content (one line of reasoning per dependency, and what
was inferred from where) and the final `CLAUDE.md` draft, with pointers and rules that depend
on a declined file removed. Mark any file that already exists; it is left as is unless the
user says to overwrite it. Done when the user approved or declined each listed file.

**STOP.** Do not write anything without confirmation.

## Step 3 — Write

Write, in order:
1. `ai-deps.yml` with the approved dependencies
2. `CLAUDE.md`: the draft approved in step 2, verbatim. (Built from the scaffold template,
   following its budget note: only pointers whose target exists or is created here. Without
   the template: English, ≤ 40 lines, pointers and reasons only.)
3. `QUICK-STATE.md` from the template skeleton, filled later by `/save-session close`
   (without the template: the five headings What I did · What is next · Blockers · Branch ·
   Open PRs)
4. `.claude/knowledge/INDEX.md` if the user said yes in step 2 (without the template: a table
   File · Purpose · review_by, and the rule that entries are `tier: advisory`)
5. `VERIFIED.md` if the user said yes in step 2 (without the template: Open and Proven
   sections; a row is proven only with the command and its raw output)

Done when every approved file is written.

## Step 4 — Verify

Run `which preflight`. If it is missing, say so and point to the setup (`deploy.sh` in the
private setup repo installs it). Otherwise run it and show the full output; if it fails, list
the exact commands to fix each issue. Done when the preflight output is shown, or its
absence is reported.

## Hard rule

Never invent dependencies to fill the template. An empty field is correct when it does not apply.
