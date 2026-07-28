---
name: ask-knowledge-base
description: "Explain a knowledge base rule in plain language, grounded in the KB (not memory). Use when the user asks what a rule/convention means, why it exists, or where it comes from."
argument-hint: "{your question}"
---

# ask-knowledge-base — explain a KB rule in plain language

Read-only. Explain inline — the answer stays in the main context so the user can keep asking.

Question: **$ARGUMENTS**

## How to explain

1. Find the rule in the knowledge base. **Start at the KB's `INDEX.md`** (default path: `~/dev/claude-kb/INDEX.md`) and open **one file only** (never an entire folder).
2. Define in plain language **before** using any technical term.
3. **Name the pattern**, so the user can search for it later.
4. Say where it comes from: which file, which source, from what date.
5. If there are two valid paths, say **which one you'd choose and why**. Don't list pros and cons for the user to decide.

## Hard rule

If the KB doesn't cover the question, **say so**. You can explain from general knowledge, but mark it explicitly as **outside the KB, unverified**. Never present memory as if it were a verified rule.

## Scope

Only explain the rule that was asked. Don't expand to adjacent topics on your own initiative — if you notice something relevant nearby, mention it in one line, don't develop it.
