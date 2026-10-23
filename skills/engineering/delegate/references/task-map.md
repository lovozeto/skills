# Task → Model Map

Reference for `delegate`. Scope for now: **opencode free models only**, run through
`ask-opencode`. Update this file when a model is added, removed, or fails a task class twice.

## Tier ladder (quality → savings)

```
opencode free (ask-opencode) → claude-haiku → claude-sonnet → claude-opus
```

Always choose the cheapest tier that clears the quality bar. Never downgrade quality to save.

## Models

Source of truth for the IDs: the header of the `ask-opencode` wrapper
(`lobomorir-ai-setup/shared/.claude/scripts/ask-opencode`, installed as `~/.local/bin/ask-opencode`). Per-model system prompts live
next to it in `opencode-prompts/`.

| Model ID | Best for |
|---|---|
| `opencode/north-mini-code-free` | Fast mechanical tasks — default |
| `opencode/laguna-s-2.1-free` | Multi-step coding, terminal agent, 1M context |
| `opencode/nemotron-3-ultra-free` | Reasoning-light analysis, complex debugging (Claude still decides) |
| `opencode/mimo-v2.5-free` | Tasks with screenshots, UI, or diagrams |

## Task classification

| Task class | Delegable | Model | Notes |
|---|---|---|---|
| Summarize long text/log | ✅ Yes | north-mini-code | laguna for very long input |
| Extract structured fields | ✅ Yes | north-mini-code | Verify form + spot-check content |
| Translate prose | ✅ Yes | north-mini-code | |
| Rewrite / clean text | ✅ Yes | north-mini-code | |
| Convert format (JSON, CSV, Markdown) | ✅ Yes | north-mini-code | |
| Rename / format / search across a repo | ✅ Yes | north-mini-code | `--dir <repo>`, review diff |
| Boilerplate / mechanical code refactor | ✅ Yes | laguna-s-2.1 | `--dir <repo>`, review diff |
| Read/summarize long code | ✅ Yes | laguna-s-2.1 | 1M context |
| Describe a screenshot / UI / diagram | ✅ Yes | mimo-v2.5 | |
| Classify by text form | ✅ Yes | north-mini-code | e.g. "does this contain a date?" |
| Classify by world knowledge | ❌ No | — | Small models hallucinate confidently |
| Translate SKILL.md / agent / command | ⚠️ High risk | laguna-s-2.1 | See protocol below |
| Architecture / decisions / critical code | ❌ No | — | Keep on Claude |
| QA of a delegated result | ❌ No | — | Claude always owns QA |
| Private code, credentials, personal data | ❌ No | — | opencode is cloud — data leaves the machine |

## Translating instruction files — read this before delegating

Translating a README is safe. Translating a `SKILL.md`, agent, or command is **high risk**:
a translated identifier, a softened `NEVER`, or an inverted negation silently breaks the
system. Protocol:
1. Prompt that preserves code blocks, paths, backticks, and identifiers verbatim
2. 4-point QA per file: identifiers unchanged, NEVER/ALWAYS strength preserved,
   negations intact, no hallucinated content
3. Two-strike rule: if a file class fails QA twice, stop delegating it

## Failure log

Record task classes that failed QA twice here (date, model, task class, what went wrong).

| Date | Model | Task class | Failure |
|---|---|---|---|
