---
tier: advisory
last_verified: unknown
review_by: 2026-10-22
---

# Best practices — prompting

`tier: advisory` · seed (unverified). Refresh via `/refresh-forge-kb`.

- **Imperative instructions.** Write skill/agent bodies in the imperative ("Read X", "Return
  Y"), not narration.
- **Specify output format.** Show the exact shape you expect; verify it before use.
- **Preserve strength words.** `NEVER`/`ALWAYS` carry load — never soften them when editing or
  translating; a flipped negation silently breaks the system.
- **Preserve identifiers verbatim.** Code, flags, paths, and names are not translated or
  paraphrased.
- **Least context.** Give an agent exactly the inputs its one task needs.
- **Explicit over implicit.** State preconditions; if an input is missing, stop and flag it
  rather than guessing.

## To verify / expand via refresh
- Anthropic prompting docs (tool use, structured output reliability).
- OpenAI and Gemini prompting guides — portable patterns for structured output and refusal
  handling.
