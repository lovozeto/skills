---
name: offload-to-local
description: Decide whether to offload a token-heavy, low-reasoning task (summarize, classify, extract fields, translate, rewrite/clean text, convert format, mechanical code refactor, read/summarize long code) to a free local model instead of spending Claude tokens. Use before running any such task.
---

# offload-to-local — route a task to the cheapest model that clears the bar

The full task→wrapper→model map lives in `references/task-map.md` (ships with this skill).
This skill is the **how**, not the copy.

## When it applies

Only if the task is **high in tokens but simple in reasoning** and the result coming back is **compact**. If the task is already small, **don't offload** — coordination overhead costs more than the tokens saved.

Offloadable: summarize long text/log, extract structured fields, translate prose, rewrite/clean text, convert format (JSON/CSV/Markdown), boilerplate or mechanical code refactor, read/summarize long code.

**Not** offloadable: reasoning, architecture, decisions, critical code, QA, web search (local models have no internet).

### "Classify" splits into two — it is not one thing

| Type | Example | Offloadable? |
|---|---|---|
| **By text form** | Does this name contain a date? What language is this? | **Yes** |
| **By world knowledge** | Is this codec still supported? Is this library deprecated? | **No** |

It looks mechanical, but if the correct answer requires knowing something about the world, a local model **hallucinates confidently**. Measured 2026-07-23: `qwen3.5-9b` classifying format risk got 2 of 4 wrong and stated "Apple deprecated QuickTime in 2017" — false, said without a hint of doubt. That judgment stays with Claude.

### Translating instruction files — not the same as translating prose

Translating a README is safe. Translating a `SKILL.md`, agent, or command to English is **high risk**: a translated identifier, a softened `NEVER`, or an inverted negation silently breaks the system. See `references/task-map.md` for the full protocol.

### One constraint per instruction

Local models **lose constraints when given several at once**. Measured: `ask-apple` was asked for "10 examples, 6 in Spanish and 4 in English, varied, no tool names mentioned" and returned 10 in Spanish with duplicates. If you need multiple conditions, **split into separate calls** or accept finishing the remainder yourself. Don't escalate the tier for this before hardening the prompt.

## Steps

1. **Read `hardware.md`** in the active profile (set up by lobomorir-ai-setup) → which local models are available on this machine. If it doesn't exist or says `delegation_local: not-configured` (e.g. unregistered machine): **don't delegate to local**, use the Claude tier ladder and continue.

2. **Tier ladder — quality → savings:** `local → Haiku → Sonnet → Opus`. Choose the **cheapest that clears the bar** for the task. Never downgrade quality to save.

3. **Choose the wrapper** from the map in `references/task-map.md`: light text → `ask-apple`; medium/large context, conversions → `ask-local`; mechanical code → `ask-local` with a coder model. Exact IDs come from the map + hardware.md, not from memory.

   `ask-apple` and `ask-local` should be on PATH after setup:
   ```
   ask-apple "<prompt>"
   ask-local --model <id> "<prompt>"
   ```

   **Short structured tasks → `ask-apple` first** (~2s measured, vs ~9s for a warm local and ~21s cold). **Group** subtasks on the same model — switching costs ~12s swap (one model at a time).  Batch size: ~40 items.

4. **Write the prompt with `/write-for-model`, not freehand.** Local models have limited context and fail differently than Claude: they ask for clarification instead of answering, or ignore the format. A prompt for a local model needs the **output lock in the first lines** ("NEVER ask questions. NEVER explain. Output only the JSON."), a **flat** structure — nesting loses them — and **few-shot** examples including the empty case.

   Measured: `gemma-4-e4b` with an unoptimized prompt returned questions instead of the JSON asked for.

   If the local ignores the format: **harden the prompt first, then escalate the tier.** Escalating for a poorly written prompt overpays for a problem that was yours.

5. **Mandatory QA — and these are TWO distinct things, not synonyms.**

   | Level | What it checks | What it catches |
   |---|---|---|
   | **Form** | schema, regex, length, required fields present | broken or malformatted output |
   | **Content** | spot-check 3–5 cases against the source | **hallucinations** |

   **Validating form without a spot-check gives false confidence.** Measured 2026-07-23: `qwen3.5-9b` returned perfectly valid JSON — with 2 of 4 values fabricated. The schema passed clean. The only check that caught it was reading 4 cases against the real data.

   It's cheap (reading a compact result is far less than generating it). If it fails, redo one tier up. Don't assume someone else reviewed.

   **Two-strike rule:** if a **class** of task fails QA twice, stop delegating it — don't keep retrying. Log the case in `references/task-map.md` so the next session doesn't repeat the cost.

6. **Fallback:** if a wrapper exits with code ≠ 0 (unavailable), **do it yourself** or move one tier up. Never fail the task because of a missing wrapper.

## Hard constraints

- **Never use a pay-per-use model** — Kimi, Gemini API/CLI are out.
- `ask-apple` requires macOS ≥ 26; `ask-local` requires LM Studio with a loaded model. Both wrappers exit with code 2 if unavailable — apply the fallback in step 6.
- If neither wrapper is on PATH, the skill explains how to set them up. Never fail the task just because the wrapper is missing — fall through to the Claude tier ladder.

For the detailed map, LM Studio control via `lms`, and complete prerequisites: read `references/task-map.md` (ships with this skill).
