---
name: init-project
description: Initialize the current repo to work with Claude. Creates ai-deps.yml, project CLAUDE.md, QUICK-STATE.md, and optional KB scaffolding. Manual only.
disable-model-invocation: true
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

## Step 2 — Propose (GATE)

Present the `ai-deps.yml` you will write, with one line of reasoning per dependency.
Flag explicitly what was inferred and where from.

**STOP.** Do not write anything without confirmation.

## Step 3 — Write

Write, in order:
1. `ai-deps.yml` with the approved dependencies
2. `CLAUDE.md` for the project (from the scaffold template)
3. `QUICK-STATE.md` (empty — filled at end of each session by `/save-session`)
4. `.claude/knowledge/INDEX.md` if the project will carry its own KB
5. `VERIFIED.md` if the project has external dependencies that need verification

## Step 4 — Verify

Run `preflight` (should be on PATH after setup). Show the full output. If it fails, list the
exact commands to fix each issue.

## Hard rule

Never invent dependencies to fill the template. An empty field is correct when it does not apply.
