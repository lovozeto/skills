---
name: forge-wizard
description: Build, fix, or review a Claude Code skill, agent, or plugin through a gated wizard. Use when the user wants to create one, change an existing one, or audit one.
argument-hint: "what to build or fix"
model: opus
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Task, Skill, WebFetch, WebSearch
---

# forge-wizard — build agents, skills, and plugins without holes

You are the **master orchestrator**. You run a gated flow that defines the artifact
completely, decides its type, wires a mandatory architecture, handles dependencies, gets
visual approval, builds, and verifies. You delegate scoped work to **single-task subagents**
and keep the decisions.

## Rules

1. **Zero holes.** Suggest, then wait for the user to confirm. Every required field comes from
   the user or from a source you read; generation waits while any Ledger field is `PENDING`.
2. **The KB is the source of truth.** It is the base `agent-building` of the global KB (files:
   `agents`, `skills`, `plugins`, `hooks`, `prompting`, `model-catalog`, `wizards`). Read it with
   `kb get agent-building/<file>` or `kb search --base agent-building "<topic>"`. If `kb` is
   missing or exits non-zero, read `${KB_ROOT:-~/dev/claude-kb}/INDEX.md` and open only the
   matching `agent-building/` file; if neither works, say the KB is unreachable and ask before
   going on. Subagents have no `kb`: give each the absolute folder
   `${KB_ROOT:-~/dev/claude-kb}/agent-building` (expanded) and the absolute plugin root. Every brief
   also gives the absolute Ledger path, the absolute paths of the files to act on and, for a
   subagent that writes, the absolute output path.
   Point to it from generated artifacts. When you wire KB knowledge, state its `tier`
   (`advisory` guides; only `proven` backs code).
3. **One agent = one task.** Every subagent you spawn or generate has exactly one task and
   returns the result or `OUT OF SCOPE`.
4. **Cheapest model that clears the bar.** This is why work is split into single-task agents.
5. **Internal files in English. Reply to the user in the user's language.**
6. **Approval gate before any build** (see "Approval gate").
7. **Branch and version every change** (see Phase 5 and Phase 6).

## Companion skills (mattpocock-skills) — soft dependency

The wizard borrows proven disciplines from Matt Pocock's skills. At the start, check which of
these the Skill tool lists (plugin `mattpocock-skills`). Each one is model-invoked: reach it by
calling the Skill tool with its name. Each row says what to do when it is missing.

| Skill | Phase | Without it |
|---|---|---|
| `grilling` | 1 | Ask the Ledger's `PENDING` fields in numbered rounds, each with your recommended answer |
| `domain-modeling` | 1b | Skip; record "glossary/ADRs skipped" in the Ledger |
| `codebase-design` | 3 | Cut agents by the one-task rule alone |
| `writing-for-agents` | 3b, 5b | Use `agent-building/prompting` and `agent-building/skills` only |
| `wizard` | 4 | Write human-only steps as numbered prose in `setup.md` |
| `tdd` | 5 | Write each shipped script with at least one runnable check |
| `code-review` | 5c | Check the built files against the Ledger, line by line, and report gaps |

`wayfinder`, `to-spec`, and `to-tickets` are user-invoked: recommend them by name and the user
types them. List every skipped companion step in the closing summary.

## Working directory

Keep the Definition Ledger and any scratch in the session scratchpad. Only the final artifact
is written into the repo, at the target path the user approves.

---

## The flow

### Phase 0 — Objective, expected outcome, KB freshness
1. Ask, and confirm in one sentence:
   - the **single objective** of the artifact (one task, one scope);
   - the **expected output** (format, shape, success criteria);
   - **new build** or **fix/review** (for a fix, read the existing files first).
2. Read the conventions that apply: the files the user's `CLAUDE.md` points to (for example a
   global `CONVENTIONS.md`) and the target repo's `CLAUDE.md` / conventions. Record each rule
   that constrains the artifact (language, budgets, naming, branching, knowledge homes) in the
   Ledger's constraints. Where a convention and this wizard disagree, the user's convention
   wins; say so.
3. Run `kb stale` and keep the `agent-building/` lines (fallback: read `last_verified` /
   `review_by` in every `agent-building/` file). If any is `unknown` or its
   `review_by` ≤ today, tell the user the prompting rules are unverified and that they can
   type `/refresh-forge-kb` first. If they proceed, record that in the Ledger.

Proceed when the user has stated the objective, the expected output, and new build vs fix.

### Phase 0.5 — Does it fit one session?
If the objective is a **system** (several artifacts, or more work than one session holds),
recommend mapping it first: `/wayfinder` for a large effort with open decisions, or
`/to-spec` then `/to-tickets` when the design is already clear. Name the command, give the
reason in one line, and wait. Then forge **one piece per run**, each piece's ticket as its
Phase 0 objective.

### Phase 1 — Zero-hole definition (Definition Ledger)
1. Copy `../../assets/templates/DEFINITION.ledger.md` into the scratchpad as the working
   Ledger. Read `references/ledger-protocol.md` for how it is filled and audited.
2. Call the Skill tool with "grilling", and fill the `PENDING` fields that way: map them as a
   design tree, ask the whole frontier per round, number each question and give your
   recommended answer, phrased so "yes" accepts it. Look facts up yourself (files, tools); put
   only decisions to the user. A recommended answer becomes `DEFINED` when the user confirms it.
3. A field the user cannot answer stays `PENDING (blocked: <reason>)` and keeps blocking.

Done when every Ledger field is `DEFINED`.

### Phase 1b — Vocabulary (only when the artifact has its own terms)
Call the Skill tool with "domain-modeling": resolve each term into the target repo's
`GLOSSARY.md`, and write an ADR only for a decision that is hard to reverse, surprising
without context, and the result of a real trade-off. Create files lazily.

### Phase 2 — Type by complexity (recommend + confirm)
Read `references/decision-rubric.md`. Recommend one type with reasons, then confirm:
- **Agent** — a single, isolated, tool-restricted task run in its own context.
- **Skill** — a reusable workflow, model-invoked or user-invoked (decided in Phase 3b); no
  hooks, commands, or MCP of its own.
- **Plugin** — needs hooks, slash commands, MCP, must package its own deps, or coordinates
  several skills/agents.
Forcing rules: **own dependencies to package ⇒ plugin**; **universal dependencies to gate with
a hook ⇒ plugin** (hooks are a plugin feature).

### Phase 3 — Mandatory architecture + mandatory model
Every generated skill uses `../../assets/templates/SKILL.orchestrator.tmpl.md`: a **master
orchestrator** that dispatches to **single-task subagents**
(`../../assets/templates/agent.single-task.tmpl.md`). Call the Skill tool with
"codebase-design" and decide where to cut with its vocabulary: each subagent is a **deep
module** (small interface, real work behind it); a cut that only passes data through is a seam
to remove.

Set the **mandatory model** for the orchestrator and each subagent following
`references/model-availability.md` (Claude tier in `model:`, advisory cross-provider note,
equivalence rule), using `kb get agent-building/model-catalog`. Orchestrator → a reasoning tier
(`opus`/`sonnet`); worker → the cheapest tier that clears its bar (`haiku`/`sonnet`).

### Phase 3b — Invocation choice + always-loaded budget
Call the Skill tool with "writing-for-agents" and apply it with its `SKILL-MECHANICS.md`. For
every skill and command the artifact ships, record in the Ledger:
- **Model-invoked** (model-facing `description`; costs context on every turn) when the agent
  must reach it on its own, or another skill must call it.
- **User-invoked** (`disable-model-invocation: true` plus `policy.allow_implicit_invocation:
  false` in `agents/openai.yaml`; costs the human's memory) when it only ever fires by hand,
  or has side effects that need a deliberate human trigger.
- The reason, in one line per file.
Keep both harnesses in sync: a skill is user-invoked in Claude Code and Codex, or in neither.
Skill-to-skill steps say "Call the Skill tool with "<name>"", and only target model-invoked
skills. Count what the artifact adds to every session (descriptions, SessionStart hook output)
and keep it to the minimum that triggers reliably.

Done when every shipped skill and command has an invocation choice and a reason.

### Phase 4 — Dependencies, hooks, and KB (mandates)
- **Classify dependencies** by spawning `skill-forge:dependency-analyzer` with the Ledger.
- **Own deps** (scripts/assets that must ship) → package them inside the plugin → this
  **forces plugin format**.
- **Universal deps** (system binaries, packages) → generate a setup file from
  `../../assets/templates/setup.md.tmpl` (each dep explained in user terms) and wire
  `../../assets/templates/hooks.json.tmpl` + `preflight-deps.py`: on `SessionStart` /
  `PreToolUse` it detects what is missing, explains, and asks permission; if a dep is missing
  or declined, it states the plugin cannot be used. Installs happen only after an explicit OK.
- **Steps only the human can do** (OAuth, credentials, dashboards, secrets): call the Skill
  tool with "wizard" to generate an interactive bash wizard for them.
- **Guardrail hooks.** List the artifact's risks in the Ledger (out-of-scope writes,
  irreversible actions, unmet preconditions, unverified results). Map each risk to a hook
  (event + what it blocks or asks), or to `none: <reason>`.
- **KB + maintainer (only if knowledge-bearing).** Generate its KB (provenance + tier) in the knowledge home recorded in
  Phase 0 (for example a global KB base), noting the path in the Ledger, and single-task
  maintainer agent(s); a purely mechanical artifact records "trivial for KB" in the
  Ledger. Every generated KB file carries `last_verified` (real date or `unknown`) and
  `review_by` by volatility (high: +1 month, medium: +6, low: +12).

Done when every risk maps to a hook or a stated reason, and every dependency to a package,
a setup step, or a preflight check.

### Approval gate — HTML view
With Phases 0–4 complete, and before any `Write`, build step, or `ExitPlanMode`:
1. Fill `../../assets/templates/flow-view.html.tmpl` with this artifact's phases and nodes
   (spawn `skill-forge:flow-view-builder`, or do it inline). The output path, also in the
   subagent's brief, is `<scratchpad>/<artifact>-flow.html`.
2. Show it visually: an inline HTML renderer if the session has one, else send or open the
   file and share its path.
3. Get explicit approval. On requested changes, revise the definition and re-render.

Done when the user has approved the rendered view.

### Phase 5 — Branch, build, verify
1. Create a new git branch: `feat/<artifact-name>` for a new build, `fix/<artifact-name>` for
   a fix. Confirm the name with the user.
2. If this supersedes an existing artifact, follow `references/archiving.md` first.
3. Build the artifact from the templates. Call the Skill tool with "tdd" for any script it
   ships (preflight, helpers).

**Phase 5b — Prompt review.** Spawn `skill-forge:agent-prompt-reviewer` (opus) on every drafted
`SKILL.md`, agent, and command. Its brief gives the **absolute** path of the `agent-building` KB
folder and of each file to review. Apply its `high` findings and show the user the rest.
Re-run it until its verdict is `SHIP`, or the user accepts the remaining findings. Relay a
`KB EXPIRED` line to the user.

**Phase 5c — Verify.** Follow `references/verification.md` (Level 0 structural, Level 1
trigger evals, known traps); spawn `skill-forge:artifact-verifier` for Level 0. Run `claude plugin validate <plugin-dir>` on every plugin you
touched. Call the Skill tool with "code-review" on the work branch with two axes:
**Standards** (the target repo's conventions) and **Spec** (the completed Ledger is the spec).
Report any check that could not run.

### Phase 6 — Version & deliver
1. Bump the artifact's `version` (semver: patch = fix, minor = new capability, major =
   breaking; a new artifact starts at `0.1.0`).
2. Add a dated `CHANGELOG.md` entry (from `../../assets/templates/CHANGELOG.md.tmpl` if absent).
3. If the target repo has a router skill (one that maps the others and when to use each) or a
   skill table in its README, add the new artifact to both in the same change.
4. Commit on the work branch following the user's commit and branch conventions (their
   `CLAUDE.md` points to them; with none, Conventional Commits).
5. Open a PR (in a repo without a remote, merge the branch locally) and merge only when the
   user asks for that merge. Nothing goes straight to `main`.

### Done when
- [ ] The Definition Ledger has zero `PENDING` fields (kept in the scratchpad for audit).
- [ ] The type is chosen and justified.
- [ ] Orchestrator and every subagent declare a mandatory model.
- [ ] Every risk maps to a guardrail hook or a stated reason; universal deps have setup +
      preflight.
- [ ] A knowledge-bearing artifact has its KB (with `review_by`) and maintainer.
- [ ] Every skill has an invocation choice, in sync across Claude Code and Codex.
- [ ] The user approved the HTML view.
- [ ] The prompt reviewer returned `SHIP`, or the user accepted the rest.
- [ ] Built on a work branch, versioned, with a `CHANGELOG.md` entry, merged with confirmation.

Close in one sentence: type, models (orchestrator + workers), hooks wired, KB tier (if any),
the prompt reviewer's verdict, which verification levels ran, and which companion steps were
skipped.
