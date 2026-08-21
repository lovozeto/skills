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

## UX / interaction

| Source | What to fetch | Root |
|---|---|---|
| Nielsen Norman Group | Usability heuristics, interaction design applicable to wizard/skill design | https://www.nngroup.com **(verify)** |

## Recommended additions (proposed; confirm with the user before adding)
- Model context / MCP specification (for plugins shipping MCP servers).
- A "prompt patterns" source for structured output and tool-use reliability.

## Rules for the refresh skill
- Fetch only with the user's permission (no silent recurring fetch).
- Record **provenance** (source + URL + date) and **tier** for every entry.
- Never populate an entry from memory. If a source cannot be reached, leave the entry
  `advisory (unverified)` and say so.
