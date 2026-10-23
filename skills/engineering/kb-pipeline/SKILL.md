---
name: kb-pipeline
description: "Research, update, or refresh a knowledge base. Three mandatory gates: pre-flight, curation, and review. Never writes without confirmation."
argument-hint: "[base] [--topics \"...\"] | --refresh [base]"
allowed-tools: Read, Write, Agent
---

# kb-pipeline — research and maintain a knowledge base

Orchestrates the full pipeline: scout → curate → extract → merge → review.
No knowledge is written to the KB without explicit user confirmation at three gates.

Active KB path: `~/dev/claude-kb/` (default). Set by the active profile in `lobomorir-ai-setup`.

Invoke as:
- `/kb-pipeline [base]` — research a knowledge base (e.g. `apple-hig`, `react-native-core`)
- `/kb-pipeline --refresh [base]` — freshness check for an existing base
- `/kb-pipeline --refresh` — freshness check across all bases

---

## --refresh mode

Read `subagents/kb-freshness.md` (ships with this skill). Invoke an Agent with those
instructions, targeting the base(s) indicated.

All freshness logic lives in that file. Don't reproduce it here.

---

## Research mode

### Step 0 — Pre-flight (MANDATORY GATE)

Before invoking any subagent:

1. Read `~/dev/claude-kb/sources.yml` → find the entry for the requested base.
   Extract: list of sources, `refresh_after_days`, `scope_filter`.
2. Read `~/dev/claude-kb/INDEX.md` → list which files already exist for this base.
3. Present a table:

   | Field | Value |
   |---|---|
   | Base | `[base]` |
   | Files to create or update | (from INDEX.md) |
   | Sources to walk | (from sources.yml) |
   | Refresh threshold | `refresh_after_days` days |
   | Scope filter | (from sources.yml) |

**STOP.** Ask for explicit confirmation. Do not continue without it.

### Step 1 — Scout

Read `subagents/kb-scout.md` (ships with this skill).

For **each source** in the base's source list: invoke an Agent with the kb-scout
instructions, passing: publisher name, portal URL, and scope_filter.

Collect the URL candidate lists from each scout run.

### Step 2 — Curation gate (MANDATORY GATE)

Present the full URL list grouped by source, with one line per URL on what it covers.

**STOP.** Let the user prune. Their judgment on what's worth capturing overrides yours.

### Step 3 — Extract (isolated per source)

Read `subagents/kb-extractor.md` (ships with this skill).

Invoke **one Agent per source, never two sources in the same agent context**.
Each invocation sees exactly one source and writes to `{base}/.raw/{publisher}.md`.

Reason: two publishers in one context get averaged into rules with no clear author.
The isolation is the point — do not skip it to save time.

### Step 4 — Merge

Read `subagents/kb-merge.md` (ships with this skill).

Invoke one Agent with all the `.raw/` intermediates for this base.

### Step 5 — Review gate (MANDATORY GATE)

Present the diff of the merged file against the previous version (if any).
Flag every `⚠️ unresolved conflict` the merge left — do not let them pass unnoticed.

**STOP.** No commit without approval. When conflicts need arbitration, tell the user to run `/arbitrate` (user-invoked).

---

## Hard rules

- Never invent sources that are not in `sources.yml`. If a source is not there, say so.
- If any step fails, report and stop. Never continue to the next step with partial data.
- One base per run. If the user asks for a different base mid-run, redirect them to a new session.
- All subagent instructions are in `subagents/*.md` — read them at runtime, don't reproduce them here.
