---
name: delegate
description: Hand off a token-heavy, low-reasoning task to a free opencode model via `ask-opencode` instead of spending Claude tokens. Use before running any such task — summarize, extract fields, translate, rewrite/clean text, convert format, mechanical code refactor or boilerplate, read/summarize long code, rename/format/search across a repo — and whenever the user says "delegate", "pass this to opencode", or "use a free model".
argument-hint: "[task description]"
---

# delegate — hand a task to a free opencode model

The task → model map lives in `references/task-map.md` (ships with this skill).
This skill is the **how**, not the copy.

**Scope for now: opencode only.** LM Studio (`ask-local`) and Apple on-device (`ask-apple`)
are out of this skill until they are re-added on purpose. If opencode is not available,
fall through to the Claude tier ladder (step 6) — never to a local wrapper.

## When it applies

Only if the task is **high in tokens but simple in reasoning** and the result coming back is
**compact** (or is a diff you can review). If the task is already small, **don't delegate** —
coordination overhead costs more than the tokens saved.

Delegable: summarize long text/log, extract structured fields, translate prose, rewrite/clean
text, convert format (JSON/CSV/Markdown), boilerplate or mechanical code refactor,
read/summarize long code, mechanical repo-wide edits (rename, format, search).

**Not** delegable: architecture, decisions, critical code, QA of the delegated result,
anything with private code or credentials (see Privacy).

### "Classify" splits into two — it is not one thing

| Type | Example | Delegable? |
|---|---|---|
| **By text form** | Does this name contain a date? What language is this? | **Yes** |
| **By world knowledge** | Is this codec still supported? Is this library deprecated? | **No** |

If the correct answer requires knowing something about the world, a small model
**hallucinates confidently**. Measured 2026-07-23: a small model classifying format risk got
2 of 4 wrong and stated "Apple deprecated QuickTime in 2017" — false, said without doubt.
That judgment stays with Claude.

### Translating instruction files — not the same as translating prose

Translating a README is safe. Translating a `SKILL.md`, agent, or command is **high risk**:
a translated identifier, a softened `NEVER`, or an inverted negation silently breaks the
system. See `references/task-map.md` for the protocol.

### One constraint per instruction

Small models **lose constraints when given several at once**. Measured: asked for
"10 examples, 6 in Spanish and 4 in English, varied, no tool names", a model returned 10 in
Spanish with duplicates. Split multiple conditions into separate calls, or finish the
remainder yourself. Don't escalate the model for this before hardening the prompt.

## Privacy (hard rule)

`opencode/*` models send the prompt **and any files they read** to opencode.ai servers.
**NEVER** delegate a task whose prompt or working directory contains private code,
credentials, `.env` files, personal data, or client material. Keep it in Claude.

## Steps

1. **Check availability.** Read `~/dev/claude-kb/hardware.md`, field `opencode:`.
   - `allowed` → continue.
   - `not-installed`, `not-allowed`, or field missing → **don't delegate**; go to step 6.
   Also confirm `ask-opencode` is on PATH (`command -v ask-opencode`).

2. **Choose the model** from `references/task-map.md`. Pick the cheapest model that clears
   the bar — never downgrade quality to save. Exact IDs come from the map, not from memory.

3. **Write the prompt: call the Skill tool with "write-for-model".** Small models fail differently
   than Claude: they ask for clarification instead of answering, or ignore the format. Put the
   **output lock in the first lines** ("NEVER ask questions. NEVER explain. Output only the
   JSON."), keep the structure **flat**, and add **few-shot** examples including the empty case.
   If the model ignores the format: **harden the prompt first, then change model.**

4. **Run it.**
   ```
   ask-opencode --model <id> "<prompt>"
   ask-opencode --model <id> --dir <repo> "<prompt>"     # task that reads/edits files
   ```
   - **NEVER pass `--unsafe`** unless the user explicitly asked for it in this session — it
     approves every tool permission, including destructive ones.
   - For file-editing tasks, run in a clean git tree so the change is reviewable as a diff.
   - Group subtasks on the same model; batch ~40 items per call.

5. **Mandatory QA — two distinct checks, not synonyms.**

   | Level | What it checks | What it catches |
   |---|---|---|
   | **Form** | schema, regex, length, required fields; for edits: `git diff` scope | broken output, edits outside scope |
   | **Content** | spot-check 3–5 cases against the source; for edits: read the diff | **hallucinations**, wrong logic |

   **Form without content gives false confidence.** Measured 2026-07-23: perfectly valid JSON
   with 2 of 4 values fabricated. Only the spot-check caught it.

   If QA fails, redo with a stronger model from the map, or do it yourself.
   **Two-strike rule:** if a **class** of task fails QA twice, stop delegating it and log the
   case in `references/task-map.md` so the next session doesn't repeat the cost.

6. **Fallback.** If `ask-opencode` exits ≠ 0 (exit 2 = opencode missing or model unavailable),
   or opencode is not allowed: **do it yourself**, or use a Claude subagent following the tier
   ladder `Haiku → Sonnet → Opus`. Never fail the task because the wrapper is missing.

## Hard constraints

- **Never use a pay-per-use model.** Only `opencode/*-free` models are allowed here.
- Never delegate private material (see Privacy).
- Never pass `--unsafe` without explicit user approval in this session.
- Claude always owns the QA of what comes back.
