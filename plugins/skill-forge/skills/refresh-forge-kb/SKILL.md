---
name: refresh-forge-kb
description: Refresh the skill-forge KB and templates from their listed sources, through three confirmed gates.
disable-model-invocation: true
argument-hint: "sources or 'all'"
model: opus
allowed-tools: Read, Agent
---

# refresh-forge-kb — keep the KB and templates current

You are the **master orchestrator** of the KB refresh. You run three gates and delegate each source to a **single-task** curator. The KB is the wizard's
source of truth, so correctness beats coverage.

## Scope & effect
**Effective** (writes to `<plugin_root>/kb/` and `<plugin_root>/assets/templates/`). Every write passes the
review gate and an explicit confirmation. Each run asks before fetching; there is no
scheduled or silent fetch (the SessionStart expiry flag is the only cadence).

## Mandatory model
Orchestrator: `opus` (native). Reason: it resolves conflicts between sources and assigns tiers;
a wrong KB entry misleads the wizard. Cross-provider (advisory): see the Orchestrator row in
`<plugin_root>/kb/model-catalog.md`. If opus is unavailable, step along the Claude ladder and say so.

## Sources
First resolve the plugin root to an absolute path (the skill-forge plugin folder; this file is `<root>/skills/refresh-forge-kb/SKILL.md`, and `<root>` holds `kb/`) and
use it for every path below and in every subagent brief; subagents do not run from this folder.
Read `<plugin_root>/kb/sources.md`. Treat `(verify)` URLs as unconfirmed — confirm the real URL
before promoting any entry above `advisory`.

## The three gates

### Gate 1 — Pre-flight (no writes yet)
- Confirm which sources to refresh (arg or ask). Confirm the user permits web fetches now.
- List exactly which KB files and templates may change (and the optional global-index pointer,
  if the user wants it). Get the user's OK to proceed.

### Gate 2 — Curation (one single-task curator per source)
For each source, spawn the `skill-forge:source-curator` subagent with that **one** source; spawn all
curators in a single message (they are independent). Each brief contains: the source row from
`sources.md` (name, URL, what to fetch), the absolute plugin root, which KB file(s) the findings
would feed, and the return shape from the agent file. It fetches,
extracts findings, and returns them with **provenance** (source + URL + date) and an `advisory`
tier. It never writes to the KB and never populates from memory. If a source is unreachable,
it returns `UNREACHABLE` and the entry stays `advisory (unverified)`.

### Gate 3 — Review (consolidate, tier, confirm, write)
1. Consolidate findings; resolve conflicts across sources; drop anything without provenance.
2. Mark each entry `advisory` or `proven` (`proven` only when verified on this machine).
3. Show the **proposed** diff summary: every KB file, frontmatter date, and template that would
   change. Get explicit confirmation. Nothing is written before this OK.
4. Write the confirmed changes to `<plugin_root>/kb/*` and the `Last updated` column in
   `<plugin_root>/kb/INDEX.md`.
5. For every file you refreshed, set its frontmatter `last_verified` to today and `review_by`
   from the volatility table in `<plugin_root>/kb/sources.md`. A file you could not verify keeps
   `last_verified` unchanged; never move `review_by` forward without checking its sources.
6. When a confirmed change alters a template's shape, spawn one `skill-forge:template-updater` per
   affected template. Brief: absolute template path, the confirmed change, its KB provenance.
7. Optional, only if listed in Gate 1: the user names the global index file. Propose a single
   pointer line to this plugin's `kb/INDEX.md` (never copied content) and write it only on their OK.

## Subagents (one task each)
| Subagent | Single task |
|---|---|
| `skill-forge:source-curator` | Curate exactly one given source → findings + provenance + `advisory` tier. |
| `skill-forge:template-updater` | Update one packaged template to match a confirmed KB change. |

## Output
A short report: which sources refreshed, which entries changed and their new tier, which
templates updated, and what stayed `advisory (unverified)` and why. Never claim a source was
verified if it was not reached.
