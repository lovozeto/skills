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
| `/delegate` | Hand token-heavy, low-reasoning tasks to a free opencode model |
| `/ask-knowledge-base` | Explain a knowledge base rule in plain language |
| `/write-for-model` | Build an optimized prompt for a specific local or delegation model |
| `/commit` | Stage and commit following Conventional Commits |
| `/kb-pipeline` | Research, update, or refresh a knowledge base with mandatory curation gates |
| `/update-knowledge-base` | Add or correct a single KB entry from a verified source URL |
| `/arbitrate` | Resolve a clash between UX intent and a verified technical constraint |
| `/benchmark-model` | Test a local model, measure quality and speed, update the task routing map |
| `/init-project` | Initialize a repo for AI-assisted work: deps, CLAUDE.md, QUICK-STATE.md |

### Productivity

| Skill | What it does |
|---|---|
| `/ask-wolf` | Router: which skill or flow fits your situation (manual) |
| `/save-session` | Write end-of-session state, log PRs, or reconcile memory |
| `/resume-session` | Load QUICK-STATE.md and orient on what was happening and what comes next |

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

```bash
/plugin marketplace add lovozeto/skills
/plugin install skill-forge@lovozeto-skills
```

See [`plugins/skill-forge/README.md`](plugins/skill-forge/README.md).

## Setup

Some skills require additional setup provided by
[lobomorir-ai-setup](https://github.com/lovozeto/lobomorir-ai-setup):

| Dependency | Used by |
|---|---|
| `ask-opencode` wrapper on PATH | `delegate`, `write-for-model` |
| `hardware.md` in active profile | `delegate`, `skill-forge` |
| Knowledge base at `~/dev/claude-kb/` | `ask-knowledge-base`, `kb-pipeline` |
| `preflight` on PATH | `init-project` |

Without that setup, skills fall back gracefully — `delegate` uses the Claude
tier ladder, and `ask-knowledge-base` accepts a custom KB path at invocation time.

## Complementary: mattpocock/skills

These skills work well alongside the curated selection from
[mattpocock/skills](https://github.com/mattpocock/skills):

```bash
claude plugin marketplace add mattpocock/skills
claude plugin install mattpocock-skills@mattpocock
```

Install it as a Claude Code plugin: `npx skills` does not link it into `~/.claude/skills`.
