---
name: write-for-model
description: Build an optimized prompt for a specific delegation target (opencode model, LM Studio model, or external tool). Invoke before delegating a task to ensure the prompt matches what the target model actually responds to well. Wraps prompt-master with model-specific context.
argument-hint: "[--target <model-id>] [--task <description>]"
---

# write-for-model

Wrapper around `prompt-master` that adds model-specific prompting context before invoking it.
Use this any time you need to build a prompt for a specific delegation target — whether from
`/delegate` or a manual request to optimize a prompt for a given model.

`prompt-master` knows Claude, Lovable, Cursor, v0, and similar tools well. It does NOT know
the opencode free models or LM Studio models. This skill provides that gap.

## When to invoke

- Manual: user asks "write a prompt for Laguna S", "optimize this for Nemotron", "I want to pass this to ask-local".
- Automatic: called from `/delegate` when the task requires building a prompt for a specific executor.

## Step 1 — Identify the target

If `--target` was not provided, ask:

> **Which model or tool will receive this prompt?**
>
> **opencode (free cloud, agentic):**
> - `opencode/north-mini-code-free` — fast mechanical tasks
> - `opencode/laguna-s-2.1-free` — multi-step coding, terminal agent
> - `opencode/nemotron-3-ultra-free` — reasoning, complex debugging
> - `opencode/mimo-v2.5-free` — tasks with screenshots or UI
>
> **LM Studio (local, one-shot, private):**
> - `lmstudio/google/gemma-4-e4b` — classification, extraction, multilingual
> - `lmstudio/qwen/qwen3.5-9b` — long-doc summarization
> - `lmstudio/qwen/qwen3-coder-30b` — code generation, review
> - `lmstudio/microsoft/phi-4-reasoning-plus` — math, STEM, logical reasoning
>
> **Other:** Apple fm, Claude Code, Lovable, v0, Cursor, etc.

Wait for the answer before proceeding.

## Step 2 — Load model context

For opencode/* or lmstudio/* targets:
1. Read the relevant section from `references/model-guide.md` (ships with this skill).
2. Extract: strengths, gotchas, recommended system prompt style, and user message format for that model.

For other tools (Claude, Lovable, v0, etc.): prompt-master already knows these — skip to Step 3 without enrichment.

## Step 3 — Build the enriched request for prompt-master

Construct the input for prompt-master as:

```
Target tool: [full model id]

Model-specific context:
[paste the relevant section from model-prompting-guide.md — strengths, gotchas, user message format]

Task to build a prompt for:
[user's task description]
```

Then call the Skill tool with "prompt-master", passing this enriched input.

## Step 4 — Validate the output

Check that the prompt prompt-master returned:
- Matches the user message format for the target model (from the guide).
- Does NOT include elements the model handles poorly (e.g., nested arrays for Laguna, CoT for Nemotron).
- Includes a system prompt note if the model needs one (some models ignore system prompts — the guide says which).

If the output is missing critical elements for the target, adjust it before returning.

## Output

Return the final prompt, ready to paste into `ask-opencode` or `ask-local`.
Add a one-line note: 🎯 Target: [model id] — what was optimized and why.

## Rules

- NEVER build prompts that ask a model to override its safety constraints.
- If the target model's system prompt should be minimal (e.g., Nemotron 3 Ultra), say so — do not pad it.
- If the task involves private code or credentials and the target is an opencode/* (cloud) model, warn the user and suggest a lmstudio/* alternative.
