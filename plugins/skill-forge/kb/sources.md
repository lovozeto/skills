---
tier: advisory
last_verified: unknown
review_by: 2026-10-22
---

# Credible sources

The set `/refresh-forge-kb` fetches from. URLs marked **(verify)** must be confirmed by the
refresh skill before any entry citing them is promoted above `advisory` — do not treat a
`(verify)` URL as fact.

## Building agents / skills / plugins

| Source | What to fetch | Root (verify exact deep links) |
|---|---|---|
| Anthropic — Claude docs | Model ids, prompting, tool use, agents | https://docs.claude.com |
| Anthropic — Claude Code docs | Skills, plugins, hooks, subagents, settings | https://docs.claude.com/en/docs/claude-code **(verify)** |
| Anthropic — engineering | "Building effective agents" | https://www.anthropic.com/engineering/building-effective-agents **(verify)** |
| agentskills.io | Portable Agent Skills standard (the subset Claude Code extends) | https://agentskills.io **(verify)** |
| OpenAI | Agents SDK, "A practical guide to building agents", prompting | https://platform.openai.com/docs **(verify)** |
| OpenCode | Agent/tooling docs, Zen model catalog (free + paid) | https://opencode.ai **(verify)** |
| Google | Gemini prompting guidance | https://ai.google.dev **(verify)** |
| Moonshot AI | Kimi model docs | (verify canonical docs URL) |
| Agent eval guides | Evaluating agent/skill triggering & task success | (curate; verify each) |
| Matt Pocock — `writing-for-agents` | Context pointers, the two loads (context vs cognitive), information hierarchy, completion criteria, leading words, negation, pruning; `SKILL-MECHANICS.md` for invocation choice | https://github.com/mattpocock/skills (`skills/productivity/writing-for-agents/`); also installed as plugin `mattpocock-skills` |

## UX / interaction

| Source | What to fetch | Root |
|---|---|---|
| Nielsen Norman Group | Usability heuristics, interaction design applicable to wizard/skill design | https://www.nngroup.com **(verify)** |

## Recommended additions (proposed; confirm with the user before adding)
- Model context / MCP specification (for plugins shipping MCP servers).
- A "prompt patterns" source for structured output and tool-use reliability.

## Expiry per file (`review_by`)

Every KB file carries `last_verified` (real date, or `unknown`) and `review_by` in its
frontmatter. `review_by` is set from volatility each time the file is refreshed:

| File | Volatility | `review_by` |
|---|---|---|
| `model-catalog.md` | high (models change monthly) | `last_verified` + 1 month |
| `best-practices/prompting.md` | high | + 1 month |
| `best-practices/skills.md`, `agents.md`, `plugins.md`, `hooks.md` | high (Claude Code ships often) | + 1 month |
| `sources.md` | medium | + 6 months |
| `best-practices/ux-heuristics.md` | low | + 12 months |

The user's session preflight flags any file whose `review_by` has passed. That flag is the
cadence: there is no silent recurring fetch.

## Rules for the refresh skill
- Fetch only with the user's permission (no silent recurring fetch).
- Record **provenance** (source + URL + date) and **tier** for every entry.
- Never populate an entry from memory. If a source cannot be reached, leave the entry
  `advisory (unverified)` and say so.
