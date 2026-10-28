# Model Prompting Guide

Reference for `write-for-model`. Update after running `/benchmark-model` or measuring
new behavior. Each section documents strengths, gotchas, and the recommended prompt shape.

---

## Free cloud models via `ask-opencode` (measured 2026-10-23)

Run through `ask-opencode`, which isolates them (no `CLAUDE.md`, empty folder in text mode).
Free ids rotate: the live list and measured results are in the `delegate` skill's
`references/task-map.md`. NOT for private code or personal data.

Shared shape that worked for every model in the benchmark:
- Output lock first: "Output ONLY <format>, no code fences." Then the task, then the input.
- Name the exact schema and a value for ambiguous fields (e.g. `Use "yo" for the person
  writing`): without it, models invented "Usuario".
- For agentic edits, say what must stay untouched ("change nothing else; string literals and
  comments stay"): three models renamed a string literal the task excluded.
- For rewrites, list the facts that must survive ("keep the deadline"): three Gemini models
  dropped it.
- Ask for a fixed final reply ("reply exactly: DONE") and check it: glm and the Nemotron
  models explained instead.

### `opencode/deepseek-v4.1-flash-free` (default)
- Best for: extraction, rewrites, conversions, agentic edits. 3/3 correct, 3–11 s.
- Data: zero retention, no training.

### `opencode/glm-5.3-flash-free`
- Best for: images, PDFs, screenshots; warm Spanish rewrites.
- Gotcha: tends to explain instead of the fixed final reply.
- Data: zero retention, no training.

### `opencode/beam-free`
- Best for: fast short tasks (titles, summaries). Flatter tone in rewrites.
- Data: no training, 30-day retention, region-limited.

### `google/gemini-3.1-flash-lite` (fallback, non-sensitive only)
- Good at JSON and code edits; dropped meaning in a rewrite.
- Data: free tier — Google may use and human-review prompts.

---

## LM Studio models (local, one-shot, private) — PAUSED

Local delegation is paused (see `delegation.md`). Kept as a measured record.

These run via `ask-local`. No internet. Context size varies by model.

### `google/gemma-4-e4b`
- Best for: classification (by form), field extraction, multilingual tasks
- Gotchas: small context; may ask for clarification instead of answering — lock the output format in line 1
- Prompt shape: output lock first ("NEVER ask. Output only: ..."), then task, then 2–3 examples including empty case

### `qwen/qwen3.5-9b`
- Best for: long-document summarization, general local tasks
- Gotchas: hallucinations on world-knowledge classification; loses constraints after ~3 in one prompt
- Prompt shape: one constraint per call; flat structure; explicit output format

### `qwen/qwen3-coder-30b`
- Best for: code generation, code review, boilerplate
- Gotchas: large model, slow cold start (~21s); best when grouped in batches
- Prompt shape: provide file context explicitly; specify language in the first line

### `microsoft/phi-4-reasoning-plus`
- Best for: math, STEM, logical reasoning
- Gotchas: verbose by default; add "Be concise." at the end of the prompt
- Prompt shape: state the problem cleanly; let it reason; specify output format after the problem

---

## Apple on-device (via `ask-apple`) — PAUSED

- Best for: short, structured, fast tasks (~2s). Classification by form, quick rewrites.
- Hard limit: macOS ≥ 26 required. No internet. Very short context.
- Prompt shape: one sentence of task + "Output only: [format]" — nothing more
- Gotchas: fails multi-constraint prompts; give one instruction at a time
