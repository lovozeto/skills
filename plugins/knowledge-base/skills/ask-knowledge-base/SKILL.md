---
name: ask-knowledge-base
description: "Explain a knowledge base rule in plain language, grounded in the KB (not memory). Use when the user asks what a rule/convention means, why it exists, or where it comes from. Not for changing a rule (update-knowledge-base) or researching a topic (kb-pipeline)."
argument-hint: "{your question}"
allowed-tools: Read, Bash(kb *)
disallowed-tools: Write, Edit, NotebookEdit
---

# ask-knowledge-base — explain a KB rule in plain language

Read-only. Explain inline — the answer stays in the main context so the user can keep asking.

Question: **$ARGUMENTS**

## How to explain

1. Find the rule in the knowledge base. **Start with the `kb` CLI**: translate the question to
   English keywords and run `kb search "<query>" [--base <base>]`; then
   `kb get <base>/<file>#<section>` on the best hit (one section, never a whole file or folder).
   Do not add `--fresh` (it hides expired files, which would read as "not covered"); report
   expiry instead (step 4). Add `--tier proven` only if the user asks what was actually run.
   If `kb` is not on PATH or exits non-zero, fall back to `${KB_ROOT:-~/dev/claude-kb}/INDEX.md`
   and open **one file only**.
2. Define in plain language **before** using any technical term.
3. **Name the pattern**, so the user can search for it later.
4. Say where it comes from, in one line: `<base>/<file>#<section>`, the source (publisher + URL),
   its `last_verified` date, the file's `tier` (advisory or proven), and a warning if
   `review_by` has passed. The answer is not done until that line is present.
5. If there are two valid paths, say **which one you'd choose and why**. Don't list pros and cons for the user to decide.

## Hard rule

If `kb search` exits 0 with no hits (and the INDEX fallback has no matching file), the KB doesn't cover the question: **say so**. If `kb` fails or the KB folder is missing, say the KB could not be read instead; that is not "not covered". You can explain from general knowledge, but mark it explicitly as **outside the KB, unverified**. Never present memory as if it were a verified rule.

## Scope

Only explain the rule that was asked. Don't expand to adjacent topics on your own initiative — if you notice something relevant nearby, mention it in one line, don't develop it.
