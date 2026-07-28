# Task → Model Map

Reference for `offload-to-local`. Update this file when you run `/benchmark-model`
and discover a better model for a task class.

## Tier ladder (quality → savings)

```
local (ask-apple / ask-local) → claude-haiku → claude-sonnet → claude-opus
```

Always choose the cheapest tier that clears the quality bar. Never downgrade quality to save.

## Wrapper selection

| Wrapper | When to use |
|---|---|
| `ask-apple` | Short, structured tasks (~2s). Text light, single-pass. |
| `ask-local` | Medium/long context, code, conversions, multi-constraint. Auto-manages LM Studio. |

**Group subtasks by model** — switching models costs ~12s swap (one model at a time policy).
**Batch size: ~40 items** — longer degrades format adherence; shorter wastes coordination overhead.

## Task classification

| Task class | Delegable to local | Notes |
|---|---|---|
| Summarize long text/log | ✅ Yes | ask-apple for short, ask-local for long |
| Extract structured fields | ✅ Yes | Verify form + spot-check content |
| Translate prose | ✅ Yes | ask-apple |
| Rewrite / clean text | ✅ Yes | |
| Convert format (JSON, CSV, Markdown) | ✅ Yes | |
| Boilerplate / mechanical code refactor | ✅ Yes | ask-local with coder model |
| Read/summarize long code | ✅ Yes | ask-local |
| Classify by text form | ✅ Yes | e.g. "does this contain a date?" |
| Classify by world knowledge | ❌ No | Local models hallucinate confidently |
| Translate SKILL.md / agent / command | ⚠️ High risk | See portability notes below |
| Reasoning / architecture / decisions | ❌ No | Keep on Claude |
| Critical code | ❌ No | |
| QA / verification | ❌ No | |
| Web search / current events | ❌ No | Local models have no internet |

## Translating instruction files — read this before delegating

Translating a README is safe. Translating a `SKILL.md`, agent, or command to English
is **high risk**: a translated identifier, a softened `NEVER`, or an inverted negation
silently breaks the system. Protocol:
1. Prompt that preserves code blocks and identifiers verbatim
2. 4-point QA per file: identifiers unchanged, NEVER/ALWAYS strength preserved,
   negations intact, no hallucinated content
3. Two-strike rule: if a file class fails QA twice, stop delegating it

## Local models available (update per machine)

This section is populated by `lobomorir-ai-setup` profile setup.
If not configured, use the Claude tier ladder only.

| Wrapper | Model ID | Best for |
|---|---|---|
| ask-apple | Apple on-device FM | Short structured, fast (~2s) |
| ask-local | google/gemma-4-e4b | Light tasks |
| ask-local | qwen/qwen3.5-9b | General local |
| ask-local | qwen/qwen3-coder-30b | Code tasks |
| ask-local | microsoft/phi-4-reasoning-plus | Reasoning-light |

Update this table after running `/benchmark-model`.
