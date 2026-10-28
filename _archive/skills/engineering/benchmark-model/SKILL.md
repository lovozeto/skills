---
name: benchmark-model
description: "Test a local model on representative tasks, measure quality and speed, and update the task-map in delegate with findings. Run after adding a new model or after a model update."
disable-model-invocation: true
argument-hint: "<model-id> [--tasks \"classify|summarize|extract|translate|code\"]"
allowed-tools: Bash(ask-local *), Bash(ask-apple *), Bash(lms *), Read, Write
---

> **ARCHIVED (2026-10-28).** Superseded by the `delegation` plugin (`plugins/delegation/`, skill `benchmark-model`), which adds local Ollama delegation, a data scan before cloud calls, and the `bench-model` benchmark.

# benchmark-model — measure a local model and update the routing map

Run after adding a new model to LM Studio or after a model update. Results feed
`references/task-map.md` in the `delegate` skill.

Model to test: **$ARGUMENTS**

## Steps

### 1. Identify the model and wrapper

- If model ID starts with `apple/` or you're testing `ask-apple`: use `ask-apple`.
- All others: use `ask-local --model <id>`.

Verify the model is loaded:
```bash
lms status    # for LM Studio models
```
If not loaded, say so and stop. Do not proceed with an unloaded model.

### 2. Run the task suite

Run each selected task class (default: all). Use the test cases below.
Record: output quality (pass/fail with reason), wall-clock time.

**Classify by form** — `ask-local --model <id> "Does this string contain a date? Answer YES or NO only. Input: 'Meeting on 2026-07-28 at 3pm'"`
Expected: `YES`

**Classify by world knowledge** — `ask-local --model <id> "Is WebP still the recommended image format for web in 2026? Answer YES or NO only."`
Trap: if it answers confidently without caveats, flag as hallucination risk for world-knowledge tasks.

**Summarize** — Feed a 500-word paragraph and ask for a 3-sentence summary. Check: factually accurate, no invented details.

**Extract fields** — Feed a JSON-like blob and ask to extract 3 fields as JSON. Check: valid JSON, correct fields.

**Translate prose** — Translate a short paragraph. Check: fluent, no omissions.

**Code (mechanical)** — Ask to rename a variable across a 30-line code block. Check: all instances renamed, no logic changes.

### 3. Measure timing

Time each call: `time ask-local --model <id> "<prompt>"`. Note warm vs. cold start if relevant.

### 4. Gate — present findings

Present a results table:

| Task class | Pass? | Time (warm) | Notes |
|---|---|---|---|
| Classify by form | ✅ / ❌ | Xs | |
| Classify by world knowledge | ✅ / ❌ | Xs | hallucination? |
| Summarize | ✅ / ❌ | Xs | |
| Extract fields | ✅ / ❌ | Xs | |
| Translate | ✅ / ❌ | Xs | |
| Code (mechanical) | ✅ / ❌ | Xs | |

**STOP.** Ask for confirmation before writing anything.

### 5. Update `task-map.md`

Read `references/task-map.md` in the `delegate` skill
(default path: `~/.agents/skills/lovozeto__skills/skills/engineering/delegate/references/task-map.md`
or wherever skills are installed).

Update the local models table with the new row. If the model already exists, update its row.
Add a date stamp to the notes column.

If any task class failed QA twice in this run, add it to the two-strike log at the bottom
of the file.

## Rules

- Do not run this during a work session — it consumes time and may interfere with active model state.
- Do not mark a task class as "pass" without spot-checking at least 3 outputs.
- If `ask-local` exits with code ≠ 0, note it and skip that task class — do not fail the benchmark.
