# lovozeto/skills

Claude Code skills for AI-assisted design and engineering. Public and distributable: the
personal setup that uses them (profiles, machines, knowledge base, deploy script) lives in the
private repo `lovozeto/lobomorir-ai-setup`, and this repo is its exported copy.

## Install

As a Claude Code plugin (recommended: versioned, one command to update):

```
/plugin marketplace add lovozeto/skills
/plugin install lovozeto-skills@lovozeto-skills
```

Or copy the skills into `~/.claude/skills` with the skills CLI:

```bash
npx skills add lovozeto/skills -g -y
```

## Skills

### Knowledge base

| Skill | What it does |
|---|---|
| `ask-kb` | Looks up the team knowledge base with the `kb` CLI before a design or engineering decision, and answers with the rule and its ref. Model-invoked. |
| `kb-curate` | Extracts atomic, sourced rules from one source at a time into the knowledge base, in the format `kb` indexes. |

### Reviews and QA

| Skill | What it does |
|---|---|
| `qa-code` | Review the changes since a commit, branch or tag on two axes: the repo's coding standards and the originating spec. Parallel sub-agents, side-by-side report. |
| `qa` | Strict technical audit: build, type check, imports, error and loading states, logic. Reports real failures only. |
| `ux-review` | Evaluates flows, information hierarchy, mobile ergonomics (44 px targets), interaction clarity and dark patterns. |
| `copy-review` | Audits and writes microcopy, error messages, button labels and interface text in the right tone. |
| `vqa` | Visual QA across breakpoints (375, 768, 1280 px) and light/dark mode: misalignments, wrong fonts, regressions. |
| `diagnosing-bugs` | Diagnosis loop for hard bugs and performance regressions, with a human-in-the-loop script template. |

### Design and build

| Skill | What it does |
|---|---|
| `brand` | Generates and updates the project's brand guidelines: WCAG-checked palette, type scale, logo rules, spacing, do's and don'ts. |
| `ui-spec` | Specifies UI decisions: hierarchy, type scale, AA palette, spacing, breakpoints, component states. |
| `web-graphics` | Builds real-time interactive graphics (Canvas 2D, WebGL, Three.js, particles, animation) tuned for 60 fps. |

### Thinking and workflow

| Skill | What it does |
|---|---|
| `grill-me` | Stress-tests a plan, decision or idea with relentless questions. |
| `kanban` | Organises ideas, tasks and progress on the project's board (GitHub Projects or `KANBAN.md`). |
| `prompt-master` | Writes, fixes and adapts prompts for other AI tools (LLMs, Cursor, image models). From nidhinjs/prompt-master (MIT), pinned at 1.8.2. |

## Setup some skills expect

| Dependency | Used by | Provided by |
|---|---|---|
| The `kb` CLI on PATH and a knowledge base at `~/dev/claude-kb` (or `$KB_ROOT`) | `ask-kb`, `kb-curate` | `lovozeto/kb` + `lobomorir-ai-setup/sync.sh` |

Without it, `ask-kb` falls back to reading `INDEX.md` by hand, and `kb-curate` still writes
files in the indexed format.

## Develop

Skills are edited in the private repo and exported here with `./sync.sh --export-public`.
Maintenance rules: `CLAUDE.md`. Superseded skills: `_archive/`.
