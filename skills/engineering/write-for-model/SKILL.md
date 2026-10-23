---
name: write-for-model
description: Build an optimized prompt for a specific delegation target (a free model via ask-opencode, or an external tool). Invoke before delegating a task to ensure the prompt matches what the target model actually responds to well. Wraps prompt-master with model-specific context.
argument-hint: "[--target <model-id>] [--task <description>]"
---

# write-for-model

Wrapper around `prompt-master` that adds model-specific prompting context before invoking it.
Use this any time you need to build a prompt for a specific delegation target — whether from
`/delegate` or a manual request to optimize a prompt for a given model.

`prompt-master` knows Claude, Lovable, Cursor, v0, and similar tools well. It does NOT know
the opencode free models or LM Studio models. This skill provides that gap.

## When to invoke

- Manual: user asks "write a prompt for deepseek", "optimize this for glm", "I want to pass this to ask-opencode".
- Automatic: called from `/delegate` when the task requires building a prompt for a specific executor.

## Step 1 — Identify the target

If `--target` was not provided, ask:

> **Which model or tool will receive this prompt?**
>
> **Free cloud via `ask-opencode`:** the current models and what each is for are listed in
> the `delegate` skill's `references/task-map.md` (default: `opencode/deepseek-v4.1-flash-free`).
>
> **LM Studio / Apple fm:** paused for now (see `~/dev/claude-kb/delegation.md`).
>
> **Other:** Apple fm, Claude Code, Lovable, v0, Cursor, etc.

Wait for the answer before proceeding.

## Step 2 — Load model context

For `ask-opencode` targets (opencode/* or google/*):
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
- Does NOT include elements the model handles poorly (see the model's section in the guide).
- Includes a system prompt note if the model needs one (some models ignore system prompts — the guide says which).

If the output is missing critical elements for the target, adjust it before returning.

## Output

Return the final prompt, ready to pass to `ask-opencode`.
Add a one-line note: 🎯 Target: [model id] — what was optimized and why.

## Rules

- NEVER build prompts that ask a model to override its safety constraints.
- If the target model's system prompt should be minimal (e.g., Nemotron 3 Ultra), say so — do not pad it.
- If the task involves private code or credentials and the target is an opencode/* (cloud) model, warn the user and suggest a lmstudio/* alternative.
