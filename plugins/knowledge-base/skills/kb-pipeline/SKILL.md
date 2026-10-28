---
name: kb-pipeline
description: "Research a whole topic, or refresh expired files, in the global knowledge base. Three mandatory gates (pre-flight, curation, review); nothing is written to the KB without approval. Not for a single known entry: use update-knowledge-base."
argument-hint: "[base] [--topics \"...\"] | --refresh [base]"
disable-model-invocation: true
model: opus
allowed-tools: Read, Bash(kb *), Agent
---

# kb-pipeline — research and maintain a knowledge base

Orchestrates the full pipeline: scout → curate → extract → merge → review.
Effect: the extractor agents write `.raw/` files into the KB after the pre-flight and curation
gates; the merged KB file and its `INDEX.md` row are written by you only after the review
gate; nothing is committed unless the user asks.

KB root: `${KB_ROOT:-~/dev/claude-kb}` (default `~/dev/claude-kb/`). Expand it to an absolute
path once, at the start, and use that path in every brief.

Invoke as:
- `/knowledge-base:kb-pipeline [base]` — research a knowledge base (e.g. `apple-hig`, `react-native-core`)
- `/knowledge-base:kb-pipeline --refresh [base]` — freshness check for an existing base
- `/knowledge-base:kb-pipeline --refresh` — freshness check across all bases (one agent per file)

## Agents and models

Each step runs a plugin agent through the Agent tool with `subagent_type` set to its
namespaced name. Each agent pins its own model in its frontmatter (workers get the cheapest
tier that clears the bar; this orchestrator keeps the reasoning). Cross-provider equivalents
are advisory, from the skill-forge model catalog.

| Role | `subagent_type` | Model | Why | If run outside Claude (advisory) |
|---|---|---|---|---|
| Orchestrator (this skill) | — | `opus` | gates, conflict surfacing, diff review, final writes | OpenAI `gpt-6-astra` |
| Scout | `knowledge-base:kb-scout` | `haiku` | navigate + list, no synthesis | `gpt-6-luna` |
| Extractor | `knowledge-base:kb-extractor` | `sonnet` | verbatim fidelity to one source | `gpt-6.1-sol` |
| Merge | `knowledge-base:kb-merge` | `sonnet` | must catch real contradictions | `gpt-6.1-sol` |
| Freshness | `knowledge-base:kb-freshness` | `sonnet` | detect content change on fetched pages | `gpt-6.1-sol` |

In every brief, pass absolute paths (KB root, `.raw/` target, the source entry): an agent does
not run from this plugin's folder. Each agent returns its result or `OUT OF SCOPE`; on
`OUT OF SCOPE`, `PORTAL UNREACHABLE` or `SOURCE UNREACHABLE`, report it and stop that branch.

## Reading the KB

Use the `kb` CLI first: `kb search "<words>" --base <base> --json`, `kb get <base>/<file>`
(outline) or `kb get <base>/<file>#<section>`, `kb stale --json`, `kb lint`. Fallback when `kb`
is not on PATH or exits non-zero: read `<KB root>/INDEX.md` and open only the matching file.
A failing `kb` means "the KB could not be read", never "the KB does not cover it".

---

## --refresh mode

1. List expired files: `kb stale --json`. Fallback (see above): read `INDEX.md` and each
   file's `review_by`. Narrow to the requested base.
2. Invoke **one `knowledge-base:kb-freshness` agent per expired file** (never two files, or two
   bases, in one agent context), passing the absolute file path and that base's entry from
   `<KB root>/sources.yml`. The agent is read-only and returns a proposal.
3. **Refresh gate (MANDATORY GATE).** Present, per file: what expired, what changed (old →
   new rule text), dead sources, new pages. **STOP.** Nothing is written without approval.
4. After approval, apply only the approved changes yourself: for each refreshed file set
   file-level `last_verified` to today and `review_by` to today + `refresh_after_days`. Run
   `kb lint` (fallback: say "lint not run"). Report: files touched, rules updated, dead
   sources, new pages pending extraction.

All freshness logic lives in the agent. Don't reproduce it here.

---

## Research mode

### Step 0 — Pre-flight (MANDATORY GATE)

Before invoking any agent:

1. Read `<KB root>/sources.yml` (not indexed by `kb`; read it directly) → find the entry for
   the requested base. Extract: list of sources, `refresh_after_days`, `scope_filter`; a field
   the entry lacks comes from `defaults:`. Pass this merged entry to every later step.
2. List which files already exist for this base: `kb search "<base topic words>" --base <base> --json`,
   then `kb get <base>/<file>` for a file's outline. Fallback (see above): `INDEX.md`.
3. Present a table:

   | Field | Value |
   |---|---|
   | Base | `[base]` |
   | Files to create or update | (from step 2) |
   | Sources to walk | (from sources.yml) |
   | Refresh threshold | `refresh_after_days` days |
   | Scope filter | (from sources.yml) |

**STOP.** Ask for explicit confirmation. Do not continue without it.

### Step 1 — Scout

For **each source** in the base's source list: invoke `knowledge-base:kb-scout`, passing
publisher name, portal URL, and `scope_filter`.

Collect the URL candidate lists from each scout run. Done when every source returned a table, `PORTAL UNREACHABLE`, or `OUT OF SCOPE`.

### Step 2 — Curation gate (MANDATORY GATE)

Present the full URL list grouped by source, with one line per URL on what it covers.

**STOP.** Let the user prune. Their judgment on what's worth capturing overrides yours.

### Step 3 — Extract (isolated per source)

Invoke **one `knowledge-base:kb-extractor` agent per source, never two sources in the same
agent context**. Each invocation sees exactly one source (its approved URLs) and writes to the
absolute path `<KB root>/{base}/.raw/{publisher}.md`.

Reason: two publishers in one context get averaged into rules with no clear author.
The isolation is the point — do not skip it to save time.

Done when every source returned a path + count, or `SOURCE UNREACHABLE`.

### Step 4 — Merge (proposal only)

Invoke one `knowledge-base:kb-merge` agent with the absolute paths of all `.raw/` intermediates
for this base, the target file path, `<KB root>/TAXONOMY.md`, the merged `sources.yml` entry from Step 0 (for `refresh_after_days`), the frontmatter values `id: <base>-<file stem>`,
`category: <base>` and `discovered_via: kb-pipeline research run <today>`, and the current `INDEX.md` row
for the file if it exists (read with `kb get <base>/<file>`; fallback `INDEX.md`). It writes
nothing and returns the proposed file (as a diff against the existing one, or in full when
new) and the proposed `INDEX.md` row.

### Step 5 — Review gate (MANDATORY GATE)

Present the proposed diff of the merged file against the previous version (if any) and the
`INDEX.md` row. Flag every `⚠️ unresolved conflict` the merge left — do not let them pass
unnoticed. The user resolves each one here (keep one side, keep both, or drop the rule);
record the choice and its reason in the file.

**STOP.** Nothing is written without approval.

After approval: write the merged file and the `INDEX.md` row yourself (the plugin's hook
asks for confirmation on each write outside `.raw/`; that is expected). Run `kb lint` and
report its output (fallback: say "lint not run"). Report: files written, total rules,
conflicts and how they were resolved. Commit only when the user asks.

---

## Hard rules

- Guardrail: `Write` is not pre-approved, and the plugin's PreToolUse hook asks before any
  write inside the KB outside a `.raw/` folder. The three gates are enforced by these
  instructions plus that prompt.
- Never invent sources that are not in `sources.yml`. If a source is not there, say so.
- If any step fails, report and stop. Never continue to the next step with partial data.
- Research mode: one base per run. If the user asks for a different base mid-run, redirect them to a new session.
- All agent instructions live in the plugin's `agents/*.md` — don't reproduce them here.
