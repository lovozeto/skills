---
tier: advisory
last_verified: 2026-10-23
review_by: 2026-11-23
---

# Best practices — agents (subagents)

`tier: advisory` · refreshed 2026-10-23. Tags: [CC] Claude Code docs, [A] Anthropic docs,
[AE] Anthropic engineering, [O] OpenAI.

## Design
- **Simplest thing first.** Add agents only when evals show they help; workflows (fixed code
  paths) before agents (self-directed). Patterns: routing, parallelization,
  orchestrator-workers, evaluator-optimizer (needs clear criteria). [AE]
- **One task per agent.** Returns the result or `OUT OF SCOPE`; never expands scope.
- **When multi-agent pays.** High-value, parallelizable, independent work; not tasks with
  shared context or many dependencies. Current Claude models over-delegate: work directly for
  simple, sequential, single-file tasks. [A][AE]
- **The brief.** Objective, output format, tool/source guidance, and task boundaries; vague
  briefs cause duplicated work and gaps. [AE]
- **Structured, compact returns.** A fixed shape the orchestrator can verify; large outputs go
  to files and the agent returns a reference (~1–2k-token summaries). [AE]
- **No assumptions.** If an input is missing, flag it and stop.
- **Isolation.** Pass exactly what the task needs. Give absolute paths: a subagent does not run
  from its definition file's folder.

## Claude Code mechanics [CC]
- **Frontmatter:** `name` + `description` required; optional `tools`, `disallowedTools`,
  `model` (`haiku|sonnet|opus|fable|<full id>|inherit`), `permissionMode`, `maxTurns`,
  `skills` (preloaded; user-invoked skills cannot be), `mcpServers`, `hooks`, `memory`,
  `background`, `omitClaudeMd`, `effort`, `isolation: worktree`. Unknown keys are ignored.
- **Tools:** `tools` is an allowlist (omit = inherit all); `disallowedTools` a denylist.
  Specifiers do not narrow a tool (`Bash(git push *)` removes all Bash); block commands with
  `permissions.deny` or a hook.
- **Nesting:** subagents can spawn subagents (default depth 3). Remove the `Agent` tool to stop it.
- **Plugin agents ignore** `hooks`, `mcpServers`, `permissionMode`, `initialPrompt`; ship
  hooks in `hooks/hooks.json` and MCP in `.mcp.json` instead.
- **Descriptions short:** combined custom agent descriptions above ~15k tokens trigger a warning.

## Model
- **Mandatory model** with an equivalence fallback (see `../model-catalog.md`): workers get the
  cheapest capable tier, orchestrators reasoning.

## Evaluation
- **Small samples early; judge outcome and process** (LLM judge with a rubric + human check);
  guard failure modes such as spawning many agents for a simple query. [AE]
