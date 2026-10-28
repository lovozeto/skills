# skill-forge

A guided **wizard** for designing and building Claude Code **agents, skills, and plugins** — universal in the style of the official `claude-plugins-official` marketplace, with strong guarantees against under-specification and hallucination.

## What it guarantees

- **Zero-hole definition.** A *Definition Ledger* tracks every required field as `DEFINED` or `PENDING`. The wizard suggests but never assumes; generation is blocked while anything is `PENDING`.
- **Type decision by complexity.** It recommends (and confirms with you) whether the work should be a single **agent**, a **skill** with subagents, or a **plugin** bundling several — with reasons.
- **Mandatory architecture.** Every generated skill ships a **master orchestrator** plus **single-task** specialized subagents (one task per agent).
- **Mandatory model per agent.** Every agent/orchestrator declares which model(s) launch it, with an **equivalence rule** when the recommended one is unavailable on the machine.
- **Hooks always.** Every generated artifact ships guardrail hooks scaled to its complexity.
- **KB + maintainer always.** Any knowledge-bearing artifact ships its own KB (provenance + tier) and single-task agents that keep it fresh.
- **HTML approval view.** Before building, the wizard renders an HTML view of the workflow(s) for you to approve.
- **Dependencies handled.** Own deps are packaged (forces plugin format); universal deps get a setup file plus a preflight hook that asks permission and blocks use if missing or denied.

## Components

| Path | Role |
|---|---|
| `skills/forge-wizard/` | The master wizard (orchestrator). Drives the whole flow. |
| `skills/forge-wizard/agents/agent-prompt-reviewer.md` | Opus reviewer: judges every drafted file as a prompt, against the KB and `writing-for-agents`. |
| `skills/refresh-forge-kb/` | On-demand maintainer that refreshes the KB and the packaged templates from credible sources. |
| `kb/` | Bundled, portable knowledge base (best practices + multi-provider model catalog), the wizard's source of truth. |
| `assets/templates/` | Reusable scaffolds the wizard instantiates (ledger, plugin.json, hooks.json, preflight, setup, skill/agent, HTML flow view). |

## Install

This repository is a plugin marketplace (`/.claude-plugin/marketplace.json`). Add it and install:

```bash
/plugin marketplace add lovozeto/skills
/plugin install skill-forge@lovozeto-skills
```

Or install by path from a local clone. See the marketplace manifest at the repo root.

## Companion plugin (recommended)

Install `mattpocock-skills` (`claude plugin marketplace add mattpocock/skills` then
`claude plugin install mattpocock-skills@mattpocock`). The wizard uses its `grilling`,
`domain-modeling`, `codebase-design`, `writing-for-agents`, `wizard`, `tdd`, and `code-review`
skills, and recommends `wayfinder` / `to-spec` / `to-tickets` for large work. Without it, the
wizard runs its built-in flow and says which steps it skipped.

## Host dependencies

- **Python ≥ 3.10** with `pyyaml` for the verification scripts (structural validation via the official `skill-creator`). The macOS Command Line Tools Python 3.9.6 fails on PEP 604 syntax — use a newer interpreter.
- Verification also assumes the official `skill-creator` plugin is installed; if it is not, the wizard runs only the checks it can and states what was not verified.

## Language

All internal files (code, config, `SKILL.md`, agents, templates, instructional KB) are in **English**. The wizard replies to you in **your** language.
