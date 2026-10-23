---
tier: advisory
last_verified: unknown
review_by: 2026-10-22
---

# Best practices — plugins

`tier: advisory` · seed (unverified). Refresh via `/refresh-forge-kb`.

- **When a plugin.** Choose a plugin when the artifact needs hooks, slash commands, MCP, must
  package its own dependencies, or bundles several coordinated skills/agents.
- **Manifest.** `.claude-plugin/plugin.json` with `name`, `description` (what + when), and
  `author`. Add `version`.
- **Distribution.** A marketplace manifest (`.claude-plugin/marketplace.json`) lists plugins
  by `source` path so `/plugin marketplace add` + `/plugin install` work.
- **`${CLAUDE_PLUGIN_ROOT}`.** Reference bundled scripts/hooks by this variable, never by an
  absolute path.
- **Own deps ship inside.** Package proprietary scripts/assets in the plugin. Universal deps
  are declared in a setup file and gated by a preflight hook.
- **Least surprise.** The plugin's behavior must match its description; no hidden effects.

## To verify / expand via refresh
- Claude Code plugin & marketplace schema, component discovery (skills/agents/commands/hooks/MCP).
- Versioning and update flow.
