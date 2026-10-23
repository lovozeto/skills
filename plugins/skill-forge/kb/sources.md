---
tier: advisory
last_verified: 2026-10-23
review_by: 2027-04-23
---

# Credible sources

The set `/refresh-forge-kb` fetches from. URLs marked **(verify)** must be confirmed by the
refresh skill before any entry citing them is promoted above `advisory` — do not treat a
`(verify)` URL as fact.

## Building agents / skills / plugins

URLs confirmed by `/refresh-forge-kb` on 2026-10-23 unless marked **(verify)**.

| Source | What to fetch | URL |
|---|---|---|
| Anthropic — Claude docs | Prompting best practices, models overview | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices · https://platform.claude.com/docs/en/about-claude/models/overview (docs.claude.com redirects here) |
| Anthropic — Claude Code docs | Skills, subagents, plugins (manifest + marketplace reference), hooks | https://code.claude.com/docs/en/skills · /sub-agents · /plugins · /plugins/manifest-reference · /plugins/marketplace-reference · /hooks |
| Anthropic — engineering | Building effective agents (dated note), context engineering, Agent Skills, writing tools, multi-agent research | https://www.anthropic.com/engineering |
| agentskills.io | Portable Agent Skills spec + `skills-ref` validator | https://agentskills.io/specification |
| OpenAI | Prompt engineering, models, agents | https://developers.openai.com/api/docs (platform.openai.com redirects here) |
| OpenAI — Codex | Skills (`agents/openai.yaml`), AGENTS.md | https://learn.chatgpt.com/docs/build-skills · https://learn.chatgpt.com/docs/agent-configuration/agents-md |
| OpenCode | Zen docs (free-model conditions, privacy), live model list, metadata | https://opencode.ai/docs/zen/ · https://opencode.ai/zen/v1/models (authoritative for liveness) · https://models.dev/api.json (metadata; lists retired ids too) |
| Google | Gemini prompting, models, pricing (free tier), rate limits, terms | https://ai.google.dev/gemini-api/docs · https://ai.google.dev/gemini-api/terms |
| Matt Pocock — `writing-for-agents` | Context pointers, two loads, hierarchy, completion criteria, leading words, negation, pruning, invocation | https://github.com/mattpocock/skills (`skills/productivity/writing-for-agents/`, v1.3.1; also plugin `mattpocock-skills`) |
| Moonshot AI | Kimi model docs | (verify canonical docs URL) — not curated 2026-10-23 |
| Agent eval guides | Evaluating agent/skill triggering & task success | (curate; verify each) — not curated 2026-10-23 |

**Measured on this machine (`proven`):** a model is live only if a real call succeeds. The
2026-10-23 benchmark found ids missing from the Zen list that still answer, and ids in
`models.dev` that are retired.

## UX / interaction

| Source | What to fetch | Root |
|---|---|---|
| Nielsen Norman Group | 10 heuristics, wizards, progressive disclosure, confirmation dialogs | https://www.nngroup.com/articles/ten-usability-heuristics/ · /articles/wizards/ · /articles/progressive-disclosure/ · /articles/confirmation-dialog/ |

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
