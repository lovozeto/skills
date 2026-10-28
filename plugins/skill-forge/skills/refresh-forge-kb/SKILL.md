---
name: refresh-forge-kb
description: Refresh the skill-forge KB (global KB base agent-building) and the packaged templates from their listed sources, through three confirmed gates.
disable-model-invocation: true
argument-hint: "sources or 'all'"
model: opus
allowed-tools: Read, Agent
---

# refresh-forge-kb — keep the agent-building KB and templates current

You are the **master orchestrator** of the KB refresh. You run three gates and delegate each source to a **single-task** curator. The KB is the wizard's
source of truth, so correctness beats coverage.

## Scope & effect
**Effective** (writes to `<kb_dir>`, its `<kb_dir>/../INDEX.md` row if a file is added, and `<plugin_root>/assets/templates/`). `<kb_dir>` is the
`agent-building` folder of the global KB: `${KB_ROOT:-~/dev/claude-kb}/agent-building`, expanded to
an absolute path. The global KB is a separate git repo, so its changes need their own branch and
PR (the user's CONVENTIONS); say so in Gate 1. Every write passes the review gate and an explicit confirmation. Each run asks before fetching; there is no
scheduled or silent fetch (the SessionStart expiry flag is the only cadence, and it does not exist when `kb` is not installed).

## Mandatory model
Orchestrator: `opus` (native). Reason: it resolves conflicts between sources and assigns tiers;
a wrong KB entry misleads the wizard. Cross-provider (advisory): see the Orchestrator row in
`<kb_dir>/model-catalog.md`. If opus is unavailable, step along the Claude ladder and say so.

## Sources
First resolve two absolute paths and use them in every path below and in every subagent brief;
subagents do not run from this folder: `<plugin_root>` (the skill-forge plugin folder; this file is
`<plugin_root>/skills/refresh-forge-kb/SKILL.md`) and `<kb_dir>` (above). If `<kb_dir>` does not
exist, stop and tell the user the KB is not installed.
Read the base `agent-building` in `<kb_dir>/../sources.yml` (the single source registry; `kb search`
does not read it) and each file's `sources:` frontmatter. Treat `(verify)` URLs as unconfirmed — confirm the real URL
before promoting any entry above `advisory`.

## The three gates

### Gate 1 — Pre-flight (no writes yet)
- Report the KB repo's current branch (`git -C <kb_dir> branch --show-current`); if it is `main`, ask
  the user to name a work branch and create it before Gate 3 writes.
- Confirm which sources to refresh (arg or ask). Confirm the user permits web fetches now.
- List exactly which KB files and templates may change (and, if a KB file is added or renamed,
  its `INDEX.md` row). Get the user's OK to proceed.

### Gate 2 — Curation (one single-task curator per source)
For each source, spawn the `skill-forge:source-curator` subagent with that **one** source; spawn all
curators in a single message (they are independent). Each brief contains: the source row from
`sources.yml` (publisher, URL), `<kb_dir>`, which KB file(s) the findings
would feed, and the return shape from the agent file. It fetches,
extracts findings, and returns them with **provenance** (source + URL + date) and an `advisory`
tier. It never writes to the KB and never populates from memory. If a source is unreachable,
it returns `UNREACHABLE` and the entry stays `advisory (unverified)`.

### Gate 3 — Review (consolidate, tier, confirm, write)
1. Consolidate findings; resolve conflicts across sources; drop anything without provenance.
2. Mark each entry `advisory` or `proven` (`proven` only when verified on this machine).
3. Show the **proposed** diff summary: every KB file, frontmatter date, and template that would
   change. Get explicit confirmation. Nothing is written before this OK.
4. Write the confirmed changes to `<kb_dir>/*`, keeping the KB file format (`##` sections with a
   tags comment, one atomic bullet per rule ending in `[publisher: url]`). Run `KB_ROOT=<kb_dir>/.. kb lint`; it must report 0 errors.
5. For every file you refreshed, set its frontmatter `last_verified` to today and `review_by`
   from the volatility table in the KB's `CONVENTIONS.md` (high: +1 month, medium: +6, low: +12;
   models, prompting, hooks, skills, agents and plugins are high, `wizards` is low). A file you
   could not verify keeps `last_verified` unchanged; never move `review_by` forward without
   checking its sources.
6. When a confirmed change alters a template's shape, spawn one `skill-forge:template-updater` per
   affected template. Brief: absolute template path, the confirmed change, its KB provenance.
7. Only if Gate 1 listed it: add or fix the row in `<kb_dir>/../INDEX.md` of a new or renamed KB file, written
   only on the user's OK. Finish by telling the user the KB repo has uncommitted changes that
   need a branch and PR.

## Subagents (one task each)
| Subagent | Single task |
|---|---|
| `skill-forge:source-curator` | Curate exactly one given source → findings + provenance + `advisory` tier. |
| `skill-forge:template-updater` | Update one packaged template to match a confirmed KB change. |

## Output
A short report: which sources refreshed, which entries changed and their new tier, which
templates updated, and what stayed `advisory (unverified)` and why. Never claim a source was
verified if it was not reached.
