---
name: workshop-skill
description: Create or improve a Claude Code skill with delegation awareness, QA contract, and scope rule built in. Invoke when creating or improving a skill.
disable-model-invocation: true
argument-hint: "skill"
---

# workshop-skill — create skills with delegation awareness

A layer on top of writing a skill. You don't just write the file: you ensure it knows
**what to delegate, to whom, and what to verify** — and that it ships with scope and QA
by default.

## Before creating anything (required)

1. Read `hardware.md` in the active profile (set up by `lobomorir-ai-setup`) → which local
   models are available on this machine. If no profile is configured, skip delegation to local.
2. Read `references/task-map.md` in the `offload-to-local` skill → tier ladder and
   task→wrapper→model map. This is the **single source of truth** for that map. Never copy
   it into the skill you're creating — point to it.
3. Ask for the **single objective** of the skill (one task, one scope).
4. Read `INDEX.md` of the active knowledge base (default: `~/dev/claude-kb/INDEX.md`) → what
   KB covers the skill's domain. Same rule as the routing map: **pointer, never copy**.
   - **If a KB file applies:** wire its path, purpose, and `tier` into the generated file.
     Load on demand. Other skills reuse the same source rather than duplicating knowledge.
   - **If no KB covers it:** say so and suggest running `/kb-pipeline`. Don't let the
     generated file fill from memory and present it as verified.
   - Tiers: `advisory` guides decisions; **only `proven` can back code.** If you wire an
     `advisory` base, say so.
   - **Does the knowledge belong in the KB or inside the skill?** One-question test:
     *Will more than one skill need this?*
     - **Yes** → it's a KB entry. Burying it in one skill makes it invisible; it ends up
       duplicated or contradicted.
     - **No** (the skill's own workflow, paths, or rules) → it goes inside.
   - **Never write a KB entry from memory.** KB entries are built by `/kb-pipeline` (real
     sources, provenance, tier). A KB entry is added to `INDEX.md` **when it exists**, not
     before.

## How to configure a new skill

### 1. Model tier — quality → savings

Choose the cheapest Claude tier that clears the bar for the skill's task:
- Simple with good language (classify precisely, write, extract reliably) → `haiku`
- Heavy with reasoning (correct code, analysis, most tasks) → `sonnet`
- Max reasoning / decision / QA / architecture → `opus`

`model:` in SKILL frontmatter only accepts `haiku` / `sonnet` / `opus` / `inherit`.

### 2. Only if the skill delegates to local models

Delegable work: high-token, low-reasoning (summarize, classify by form, extract, translate,
boilerplate code, convert format). If **the skill does not delegate**, skip to steps 3 and 4.

If it delegates:
- Add `Bash` to the skill's `allowed-tools` if it calls a wrapper.
- In the SKILL body, tell it to follow the delegation procedure: the task→wrapper→model map
  lives in `references/task-map.md` of the `offload-to-local` skill. **Never hardcode model
  IDs in the skill** — take them from the map + `hardware.md` at runtime.
- Fallback: if a wrapper exits with code ≠ 0, do the work at the next Claude tier. Never
  fail the task because a wrapper is missing.
- If the profile has no local models configured (`delegation_local: not-configured`): **do
  not add local delegation**; use the Claude tier ladder and note it in the skill body.

### 3. Inject the QA contract — **only if the skill delegates** (step 2)

If the skill does not delegate, **do not add this block** — it becomes dead text. If it
delegates, include in the skill body (adapting "how to verify"):

> **QA for delegated output:** every result from a delegated call is verified before use
> (schema / sanity check / spot-check). If it fails, redo one tier up.
> Do not assume someone else reviewed it.

### 4. Inject the single-task scope rule (always)

Applies to every skill, delegating or not. Add to the skill body:

> **Scope:** you have one task. Return the result or `OUT OF SCOPE`. Never expand on your
> own initiative. Return only the clean result.

## Dependencies and effects

### Dependencies — three layers, do not mix

| Layer | Declared in | Installed by |
|---|---|---|
| **Host** | `INSTALL.md` §2 | first setup, once per machine |
| **Project** | `ai-deps.yml` (`binaries.required`) | `/init-project` |
| **Skill** | skill's own preflight | skill detects and **asks permission** |

If the skill needs external binaries, **give it its own preflight** — do not add to `INSTALL.md`
(host-only). Preflight pattern:

1. **Detect** each binary and return JSON of what's missing.
2. **Explain** what each one does in user terms, not command names.
3. **Ask explicit confirmation before installing** — installation changes the user's system.
4. **Never install without the OK.** If missing, continue with what's available and **flag
   what was not verified** in the result.

### Effects — declare read-only or effective

Every skill declares in its first section whether it is **read-only** or **effective**
(makes changes).

- **Read-only** → state it as a hard rule at the top, not the bottom. If the user asks
  for an action with side effects, the skill says that's a different skill and stops.
- **Effective** → **confirmation gate before every irreversible action** (delete, overwrite,
  convert, push, install). Not optional.
- **For irreplaceable data** (family photos, backups, originals): gate + **never touch the
  original** — work on copies and leave the original intact.

Separate reading from writing into **distinct skills** when both exist. Auditing is safe and
runs many times; converting is dangerous and runs once. Mixing them makes the gate protect
poorly. Pattern: `inspecting-*` (reads) vs `optimizing-*` (writes).

## Verify before calling it done

`workshop-skill` configures the **policy**. Measuring whether the skill actually works is a
separate layer: the `skill-creator` plugin. Do not copy its logic — call it.

A `description` that "sounds right" is not the same as one that **fires**. Without this step,
you are building blind.

Find `skill-creator` at:
```
~/.claude/plugins/marketplaces/claude-plugins-official/plugins/skill-creator/skills/skill-creator
```
Assign it to variable `<SC>` in the commands below.

> **Precondition:** scripts need **Python ≥ 3.10** and `pyyaml`. The Command Line Tools
> Python 3.9.6 fails (`TypeError: unsupported operand type(s) for |` — PEP 604 syntax).
> Set up a venv with Python ≥ 3.10 + pyyaml and assign it to `$PY`. If it doesn't exist,
> this is a host dependency (`INSTALL.md §2`) — **do not install from here**; say so and
> stop at that level.
>
> **Invoke as a module** (`-m scripts.x`), not a standalone script, or you get
> `ModuleNotFoundError: No module named 'scripts'`. Use `PYTHONPATH=<SC>` **without** `cd`.

### Level 0 — structural (always, free)

```bash
PYTHONPATH=<SC> $PY -m scripts.quick_validate <skill-path>
```

Validates YAML and structure.

> **Known false positives (verified against official docs 2026-07-23).** `quick_validate`
> validates the portable Agent Skills standard (`agentskills.io`), which is a **subset**.
> Claude Code *extends* that standard. These fields are **valid in Claude Code** and the
> validator flags them as "unexpected key" — **do not remove them**:
> `disable-model-invocation`, `argument-hint`, `when_to_use`.
>
> A genuine error: keys that exist in neither the standard nor Claude Code (e.g., a bare
> `version:` — it belongs under `metadata:`). When you see a warning, ask: *Does this
> field exist in the Claude Code docs?* Yes → false positive, continue. No → fix it.

> `quick_validate` **only inspects SKILL.md files.** For all other files (agents, commands),
> validate the frontmatter with a strict YAML parse — it catches the most common bug: a
> `description` without quotes that contains `:` or `{}`. Measured 2026-07-23: 4 of 4
> commands had it.
> **Rule: any `description` containing `:` or `{}` must be quoted.**
>
> ```bash
> $PY - <<'PY'  # run on every new skill/agent/command
> import re, yaml, sys
> m = re.match(r'^---\n(.*?)\n---', open(sys.argv[1]).read(), re.S)
> yaml.safe_load(m.group(1)); print("frontmatter OK")
> PY
> ```

### Level 1 — trigger testing (opt-in: spends Claude tokens)

1. Write the eval set. Format for `run_eval.py`: **flat array** of
   `{"query": "...", "should_trigger": true|false}` with **positive** prompts (should
   trigger) and **negative** prompts (should not — include close neighbors to test the edge).
2. Run from the **project root where you want to measure** (not from `<SC>`):
   ```bash
   PYTHONPATH=<SC> $PY -m scripts.run_eval --eval-set <set.json> --skill-path <skill> \
     --model haiku --runs-per-query 1 --verbose
   ```

   > **Measured trap (2026-07-23) — read this or you'll measure noise.**
   > `run_eval` does not test your skill: it writes a *temporary command* with the
   > `description` into `<project_root>/.claude/commands/` and measures whether that one
   > fires. `project_root` is the first ancestor of `cwd` that has `.claude/`.
   >
   > **If the real skill is installed globally, it competes with the temporary one.**
   > Claude resolves the request with the real skill, the temporary never activates, and
   > the harness reports **0 triggers** across all queries — including obvious ones.
   > It looks like the `description` is wrong; the measurement measured nothing.
   >
   > **Symptom:** all positives at `rate=0/N`, only negatives pass. That pattern is the
   > diagnostic, not a result.
   >
   > **How to avoid it:** run Level 1 from a project where the skill is **not installed**
   > (neither global in `~/.agents/skills/` nor in the project's local install).
   >
   > **If the skill is global and there is no escape:** measure manually:
   > `claude -p "<query>" --model haiku --output-format stream-json`, discard the
   > `system`/init event (where the name appears just because it's available), and count
   > a trigger when the skill is **selected** in the rest of the stream.

   > **`CLAUDE.md` interference in headless mode (measured 2026-07-23).** The session-goal
   > rule ("ask the objective before anything else") fires **before the skill** in `claude -p`.
   > Claude identifies the correct skill in its output and still asks for the objective first.
   > Measure **selection**, not execution — counting executions will show zeros and make you
   > blame the `description`. Keep this in mind beyond evals: it affects any headless
   > automation (CI, hooks, `claude -p`) under this config.

   > **Use `--runs-per-query 3` before editing the `description`.** With 1 run a flake reads
   > as a gap: measured, an on-target query failed on the first pass and fired 2 of 3 on re-run.
   > Changing the `description` for that false negative would have broken something that was fine.

3. Optimize the `description` with those results. **Run from the same project root as step 2:**
   ```bash
   PYTHONPATH=<SC> $PY -m scripts.improve_description --eval-results <res.json> \
     --skill-path <skill> --model <model>
   ```
   Keep the one that **measures** better, not the one that sounds better.

**Cost levers** — `run_eval.py` launches one `claude -p` per query × runs:
- `--model haiku`: cheapest tier and a stricter test — if it fires in Haiku, it fires in Opus.
- `--runs-per-query 1` on the first pass; `3` only when measuring variance.
- **Delegate eval-set generation** to a local model via `/offload-to-local`: generating
  paraphrases of requests is bulk rewriting. Write that prompt with `/write-for-model`.

> **Hard limit:** the eval run itself **cannot be delegated.** It measures whether *Claude*
> activates the skill — a mechanism LM Studio models don't have. Delegating it measures noise.

## Output

The skill file at `skills/engineering/<name>/SKILL.md` (or `skills/productivity/<name>/`),
ready, with:
- `model:` at the right tier
- `allowed-tools:` with `Bash` only if the skill delegates
- Pointer to the applicable KB file (not a copy)
- A body with scope always and QA only if it delegates

Confirm in one sentence: which model, what delegation, what QA, which KB file — and why.
State **which verification level was run** — and if none was run, say so instead of
assuming it works.
