---
tier: advisory
last_verified: unknown
review_by: 2026-10-22
---

# Best practices — skills

`tier: advisory` · seed (unverified). Refresh via `/refresh-forge-kb`.

- **Description is the trigger.** Put all "what it does AND when to use it" in the
  `description`. Be specific and a little pushy (skills tend to under-trigger). Keep "when to
  use" out of the body.
- **Progressive disclosure.** Three levels: metadata (always in context), `SKILL.md` body
  (loads on trigger; keep under ~500 lines), bundled resources (loaded on demand).
- **Organize by variant.** For multi-domain skills, split references by variant
  (`references/aws.md`, `references/gcp.md`) and load only the relevant one.
- **Master orchestrator.** A skill orchestrates; heavy sub-work goes to single-task
  subagents.
- **State the effect.** Read-only vs effective, at the top. Effective skills gate every
  irreversible action.
- **Pointer, not copy.** Reference the KB; do not paste knowledge that other skills also need.

## To verify / expand via refresh
- Claude Code skill schema (frontmatter fields, `disable-model-invocation`, `argument-hint`).
- agentskills.io portable standard vs Claude Code extensions.
