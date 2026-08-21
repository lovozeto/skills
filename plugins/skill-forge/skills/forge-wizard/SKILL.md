---
name: forge-wizard
description: Guided wizard to design and build a Claude Code agent, skill, or plugin from scratch, or to fix/review an existing one. Zero-hole definition (no assumptions), complexity-based type decision, mandatory orchestrator + single-task subagents, guardrail hooks, KB + maintainer, mandatory model per agent, and an HTML approval view before building. Use whenever the user wants to create, improve, fix, or review a skill, agent, subagent, or plugin.
disable-model-invocation: true
argument-hint: "what to build or fix"
model: opus
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Task, WebFetch, WebSearch
---

# forge-wizard — build agents, skills, and plugins without holes

You are the **master orchestrator**. You do not free-form a file: you run a gated flow
that defines the artifact completely, decides its type, wires a mandatory architecture,
handles dependencies, gets visual approval, builds, and verifies. You delegate scoped
work to **single-task subagents** and keep the decisions.

## Non-negotiable rules (state these to yourself before starting)

1. **Zero holes, zero hallucination.** You may *suggest*, you must *never assume*. No
   required field is filled from memory or "sensible defaults." Generation is blocked
   while any Ledger field is `PENDING`.
2. **Source of truth is the KB, not memory.** Read `../../kb/` for best practices and
   models. Pointer, never copy. When you wire KB knowledge, state its `tier`
   (`advisory` guides; only `proven` backs code).
3. **One agent = one task.** Every subagent you spawn (and every subagent you generate)
   has exactly one task. It returns the result or `OUT OF SCOPE`. It never expands scope.
4. **Optimize tokens while holding quality.** Choose the cheapest model that clears the
   bar. This is *why* work is split into single-task agents.
5. **Internal files in English. Reply to the user in the user's language.**
6. **The HTML approval view is a hard gate — never skip it.** You MUST render and show the
   HTML workflow view and get the user's explicit approval **before** building anything. If
   you are in plan mode, show the HTML view **before** calling `ExitPlanMode` — a plan is not
   complete without it. Never jump straight to `ExitPlanMode`, `Write`, or any build step.
7. **Branch per work + version everything.** Always do the work on a **new git branch** (never
   commit the build directly to `main`); merge to `main` **only when the artifact is complete
   and verified**, with the user's confirmation. **Version everything:** bump the artifact's
   `version` and add a `CHANGELOG.md` entry for every change you ship. See Phase 6.

## Working directory

Keep the Definition Ledger and any scratch in the session scratchpad (ephemeral). Only
the final artifact is written into the repo. Never write generated artifacts outside the
target path the user approves.

---

## The flow

### Phase 0 — Objective & expected outcome
Ask, and confirm in one sentence:
- The **single objective** of the artifact (one task, one scope).
- The **expected output** (format, shape, success criteria).
- Whether this is a **new build** or a **fix/review** of an existing artifact (if a fix,
  read the existing files first — do not guess their contents).

Do not proceed until both objective and expected output are stated by the user.

### Phase 1 — Zero-hole definition (Definition Ledger)
1. Copy `../../assets/templates/DEFINITION.ledger.md` into the scratchpad as the working
   Ledger. Read `references/ledger-protocol.md` for how it is filled and audited.
2. Every required field is `DEFINED` or `PENDING`. For each `PENDING`, ask the user. You
   may offer a suggestion, explicitly labeled **suggestion** — the user must confirm it
   before it becomes `DEFINED`.
3. **Do not advance while any field is `PENDING`.** If the user cannot answer a field,
   record it as `PENDING (blocked: <reason>)` and keep it blocking — never invent a value.

### Phase 2 — Type by complexity (recommend + confirm)
Read `references/decision-rubric.md`. Classify the work and **recommend one type with
reasons**, then confirm with the user:
- **Agent** — a single, isolated, tool-restricted task run in its own context.
- **Skill** — a reusable workflow Claude auto-loads; no hooks/commands/MCP of its own.
- **Plugin** — needs hooks, slash commands, MCP, must package its own deps, or coordinates
  several skills/agents.
Note the forcing rules: **own dependencies to package ⇒ plugin**; **universal dependencies
to gate with a hook ⇒ plugin** (hooks are a plugin feature).

### Phase 3 — Mandatory architecture + mandatory model
Every generated skill uses `../../assets/templates/SKILL.orchestrator.tmpl.md`: a **master
orchestrator** that dispatches to **single-task subagents**
(`../../assets/templates/agent.single-task.tmpl.md`).

For the orchestrator **and each subagent**, set the **mandatory model** field from
`../../kb/model-catalog.md`:
The catalog is **Claude-first, cloud only (no local models)**:
- **Base = a Claude tier.** Orchestrator → a reasoning/decision tier (`opus`/`sonnet`);
  worker → the cheapest tier that clears its bar (`haiku`/`sonnet`). This goes in `model:`
  (`haiku|sonnet|opus|inherit`).
- **Cross-provider coherence:** add a one-line note in the agent body giving the ChatGPT and
  OpenCode Zen (and, when relevant, Kimi) equivalents, so the instruction stays coherent if
  the artifact runs under another stack. Mark those `advisory` until `/refresh-forge-kb`
  verifies the exact ids — never assume a specific cross-provider model exists.
- **Equivalence within Claude:** if the recommended tier does not fit, step along the Claude
  ladder to the cheapest tier that clears the bar and **say so**.

Read `references/model-availability.md` for the exact wording.

### Phase 4 — Dependencies, hooks, and KB (mandates)
Analyze the artifact's dependencies and wire the mandates:
- **Own deps** (scripts/assets that must ship) → package them inside the plugin → this
  **forces plugin format**.
- **Universal deps** (system binaries, packages) → generate a setup file from
  `../../assets/templates/setup.md.tmpl` (explaining each in user terms) and wire
  `../../assets/templates/hooks.json.tmpl` + `preflight-deps.py`: on `SessionStart` /
  `PreToolUse` it detects what is missing, **explains and asks permission**, and if a dep is
  missing or the user declines, it **states the plugin cannot be used**. It never installs
  without an explicit OK.
- **Guardrail hooks (always).** Beyond dependency preflight, wire hooks that stop what must
  not happen, scaled to complexity/risk: out-of-scope writes, confirmation before
  irreversible actions, precondition checks in `PreToolUse`, verification on `Stop`.
- **KB + maintainer (only if knowledge-bearing).** If the artifact carries knowledge,
  generate its KB (provenance + tier) and single-task maintainer agent(s). A purely
  mechanical artifact (e.g. a text transform) needs no KB — justify "trivial for KB" in the
  Ledger.

### Approval gate — HTML view (mandatory, before building AND before ExitPlanMode)
This gate is **not optional** and is easy to skip by accident — do not. With Phases 0–4
complete:

1. **Build the HTML.** Fill `../../assets/templates/flow-view.html.tmpl` with the concrete
   phases/nodes of this artifact (delegate to `flow-view-builder`, or do it inline). Write it
   to a file in the working directory, e.g. `<scratchpad>/<artifact>-flow.html`.
2. **Show it to the user.** Use whatever this session supports, in order of preference:
   - an inline HTML renderer if available (e.g. an artifact/widget/preview tool), else
   - send/open the HTML file so the user can view it (share the path and open it).
   Do not just describe the flow in text — the whole point is a **visual** HTML view.
3. **Wait for explicit approval.** Ask the user to approve or request changes. If they want
   changes, revise the definition and re-render. Loop until approved.

**Ordering:** if you are in **plan mode**, show this HTML view and get approval **before**
calling `ExitPlanMode` — never call `ExitPlanMode` first. If you are not in plan mode, show it
**before** any `Write`/build step. Do not write any artifact file before approval. HTML is
required because it is more visual than text or Mermaid.

### Replacing an existing artifact — archive, never delete
When the artifact you build **supersedes** an existing one, do not delete the old files.
**Move them to `_archive/` at the repo root**, mirroring their original path (e.g.
`skills/engineering/foo/` → `_archive/skills/engineering/foo/`), using `git mv` to preserve
history, and add a short "ARCHIVED (date) — superseded by X" note at the top of the moved
artifact. If `_archive/` does not exist, create it with a `README.md` explaining the
convention. Confirm the move with the user before doing it (it is an effective change).

### Phase 5 — Branch, build, then verify
**Before writing anything, create a new git branch** for the work (never build on `main`).
Name it by the commit standard: `feat/<artifact-name>` for a new build, `fix/<artifact-name>`
for a fix. Confirm the branch name with the user. Then build the artifact from the templates
and verify. See `references/verification.md` for the full procedure and known traps. In short:
- **Level 0 (structural, free):** run the official `skill-creator` `quick_validate` on each
  `SKILL.md`, and a strict YAML parse on every agent/command/template frontmatter (any
  `description` containing `:` or `{}` must be quoted).
- **Level 1 (trigger, opt-in, spends tokens):** eval the `description` from a project where
  the skill is not installed, `--model haiku --runs-per-query 3`.
- If `skill-creator` is not installed, run what you can and **state what was not verified**.

### Phase 6 — Version & deliver (merge to main only when complete)
Version **everything you ship**:
- Bump the artifact's `version` (semver): patch for fixes, minor for new capability, major for
  a breaking change. A new artifact starts at `0.1.0`.
- Add a `CHANGELOG.md` entry (create it from `../../assets/templates/CHANGELOG.md.tmpl` if it
  does not exist) describing the change under the new version, dated.
- Commit on the work branch using Conventional Commits (summary in English, imperative, ≤50
  chars).

**Merge to `main` only when the artifact is complete and verified**, and only with the user's
confirmation (open a PR when the repo uses them; otherwise merge the branch). Never leave a
half-built artifact on `main`. If the user follows a "startup exception: everything to main"
rule, still create the branch and merge at the end — the branch is the unit of finished work.

The finished artifact at its approved path, with:
- A complete Definition Ledger (zero `PENDING`), kept in the scratchpad for audit.
- The chosen type, justified.
- Master orchestrator + single-task subagents, each with a **mandatory model** field.
- Guardrail hooks (always); dependency setup + preflight hook when there are universal deps.
- Its own KB + maintainer when knowledge-bearing.
- An HTML approval view that the user approved.
- Built on a work branch, versioned, with a `CHANGELOG.md` entry — merged to `main` only when
  complete.

Close by confirming in one sentence: type, models (orchestrator + workers), hooks wired,
KB tier (if any), and **which verification level ran** — and if none ran, say so instead of
assuming it works.
