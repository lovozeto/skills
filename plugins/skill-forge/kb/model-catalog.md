---
tier: advisory
last_verified: unknown
review_by: 2026-10-22
---

# Model catalog (Claude-first, cloud only)

Source of truth for the **mandatory model** field. **Claude is the base**: every
recommendation is expressed as a Claude tier first. The other providers are here so that an
artifact carries **coherent instructions across stacks** — if the person running it uses
ChatGPT or OpenCode instead of Claude, the mandatory-model field maps to a sensible
equivalent. **No local models** (that concern lives separately in `delegate`).

Goal: **optimize tokens while holding quality**. Pick the cheapest capable model per role.

`tier`: `advisory` guides; `proven` = verified in use. Provider rows marked **(verify)** are
seeds — do not treat their ids/prices as fact until `/refresh-forge-kb` confirms them.

## Roles
- **Orchestrator** — reasoning, decisions, planning, QA. Needs a strong model.
- **Worker** — one narrow task (extract, classify, transform, boilerplate). Needs the
  cheapest model that clears the task's bar.

## Base — Claude tiers (native; go in `model:`)

| Role | Tier | Notes | tier |
|---|---|---|---|
| Orchestrator | `opus` | Max reasoning / architecture / QA | advisory |
| Orchestrator/Worker | `sonnet` | Most reasoning + code; default workhorse | advisory |
| Worker | `haiku` | Precise, light language tasks; cheapest Claude | advisory |
| — | `inherit` | Match the caller's model | advisory |

> `model:` frontmatter accepts only `haiku | sonnet | opus | inherit`. The cross-provider
> columns below are **guidance for the artifact's instructions**, never a `model:` value.

## Cross-provider equivalents (for coherent instructions elsewhere)

Always state the Claude baseline; add the equivalent so the artifact stays coherent if the
host assistant is ChatGPT or OpenCode. Fill exact model ids via `/refresh-forge-kb`.

| Role | Claude (base) | ChatGPT / OpenAI | OpenCode Zen | Kimi / Moonshot |
|---|---|---|---|---|
| Orchestrator | `opus` / `sonnet` | a top reasoning tier **(verify id)** | a paid orchestrator-grade model **(verify id)** | long-context flagship **(verify id)** |
| Worker (light) | `haiku` | a small/cheap tier **(verify id)** | a free-tier worker **(verify id)** | a light tier **(verify id)** |
| Worker (code) | `sonnet` | a coding-capable tier **(verify id)** | a coding model **(verify id)** | — |

## How the wizard uses this

1. Choose the **Claude tier** for the role (base). Put it in `model:` when the artifact runs
   under Claude.
2. In the agent body, add a one-line **cross-provider note** so the instruction is coherent
   elsewhere, e.g.: *"Model: `sonnet` (Claude base). If run under ChatGPT use <equivalent>;
   under OpenCode use <Zen equivalent>."*
3. **Equivalence within Claude:** if the recommended tier is unavailable, step down/up the
   Claude ladder and say so. Never assume a specific cross-provider model exists — mark it
   `advisory` until verified.

## Maintenance
`/refresh-forge-kb` fills the ChatGPT / OpenCode Zen / Kimi ids and pricing from `sources.md`
with provenance, and promotes a row to `proven` only when verified in real use.
