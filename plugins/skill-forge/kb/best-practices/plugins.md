---
tier: advisory
last_verified: 2026-10-23
review_by: 2026-11-23
---

# Best practices — plugins

`tier: advisory` · refreshed 2026-10-23 from Claude Code docs (plugins, manifest reference,
marketplace reference).

- **When a plugin.** A plugin packages and distributes several components (skills, agents,
  hooks, MCP, own scripts) as one versioned unit. Hooks, skills, and MCP also work standalone
  in settings; choose a plugin when the artifact must ship them together or to other people.
  Every enabled plugin's descriptions cost context on every turn.
- **Manifest.** `.claude-plugin/plugin.json`; only `name` is required (kebab-case; no
  `claude-`/`anthropic-` prefixes). `version`, `description`, `author` are recommended
  (validate warns without them). Components live at the plugin root, not in `.claude-plugin/`.
  A `CLAUDE.md` at the plugin root is not loaded: put instructions in a skill.
- **Paths.** Start with `./`, stay inside the root. `skills` adds to `skills/`; `commands`,
  `agents` replace their default dir; `hooks`, `mcpServers` merge with `hooks/hooks.json`,
  `.mcp.json`. `bin/` is added to the Bash PATH.
- **Variables.** `${CLAUDE_PLUGIN_ROOT}` changes on every update (never store state there);
  `${CLAUDE_PLUGIN_DATA}` persists. Both resolve in hooks, MCP config, and skill/agent bodies,
  but not in commands Claude runs through the Bash tool. Quote them in shell-form hooks.
- **Version pins users** until it changes: bump it with every change you ship.
- **Validate.** `claude plugin validate <dir>` (add `--strict` to fail on warnings) after every
  manifest change.
- **Marketplace.** `.claude-plugin/marketplace.json` needs `name`, `owner.name`, `plugins[]`
  with `name` + `source` (`./path`, github, git-subdir, url, npm, …). `strict` defaults to
  true; reserved names are rejected.
- **Own deps ship inside.** Universal deps go in a setup file, gated by a preflight hook.
- **Least surprise.** Behaviour matches the description; no hidden effects.
