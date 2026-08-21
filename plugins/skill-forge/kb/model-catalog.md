# Model catalog (multi-provider)

Source of truth for the **mandatory model** field. New and internal to skill-forge — it does
**not** touch `offload-to-local` (which is local-only and stays separate).

Goal: **optimize tokens while holding quality**. Pick the cheapest capable model per role,
and be explicit when you fall back. Provider-specific rows marked **(verify)** are seeds — do
not treat their ids/prices as fact until `/refresh-forge-kb` confirms them.

`tier`: `advisory` guides; `proven` = verified on this machine (a real call succeeded).

## Roles

- **Orchestrator** — reasoning, decisions, planning, QA. Needs a strong model.
- **Worker** — one narrow task (extract, classify, transform, boilerplate). Needs the
  cheapest model that clears the task's bar.

## Claude tiers (native — go in `model:`)

| Role | Tier | Notes | tier |
|---|---|---|---|
| Orchestrator | `opus` | Max reasoning / architecture / QA | advisory |
| Orchestrator/Worker | `sonnet` | Most reasoning + code; default workhorse | advisory |
| Worker | `haiku` | Precise, light language tasks; cheapest Claude | advisory |
| — | `inherit` | Match the caller's model | advisory |

> `model:` frontmatter accepts only `haiku | sonnet | opus | inherit`. Everything below is a
> **delegated route** (documented in the agent body), never a `model:` value.

## Other providers (delegated — document the route; verify before use)

| Provider | Example role fit | Free / paid | How to call | tier |
|---|---|---|---|---|
| OpenAI / ChatGPT | worker or orchestrator | paid | via a configured wrapper/tool **(verify)** | advisory |
| Moonshot / Kimi | long-context worker | (verify) | via wrapper **(verify)** | advisory |
| OpenCode Zen | worker (free tier) / orchestrator (paid) | free + paid | via OpenCode **(verify exact model ids)** | advisory |
| Local (Apple FM, LM Studio) | short/medium worker | free | see `offload-to-local` + machine `hardware.md` | advisory |

## Equivalence table (role-based)

Use when the recommended model is unavailable. Pick the closest **available** row in the same
role, preferring the same provider, then the cheapest that clears the bar.

| Role | Recommended | Equivalents (in preference order) |
|---|---|---|
| Orchestrator | `opus` | `sonnet` → paid cross-provider orchestrator **(verify)** → `sonnet`/`opus` again |
| Worker (reasoning-light) | `haiku` | local worker (if configured) → free cross-provider worker **(verify)** → `haiku` |
| Worker (code) | `sonnet` | local coder model (if configured) → `sonnet` |

If nothing equivalent is verifiably available, fall back to the Claude tier ladder and
**state that availability could not be verified**.

## Maintenance
`/refresh-forge-kb` fills the provider rows from `sources.md` (OpenAI, OpenCode Zen, Kimi),
records ids/pricing with provenance, and promotes rows to `proven` only when a real call has
been verified on this machine.
