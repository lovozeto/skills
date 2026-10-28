# knowledge-base

Read, explain, correct, and research the global knowledge base (`~/dev/claude-kb/` by
default, or `$KB_ROOT`) without answering from memory and without unapproved writes.

```bash
/plugin marketplace add lovozeto/skills
/plugin install knowledge-base@lovozeto-skills
```

## What is inside

| Piece | Invocation | What it does |
|---|---|---|
| `ask-knowledge-base` skill | automatic | Explains a KB rule in plain language and cites file, source, date, tier and expiry. Read-only. |
| `update-knowledge-base` skill | automatic | Adds or corrects one rule from a source URL, after you approve the draft; runs `kb lint`. |
| `/knowledge-base:kb-pipeline` | you type it | Researches a whole base (`[base]`) or refreshes expired files (`--refresh [base]`) through three gates: pre-flight, curation, review. |
| `kb-scout` agent | used by kb-pipeline | Lists candidate pages of one source (haiku, writes nothing). |
| `kb-extractor` agent | used by kb-pipeline | Writes one source's rules, each with its URL, to `.raw/` (sonnet). |
| `kb-merge` agent | used by kb-pipeline | Proposes the merged file, tags and `INDEX.md` row (sonnet, writes nothing). |
| `kb-freshness` agent | used by kb-pipeline | Proposes updates for one expired file (sonnet, writes nothing). |

kb-pipeline writes the final KB file and its `INDEX.md` row itself, only after you approve
the review gate. Nothing is committed unless you ask.

## Hooks, in plain terms

- **At session start:** if the `kb` command is missing, you see one line saying so and how
  to fix it; the skills then read `INDEX.md` instead. If `kb` is there, you see nothing.
- **Before a write:** whenever Claude is about to create or edit a file inside the knowledge
  base (outside a `.raw/` folder), Claude Code asks you first. Raw captures in `.raw/` and
  files outside the KB are not affected.

## Requirements

| Dependency | Why |
|---|---|
| A knowledge base at `~/dev/claude-kb/` (or `$KB_ROOT`) with `INDEX.md`, `sources.yml`, `TAXONOMY.md` | what the skills read and write |
| [`kb`](https://github.com/lovozeto/kb) CLI on PATH (recommended) | search, sections, expiry and lint; without it the skills fall back to `INDEX.md` |
| `python3`, `bash` | the hooks |

## Platforms

The skills, agents and hooks run only in Claude Code. In Codex or opencode, use the `kb`
CLI directly (`kb search`, `kb get`, `kb stale`, `kb lint`).

## Environment

| Variable | Effect |
|---|---|
| `KB_ROOT` | knowledge base root (default `~/dev/claude-kb`); used by `kb`, the skills' fallback and the write hook |

## Tests

`tests/run.sh` runs the hook tests (no network).
