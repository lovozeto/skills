---
tier: advisory
last_verified: 2026-10-23
review_by: 2026-11-23
---

# Best practices — skills

`tier: advisory` · refreshed 2026-10-23. Tags: [CC] Claude Code docs, [AS] agentskills.io,
[O] OpenAI Codex docs, [AE] Anthropic engineering, [M] writing-for-agents.

## The description is the trigger
- **What + when, front-loaded.** Lead with the trigger word and key use case; one trigger
  per distinct branch, no synonym padding; say when it should *not* trigger. Listings get
  truncated: Claude Code caps `description` + `when_to_use` at 1,536 chars; Codex budgets the
  whole skill list (~2% of context). [CC][O][M]
- **Keep when-to-use out of the body.** The body runs after the skill is chosen.

## Invocation (choose per skill, with a reason)
- **Model-invoked** (default): description always in context; the agent and other skills can
  reach it. Use when the agent must reach it on its own. [CC][M]
- **User-invoked** (`disable-model-invocation: true`): description not in context, cannot be
  preloaded into subagents, no other skill can call it; description becomes a one-line human
  summary. Use for side-effect skills that need a deliberate human trigger. [CC][M]
- **`user-invocable: false`**: hidden from the `/` menu, still model-invoked (background
  knowledge). [CC]
- **Codex parity:** `policy.allow_implicit_invocation: false` in `agents/openai.yaml` pairs with
  `disable-model-invocation: true`; explicit `$skill` still works. [O][M]

## Frontmatter
- **Portable core** ([AS]): `name` (1–64, lowercase, hyphens, = folder name), `description`
  (1–1024), optional `license`, `compatibility`, `metadata`, `allowed-tools`.
- **Claude Code extensions** ([CC]): `when_to_use`, `argument-hint`, `arguments`,
  `disable-model-invocation`, `user-invocable`, `disallowed-tools`, `model`, `effort`,
  `context: fork`, `agent`, `background`, `hooks`, `paths`, `shell`. Unknown keys are ignored
  silently, so a typo fails quietly.
- **Portability trap:** claude.ai uploads, the Skills API, and `package_skill.py` reject any key
  outside the portable core with a hard error. Keep extensions only where Claude Code runs it. [CC]
- **`allowed-tools` pre-approves, it does not restrict.** The grant lasts for the invoking turn.
  Restrict with `disallowed-tools`. [CC]

## Body and files
- **Progressive disclosure.** Metadata always loaded (~100 tokens); body loads on use and then
  stays in context (keep < 500 lines / ~5,000 tokens); `references/`, `scripts/`, `assets/`
  load on demand, linked one level deep from `SKILL.md`. Scripts run without entering
  context; mark files "run" vs "read". [CC][AS][AE]
- **Steps vs reference.** Inline what every branch needs; disclose what only some branches
  reach; keep a concept's definition and caveats together (co-location). [M]
- **Completion criteria.** Each step ends on a checkable, demanding criterion. [M]
- **Skill-to-skill calls.** "Call the Skill tool with "<name>"", one skill per call, only
  model-invoked targets; recommend user-invoked ones to the human by `/name`. [M]
- **Master orchestrator.** A skill orchestrates; heavy sub-work goes to single-task subagents.
- **State the effect.** Read-only vs effective, at the top; effective skills gate every
  irreversible action.
- **Pointer, not copy.** Reference the KB; one source of truth per meaning. [M]

## Building and safety
- **Evaluation-first.** Find where agents fail on representative tasks; test the description
  against sample prompts. [AE][O]
- **Validate.** `skills-ref validate <dir>` (agentskills.io reference validator). [AS]
- **Trusted sources only.** Audit bundled scripts and any instruction that reaches the network. [AE]
