# Model Prompting Guide

Reference for `write-for-model`. Update after running `/benchmark-model` or measuring
new behavior. Each section documents strengths, gotchas, and the recommended prompt shape.

---

## opencode free models (cloud, agentic)

These models run agentic loops (read/write files, bash). NOT for private code.

### `opencode/north-mini-code-free`
- Best for: fast, mechanical tasks — linting, formatting, small refactors
- Gotchas: limited reasoning; short context window; will hallucinate API details
- System prompt: minimal or none; put all constraints in the user message
- User message: imperative first line, then context; avoid numbered multi-step lists

### `opencode/laguna-s-2.1-free`
- Best for: multi-step coding tasks, terminal agent workflows
- Gotchas: **avoid nested arrays or deeply nested JSON in the prompt** — loses structure
- System prompt: one paragraph, plain prose; no bullets
- User message: flat structure; use code blocks for code, plain text for instructions

### `opencode/nemotron-3-ultra-free`
- Best for: reasoning, complex debugging, analysis
- Gotchas: **system prompt should be minimal or empty** — heavy system prompts reduce reasoning quality; avoid CoT instructions (it does CoT by default)
- User message: state the problem clearly; let it reason; don't over-constrain format

### `opencode/mimo-v2.5-free`
- Best for: tasks with screenshots, UI description, multimodal input
- Gotchas: weak at pure code generation
- System prompt: describe the output format; it follows formatting instructions well
- User message: describe what you see, then what you want

---

## LM Studio models (local, one-shot, private)

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

## Apple on-device (via `ask-apple`)

- Best for: short, structured, fast tasks (~2s). Classification by form, quick rewrites.
- Hard limit: macOS ≥ 26 required. No internet. Very short context.
- Prompt shape: one sentence of task + "Output only: [format]" — nothing more
- Gotchas: fails multi-constraint prompts; give one instruction at a time
