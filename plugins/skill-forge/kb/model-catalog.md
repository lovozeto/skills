---
tier: advisory
last_verified: 2026-10-23
review_by: 2026-11-23
---

# Model catalog (Claude-first, cloud only)

Source of truth for the **mandatory model** field. **Claude is the base**; the other providers
keep an artifact's instructions coherent if it runs under ChatGPT, OpenCode, or Gemini.
Goal: **optimize tokens while holding quality** — the cheapest model that clears the bar.
Refreshed 2026-10-23 from Anthropic, OpenAI, OpenCode Zen, and Google docs (`sources.md`).

## Roles
- **Orchestrator** — reasoning, decisions, planning, QA.
- **Worker** — one narrow task; the cheapest model that clears its bar.

## Base — Claude (native)

| Tier | Model id | Price $/MTok in/out | Use |
|---|---|---|---|
| `fable` | `claude-fable-5-1` | 10 / 50 | Top reasoning, long-horizon agentic work; when Opus at high effort falls short |
| `opus` | `claude-opus-5-5` | 4 / 20 | Recommended starting point; orchestrators, architecture, QA |
| `sonnet` | `claude-sonnet-5-5` | 2 / 10 | Speed + intelligence; most workers with judgment |
| `haiku` | `claude-haiku-5-5` | 0.10 / 0.50 | Classification, extraction, routing, high volume |

All: 1M context, 128K output, adaptive thinking (always on for Fable 5.1 and Opus 5.5),
knowledge cutoff Jun 2026. Subagent `model:` accepts `haiku | sonnet | opus | fable | <full
id> | inherit`; a skill's `model:` takes any `/model` value or `inherit` and applies to that turn.

## Cross-provider equivalents (guidance in the artifact's text, never a `model:` value)

| Role | Claude (base) | OpenAI | Gemini | OpenCode Zen (free, `proven` 2026-10-23) |
|---|---|---|---|---|
| Orchestrator | `opus` / `fable` | `gpt-6-astra` | `gemini-4-argon` (paid only) | — (keep orchestration on a paid model) |
| Worker (judgment) | `sonnet` | `gpt-6.1-sol` | `gemini-3.8-flash` | `deepseek-v4.1-flash-free` |
| Worker (light) | `haiku` | `gpt-6-luna` | `gemini-3.1-flash-lite` | `deepseek-v4.1-flash-free` / `beam-free` |
| Worker (images/PDF) | `sonnet` | `gpt-6.1-sol` | `gemini-3.8-flash` | `glm-5.3-flash-free` |

Free tiers: Zen free ids are "limited time" promotions and rotate; Gemini's free tier lets
Google use and human-review prompts. Never route private material to a free model. Kimi
(`kimi-k3`, paid on Zen) is not curated.

## How the wizard uses this
1. Choose the Claude tier for the role and put it in `model:` (with the reason).
2. Add a one-line cross-provider note in the agent body.
3. If the tier does not fit, step along the Claude ladder and say so.

## Maintenance
`/refresh-forge-kb` refreshes ids and prices; a free model is `proven` only after a real call
succeeds on this machine (Zen's list and `models.dev` lag behind reality).
