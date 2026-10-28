---
name: write-for-model
description: Build a prompt tuned to one delegation target (a local Ollama model, an opencode agent, or a free cloud model). Use before every delegated call, and when the user asks for a prompt for a local or free delegation model.
argument-hint: "[--target <model-id>] [--task <description>]"
---

# write-for-model

Small models fail differently from Claude: they ask questions instead of answering, drop
constraints, or edit what they were told to leave alone. This skill adds the target model's
known habits to `prompt-master`, which writes the prompt.

## 1. Target

Use the model id the caller passed. If there is none, ask the user which model will receive
the prompt.

## 2. Model context

Load what is known about the target, first source that works:

1. `kb search "<model id>" --base delegation` and `kb get delegation/prompting`.
2. `$KB_ROOT/INDEX.md` → the `delegation/prompting.md` entry.
3. Neither: use only the shape below and note "target unmeasured".

The shape that worked across models:
- Lock the output format in the first lines ("Output ONLY <format>, no code fences."), then
  the task, then the input.
- Give the exact schema and a value for every ambiguous field.
- For edits, name what stays untouched (strings, comments, other files).
- For rewrites, list the facts that must survive.
- End with a fixed final reply ("reply exactly: DONE") and check it.
- One constraint per instruction; split a task that needs several.
- Add few-shot examples, including the empty case.

## 3. Write it with prompt-master

`prompt-master` is required. If the Skill tool lists it under any name (for example
`prompt-master` or `<namespace>:prompt-master`), call it by that exact listed name. If it is
not listed, stop and tell the user to install it:
`npx skills add nidhinjs/prompt-master -g -y -a claude-code`.

Call the Skill tool with that name, passing:

```
Target tool: <model id>
Model-specific context: <what step 2 found>
Task to build a prompt for: <the task>
```

## 4. Check the prompt

- It follows the shape and the target's known habits from step 2.
- For a cloud target, it carries no data or credentials: describe the data's structure
  instead of pasting it.
- It never asks a model to bypass its safety rules.

If a check fails, fix the prompt and check again. Done when all three pass.

Return the final prompt and one line: `Target: <model id> — <what was tuned and why>`.
