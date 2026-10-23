# Task → Model Map

Reference for `delegate`. Free models only, run through `ask-opencode` (isolated: no
`CLAUDE.md`, empty folder in text mode). Update this file when a model is added, retired, or
fails a task class twice.

## Tier ladder (quality → savings)

```
free model (ask-opencode) → claude-haiku → claude-sonnet → claude-opus
```

Always choose the cheapest tier that clears the quality bar. Never downgrade quality to save.

## Models (measured 2026-10-23, `proven` on this machine)

Benchmark: JSON extraction from a Spanish WhatsApp RSVP, a Colombian-Spanish rewrite with
placeholders, and an agentic rename across two files (`--dir`), all isolated. Free ids change
often: a model is live only if a real call succeeds (`opencode models` and the Zen list both
lag). Re-run the benchmark when the KB flags this file as expired.

| Model ID | Use for | Data policy (Zen / Google docs) | Measured |
|---|---|---|---|
| `opencode/deepseek-v4.1-flash-free` | **Default** — text tasks and agentic edits | zero retention, no training | 3/3 correct, 3–11 s |
| `opencode/glm-5.3-flash-free` | Images, PDFs, screenshots; warm Spanish rewrites | zero retention, no training | 3/3 content correct; ignored "reply DONE" once |
| `opencode/beam-free` | Fast short tasks (titles, summaries) | no training, 30-day retention, region-limited | 3/3 correct, 3–7 s; flatter tone |
| `google/gemini-3.1-flash-lite` | Fallback for non-sensitive text when opencode is down | **free tier: Google may use and human-review it** | 3/3 code/JSON; dropped the deadline in the rewrite |

Not recommended now: `flint-40b-free` (slow, over-edits, may train), `nemotron-3-ultra-free`
(off the Zen list, over-edits), `nemotron-3.5-*-free` (Nvidia: "do not submit personal or
confidential data"), `mimo-v2.6-flash-free` (may train), `gemini-3.5-flash-lite` (over-edits,
drops meaning), `gemini-3.8-flash` (110–176 s, failed the agentic task), Gemini Pro / 4 Argon
(not on the free tier).

## Task classification

| Task class | Delegable | Model | Notes |
|---|---|---|---|
| Summarize long text/log | ✅ | deepseek-v4.1-flash | beam for short ones |
| Extract structured fields | ✅ | deepseek-v4.1-flash | Verify form + spot-check content |
| Translate / rewrite prose | ✅ | deepseek-v4.1-flash or glm-5.3-flash | Check placeholders and meaning kept |
| Convert format (JSON, CSV, Markdown) | ✅ | deepseek-v4.1-flash | |
| Rename / format / search across a repo | ✅ | deepseek-v4.1-flash, `--dir <repo>` | Review the diff: some models over-edit strings |
| Boilerplate / mechanical code refactor | ✅ | deepseek-v4.1-flash, `--dir <repo>` | Review the diff |
| Describe a screenshot / UI / diagram / PDF | ✅ | glm-5.3-flash | |
| Classify by text form | ✅ | deepseek-v4.1-flash | e.g. "does this contain a date?" |
| Classify by world knowledge | ❌ | — | Small models hallucinate confidently |
| Translate SKILL.md / agent / command | ⚠️ High risk | deepseek-v4.1-flash | See protocol below |
| Architecture / decisions / critical code | ❌ | — | Keep on Claude |
| QA of a delegated result | ❌ | — | Claude always owns QA |
| Private code, credentials, personal data | ❌ | — | Free models are third-party cloud |

## Translating instruction files — read this before delegating

Translating a README is safe. Translating a `SKILL.md`, agent, or command is **high risk**:
a translated identifier, a softened `NEVER`, or an inverted negation silently breaks the
system. Protocol:
1. Prompt that preserves code blocks, paths, backticks, and identifiers verbatim
2. 4-point QA per file: identifiers unchanged, NEVER/ALWAYS strength preserved,
   negations intact, no hallucinated content
3. Two-strike rule: if a file class fails QA twice, stop delegating it

## Failure log

| Date | Model | Task class | Failure |
|---|---|---|---|
| 2026-10-23 | flint-40b, nemotron-3-ultra, gemini-3.5-flash-lite | agentic rename | also renamed a string literal the task said to keep |
| 2026-10-23 | gemini-3.5-flash-lite, gemini-3.8-flash, gemini-3.1-flash-lite | rewrite | dropped the deadline from the reminder |
