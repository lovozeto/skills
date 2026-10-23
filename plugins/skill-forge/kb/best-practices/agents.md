---
tier: advisory
last_verified: unknown
review_by: 2026-10-22
---

# Best practices — agents (subagents)

`tier: advisory` · seed (unverified). Refresh via `/refresh-forge-kb`.

- **One task per agent.** A subagent does exactly one thing and returns the result or
  `OUT OF SCOPE`. It never expands scope. This is what keeps token cost down and quality up.
- **Least privilege tools.** Give the agent only the tools its one task needs.
- **Mandatory model.** Declare the launch model with an equivalence fallback (see
  `../model-catalog.md`). Workers get the cheapest capable tier; orchestrators get reasoning.
- **Structured output.** Have the agent return a fixed shape the orchestrator can verify
  (schema / sanity check) rather than prose.
- **No assumptions.** If an input is missing, flag it and stop — do not invent it.
- **Isolation.** Agents run in their own context; pass them exactly what they need, not the
  whole conversation.

## To verify / expand via refresh
- Anthropic "Building effective agents" — orchestrator-worker and evaluator patterns.
- Claude Code subagent frontmatter fields and tool scoping.
- OpenAI Agents SDK — handoffs, guardrails, tracing patterns worth porting.
