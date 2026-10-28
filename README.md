# lovozeto/skills

A collection of Claude Code skills for AI-assisted design and engineering workflows.

> This repo is **public and distributable**: skills, the `skill-forge` plugin, and its
> marketplace. Personal setup (profiles, machines, knowledge base, hooks, deploy script)
> lives in a separate **private** repo, `lovozeto/lobomorir-ai-setup`, which installs this one.

## Install

```bash
npx skills add lovozeto/skills
```

Or globally (recommended — skills work across all projects):

```bash
npx skills add lovozeto/skills -g -y
```

## Skills

### Engineering

| Skill | What it does |
|---|---|
| `/commit` | Stage and commit following Conventional Commits |
| `/arbitrate` | Resolve a clash between UX intent and a verified technical constraint |
| `/init-project` | Initialize a repo for AI-assisted work: deps, CLAUDE.md, QUICK-STATE.md |

### Productivity

| Skill | What it does |
|---|---|
| `/ask-wolf` | Router: which skill or flow fits your situation (manual) |
| `/save-session` | Write end-of-session state, log PRs, or reconcile memory |
| `/track-work` | Keep the GitHub issue and its board column current while you work |
| `/resume-session` | Load QUICK-STATE.md and orient on what was happening and what comes next |
| `/workspace-layout` | Map of `~/GitHub`: where to clone a repo and how to move one without breaking things |

### Media

| Skill | What it does |
|---|---|
| `/karaoke-builder` | Build/repair an UltraStar karaoke library — USDB / torrent (human-made) or AI (yt-dlp → demucs → forced alignment against verified lyrics), one validation pass |
| `/inspecting-photo-archives` | Read-only metadata report for old photo/video folders (capture date, camera, timezone, lost dates, at-risk formats) before importing |

## Plugins

This repository is also a plugin marketplace (`.claude-plugin/marketplace.json`).

| Plugin | What it does |
|---|---|
| `skill-forge` | Guided wizard to design and build agents, skills, and plugins: zero-hole definition, complexity-based type decision, orchestrator + single-task subagents, guardrail hooks, a live best-practices KB, mandatory model per agent, and an HTML approval view. Supersedes `/workshop-skill`. |
| `delegation` | Hand token-heavy, low-reasoning tasks to free models: text to local Ollama (`ask-local`), file work to an opencode agent, local when the material has data. Data scan before cloud calls, model allowlist, benchmark (`/delegation:benchmark-model`), machine setup (`/delegation:init`). Supersedes `/delegate`, `/write-for-model`, `/benchmark-model`. |
| `knowledge-base` | Read, explain, correct, and research the global knowledge base with the `kb` CLI (`INDEX.md` fallback): `ask-knowledge-base` and `update-knowledge-base` (automatic), `/knowledge-base:kb-pipeline` (three gates, single-task agents). A hook asks before any write inside the KB outside `.raw/`. Supersedes `/ask-knowledge-base`, `/update-knowledge-base`, `/kb-pipeline`. |

```bash
/plugin marketplace add lovozeto/skills
/plugin install skill-forge@lovozeto-skills
/plugin install delegation@lovozeto-skills
/plugin install knowledge-base@lovozeto-skills
```

See [`plugins/skill-forge/README.md`](plugins/skill-forge/README.md), [`plugins/delegation/README.md`](plugins/delegation/README.md), and [`plugins/knowledge-base/README.md`](plugins/knowledge-base/README.md).

## Setup

Some skills require additional setup provided by
[lobomorir-ai-setup](https://github.com/lovozeto/lobomorir-ai-setup):

| Dependency | Used by |
|---|---|
| Knowledge base readable with `kb` or at `$KB_ROOT` (base `delegation`, machine profile `hardware`) | `delegation` |
| Knowledge base at `~/dev/claude-kb/` or `$KB_ROOT` (optional `kb` CLI) | `knowledge-base` (`ask-knowledge-base`, `update-knowledge-base`, `kb-pipeline`) |
| `preflight` on PATH | `init-project` |

Without that setup, skills fall back gracefully: `delegation` says its model choice is
unmeasured and checks results more closely, and the `knowledge-base` skills fall back to
`$KB_ROOT/INDEX.md` (default `~/dev/claude-kb/`) when `kb` is unavailable.

## Complementary: mattpocock/skills

These skills work well alongside the curated selection from
[mattpocock/skills](https://github.com/mattpocock/skills):

```bash
claude plugin marketplace add mattpocock/skills
claude plugin install mattpocock-skills@mattpocock
```

Install it as a Claude Code plugin: `npx skills` does not link it into `~/.claude/skills`.
