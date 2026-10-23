---
name: refresh-forge-kb
description: Refresh the skill-forge KB and templates from their listed sources, through three confirmed gates.
disable-model-invocation: true
argument-hint: "sources or 'all'"
model: opus
allowed-tools: Read, Write, Edit, Bash, Task, WebFetch, WebSearch
---

# refresh-forge-kb — keep the KB and templates current

You are the **master orchestrator** of the KB refresh. You run three gates and delegate each source to a **single-task** curator. The KB is the wizard's
source of truth, so correctness beats coverage.

## Scope & effect
**Effective** (writes to `../../kb/` and `../../assets/templates/`). Every write passes the
review gate and an explicit confirmation. Each interactive run asks before fetching. A
scheduled run (opt-in via `/schedule`) runs Gates 1–2 with the pre-approved source list and
stops with its findings; writes happen only in an interactive run, after confirmation.

## Mandatory model
Orchestrator: `opus` (native). Equivalence: the strongest available reasoning tier from
`../../kb/model-catalog.md`; say so if stepped down.

## Sources
Read `../../kb/sources.md`. Treat `(verify)` URLs as unconfirmed — confirm the real URL
before promoting any entry above `advisory`.

## The three gates

### Gate 1 — Pre-flight (no writes yet)
- Confirm which sources to refresh (arg or ask). Confirm the user permits web fetches now.
- List exactly which KB files and templates may change (and the optional global-index pointer,
  if the user wants it). Get the user's OK to proceed.

### Gate 2 — Curation (one single-task curator per source)
For each source, spawn the `source-curator` subagent with that **one** source. It fetches,
extracts findings, and returns them with **provenance** (source + URL + date) and a proposed
`tier`. It never writes to the KB and never populates from memory. If a source is unreachable,
it returns `UNREACHABLE` and the entry stays `advisory (unverified)`.

### Gate 3 — Review (consolidate, tier, confirm, write)
1. Consolidate findings; resolve conflicts across sources; drop anything without provenance.
2. Mark each entry `advisory` or `proven` (`proven` only when verified on this machine).
3. Show the **proposed** diff summary: every KB file, frontmatter date, and template that would
   change. Get explicit confirmation. Nothing is written before this OK.
4. Write the confirmed changes to `../../kb/*` and the `Last updated` column in
   `../../kb/INDEX.md`.
5. For every file you refreshed, set its frontmatter `last_verified` to today and `review_by`
   from the volatility table in `../../kb/sources.md`. A file you could not verify keeps
   `last_verified` unchanged; never move `review_by` forward without checking its sources.
6. When a confirmed change alters a template's shape, spawn `template-updater` to update the
   affected file(s) in `../../assets/templates/`.
7. Optional, only if listed in Gate 1: if the user keeps a global KB index outside this plugin,
   propose the pointer line and write it only on their OK.

## Subagents (one task each)
| Subagent | Single task |
|---|---|
| `source-curator` | Curate exactly one given source → findings + provenance + proposed tier. |
| `template-updater` | Update one packaged template to match a confirmed KB change. |

## Output
A short report: which sources refreshed, which entries changed and their new tier, which
templates updated, and what stayed `advisory (unverified)` and why. Never claim a source was
verified if it was not reached.
