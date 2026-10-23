---
name: update-knowledge-base
description: "Add or correct a single KB entry from a known source, without running the full pipeline. Use when you know a rule is wrong, outdated, or missing — and you have the source URL."
argument-hint: "[topic] [--url <source-url>]"
allowed-tools: Read, Write
---

# update-knowledge-base — manual KB entry update

For surgical updates: one rule, one verified source. Not a pipeline replacement.

Use `/kb-pipeline` when you want to research an entire topic area from scratch.
Use this when you know exactly what changed and where.

## When it applies

- A rule you rely on is wrong and you know the correct source.
- A publisher updated a specific page and you want to capture the change now.
- You learned something session-specific that should go in the KB.

## Steps

1. **Identify the target KB file.** Read `~/dev/claude-kb/INDEX.md` (default KB path, set by
   active profile) to find which file covers the topic. If none does, say so — this may
   require running `/kb-pipeline` to create a new base first.

2. **Read the source.** Open the URL provided in `--url`. If no URL was given, ask for it.
   Do not write from memory — a KB entry without a source is noise.

3. **Draft the update** in the same format as the existing file:
   - Rule in one verifiable sentence + [exact URL]
   - `last_verified: today's date`
   - If the rule already exists: show what changes (old → new)
   - If it is new: show where in the file it would go

4. **Gate.** Present the draft. **STOP.** Do not write without explicit approval.

5. **Write** the approved change to the KB file. Update `last_verified` on the entry. If the
   file has a `review_by`, leave it: one entry verified is not the whole file verified.
   Do not change any other entry in the file.

## Hard rules

- One entry per invocation. If the update touches more than one rule, split into separate calls.
- `tier: advisory` unless the user explicitly promotes it. Only a human who ran the command
  can set a rule to `proven`.
- Never remove a rule — mark it as superseded with a note and the replacement rule below it.
  Deletion destroys the audit trail.
- Do not edit `INDEX.md` — only add or update entries within existing KB files.
