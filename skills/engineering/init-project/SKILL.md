---
name: init-project
description: Initialize the current repo to work with Claude. Creates ai-deps.yml, project CLAUDE.md, QUICK-STATE.md, and optional KB scaffolding. Use when a repo has no CLAUDE.md or QUICK-STATE.md yet, or the user asks to set up a project for AI-assisted work.
allowed-tools: Read, Write, Bash(cat), Bash(ls), Bash(which), Bash(preflight*)
---

# init-project — initialize a repo for AI-assisted work

Effective skill. Reads the project, proposes the scaffold, writes only after confirmation.

Template location: `~/dev/claude-kb/templates/project-scaffold/` (default, set by profile).
If the template directory does not exist, document what each file should contain rather than
skipping steps.

## Step 1 — Discover (do not assume)

Read what already exists: `package.json`, `pyproject.toml`, `docker-compose.yml`, README,
and any spec file in the root.

Determine:
- Stack (language, frameworks, runtimes)
- Binaries the project actually needs
- Whether there is an authoritative spec document

Done when stack, binaries, and spec each have an answer with its source file, or "none found".

## Step 2 — Propose (GATE)

Present every file you will write: the `ai-deps.yml` content (one line of reasoning per
dependency, and what was inferred from where), the `CLAUDE.md` draft, and ask whether to
create `.claude/knowledge/INDEX.md` and `VERIFIED.md`. Mark any file that already exists; it
is left as is unless the user says to overwrite it.

**STOP.** Do not write anything without confirmation.

## Step 3 — Write

Write, in order:
1. `ai-deps.yml` with the approved dependencies
2. `CLAUDE.md` for the project (from the scaffold template, following its budget note): keep
   only the pointers whose target exists or is created in this step, and delete the rest
   (e.g. the Spec line when there is no spec). Without the template: English, ≤ 40 lines,
   pointers and reasons only
3. `QUICK-STATE.md` (empty — filled at end of each session by `/save-session`)
4. `.claude/knowledge/INDEX.md` if the user said yes in step 2
5. `VERIFIED.md` if the user said yes in step 2

## Step 4 — Verify

Run `which preflight`. If it is missing, say so and point to the setup (`deploy.sh` in the
private setup repo installs it). Otherwise run it and show the full output; if it fails, list
the exact commands to fix each issue.

## Hard rule

Never invent dependencies to fill the template. An empty field is correct when it does not apply.
