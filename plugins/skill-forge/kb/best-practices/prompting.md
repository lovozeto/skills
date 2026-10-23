---
tier: advisory
last_verified: 2026-10-23
review_by: 2026-11-23
---

# Best practices — prompting

`tier: advisory` · refreshed 2026-10-23 from official docs (Anthropic, OpenAI, Google) and
Matt Pocock's `writing-for-agents`. Sources in `../sources.md`; tags: [A] Anthropic docs,
[AE] Anthropic engineering, [O] OpenAI, [G] Gemini, [M] writing-for-agents.

## Writing instructions
- **Clear, direct, imperative.** Write as for a brilliant new colleague with no context
  ("Read X", "Return Y"); numbered steps when order or completeness matters. Recent models
  follow wording literally: "can you suggest changes" yields suggestions only. [A][G]
- **Give the reason.** State why a constraint exists; the model generalizes from the reason
  better than from a bare rule. [A]
- **Positive target first.** Say what to do, not only what to avoid; a prohibition makes the
  banned behaviour more available. Keep a prohibition only as a hard guardrail, paired with
  the positive target. [A][M]
- **No new shouting.** Aggressive emphasis (CRITICAL, MUST, all caps) overtriggers tools and
  skills on current Claude models; prefer normal wording plus the reason. [A]
- **Preserve strength words when editing or translating.** Existing `NEVER`/`ALWAYS` and
  negations are not softened or flipped by an edit or translation; that silently breaks a
  system. (Writing new text follows the two rules above.)
- **Preserve identifiers verbatim.** Code, flags, paths, and names are not translated or
  paraphrased.
- **Right altitude.** Between brittle hard-coded logic and vague guidance; start minimal and
  add detail from observed failures. [AE]

## Structure
- **Separate parts with delimiters.** XML tags (`<instructions>`, `<context>`, `<input>`) or
  Markdown headings; pick one format and use it consistently. [A][O][G]
- **Order.** Role/identity, instructions, examples, context. For long inputs (20k+ tokens) put
  documents first and the question last, and ask for relevant quotes first. [A][O][G]
- **Examples steer best.** 3–5 relevant, varied examples, wrapped in `<example>` tags,
  including the edge/empty case. [A][G]
- **Specify output format.** Show the exact shape; for complex schemas use structured outputs
  or tools with enums instead of prompt-only formatting. Prefill is unsupported on Claude 4.6+. [A][G]

## Context
- **Least context.** Give an agent exactly what its one task needs; context is finite and
  recall degrades as it grows ("context rot"). Keep identifiers (paths, links) and load data
  just in time. [AE]
- **Cache only what cannot be found by looking.** Restating the environment (scripts, config,
  layout) is a cache that goes stale; write down the unwritten convention, the reason, the
  gotcha. [M]
- **Prune no-ops.** A sentence the model already obeys by default costs load and says nothing;
  delete the whole sentence, or use a stronger word. [M]

## Behaviour
- **Explicit over implicit.** State preconditions; if a required input is missing, stop and
  flag it rather than guessing. (Gemini's guide is looser — proceed on available information
  unless a later step needs it; this KB keeps the stricter rule.) [A][G]
- **Thinking.** Current Claude models use adaptive thinking driven by `effort`; prefer "think
  thoroughly" over hand-written step plans; do not ask the model to outline steps it already
  reasons through. [A][G]
- **Autonomy.** Reversible local actions freely; ask before destructive, hard-to-reverse, or
  externally visible actions. [A][G]

## To verify / expand via refresh
- Per-model prompting pages (Claude Opus/Sonnet/Haiku 5.5, Fable 5.1) — not fetched this round.
- Verbatim re-check of quotes (this round's fetches were summarized).
