# lovozeto/skills

A collection of Claude Code skills for AI-assisted design and engineering workflows.

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
| `/offload-to-local` | Route token-heavy, low-reasoning tasks to a free local model |
| `/ask-knowledge-base` | Explain a knowledge base rule in plain language |
| `/workshop-skill` | Create or improve a skill with delegation awareness and QA built in |
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
| `/save-session` | Write end-of-session state, log PRs, or reconcile memory |
| `/resume-session` | Load QUICK-STATE.md and orient on what was happening and what comes next |

### Media

| Skill | What it does |
|---|---|
| `/karaoke-builder` | Build/repair an UltraStar karaoke library — USDB / torrent (human-made) or AI (yt-dlp → demucs → forced alignment against verified lyrics), one validation pass |

## Setup

Some skills require additional setup provided by
[lobomorir-ai-setup](https://github.com/lovozeto/lobomorir-ai-setup):

| Dependency | Used by |
|---|---|
| `ask-apple`, `ask-local` wrappers on PATH | `offload-to-local`, `write-for-model` |
| `hardware.md` in active profile | `offload-to-local`, `workshop-skill` |
| Knowledge base at `~/dev/claude-kb/` | `ask-knowledge-base`, `kb-pipeline` |
| `preflight` on PATH | `init-project` |

Without that setup, skills fall back gracefully — `offload-to-local` uses the Claude
tier ladder, and `ask-knowledge-base` accepts a custom KB path at invocation time.

## Complementary: mattpocock/skills

These skills work well alongside the curated selection from
[mattpocock/skills](https://github.com/mattpocock/skills):

```bash
npx skills add mattpocock/skills -g -y
```
