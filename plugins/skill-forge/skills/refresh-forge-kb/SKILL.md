---
name: refresh-forge-kb
description: Refresh the skill-forge knowledge base and packaged templates from credible sources (Claude/Anthropic, Claude Code, agentskills.io, OpenAI, OpenCode Zen, Gemini, Kimi, Nielsen Norman, agent eval guides). On-demand and schedulable. Use when the user wants to update best practices, refresh the model catalog, or re-sync the skill-forge KB/templates.
disable-model-invocation: true
argument-hint: "sources or 'all'"
model: opus
allowed-tools: Read, Write, Edit, Bash, Task, WebFetch, WebSearch
---

# refresh-forge-kb — keep the KB and templates current

You are the **master orchestrator** of the KB refresh. You do not fetch and write freely: you
run three gates and delegate each source to a **single-task** curator. The KB is the wizard's
source of truth, so correctness beats coverage.

## Scope & effect
**Effective** (writes to `../../kb/` and `../../assets/templates/`). Every write passes the
review gate and an explicit confirmation. Never fetch on a recurring schedule silently — ask
before each refresh. On-demand; schedulable via `/schedule` (the user opts in).

## Mandatory model
Orchestrator: `opus` (native). Equivalence: closest available reasoning tier from
`../../kb/model-catalog.md`; Claude tier ladder as last resort, stated.

## When to run
When the user's session preflight lists a skill-forge KB file as expired, or when
`forge-wizard` reports an expired KB before building. High-volatility files expire monthly.

## Sources
Read `../../kb/sources.md`. Treat `(verify)` URLs as unconfirmed — confirm the real URL
before promoting any entry above `advisory`.

## The three gates

### Gate 1 — Pre-flight (no writes yet)
- Confirm which sources to refresh (arg or ask). Confirm the user permits web fetches now.
- List exactly which KB files and templates may change. Get the user's OK to proceed.

### Gate 2 — Curation (one single-task curator per source)
For each source, spawn the `source-curator` subagent with that **one** source. It fetches,
extracts findings, and returns them with **provenance** (source + URL + date) and a proposed
`tier`. It never writes to the KB and never populates from memory. If a source is unreachable,
it returns `UNREACHABLE` and the entry stays `advisory (unverified)`.

### Gate 3 — Review (consolidate, tier, write)
- Consolidate findings; resolve conflicts across sources; drop anything without provenance.
- Mark each entry `advisory` or `proven` (`proven` only when verified on this machine).
- Update `../../kb/*` and the `Last updated` column in `../../kb/INDEX.md`.
- For every file you refreshed, set its frontmatter `last_verified` to today and `review_by`
  from the volatility table in `../../kb/sources.md`. A file you could not verify keeps
  `last_verified` unchanged; never move `review_by` forward without checking its sources.
- When best practices changed a template's shape, spawn `template-updater` to update the
  affected file(s) in `../../assets/templates/`.
- Register/refresh a pointer in the user's global `~/dev/claude-kb/INDEX.md` for discovery.
- Show a diff summary and get explicit confirmation before finalizing.

## Subagents (one task each)
| Subagent | Single task |
|---|---|
| `source-curator` | Curate exactly one given source → findings + provenance + proposed tier. |
| `template-updater` | Update one packaged template to match a confirmed KB change. |

## Output
A short report: which sources refreshed, which entries changed and their new tier, which
templates updated, and what stayed `advisory (unverified)` and why. Never claim a source was
verified if it was not reached.
