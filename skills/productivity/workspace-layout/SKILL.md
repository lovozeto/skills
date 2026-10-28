---
name: workspace-layout
description: "Map of ~/GitHub and the procedure to clone a new repo into the right folder or move one without breaking things. Use when cloning or creating a repo under ~/GitHub, moving or renaming a local repo folder, creating a git worktree, or asking where a project lives."
---

# workspace-layout

Rule (in `~/dev/claude-kb/CONVENTIONS.md`): each repo lives in its category folder; worktrees go
in `_temporal/`. The map below is the source of truth (approved 2026-10-28). Local folder name =
GitHub repo name.

## Map of ~/GitHub

- **Root:** only `lobomorir-ai-setup/` and `skills/` (`deploy.sh` links into both), plus `.claude/`.
- **entrepreneur-projects/:** ControlR (formerly "Xbox Play"; xcloud reference clones live git-ignored in `ControlR/refs/`), DumbTV, kb, deck-patcher (3 repos inside), SteamOSPatcher, Tesla-expandedTheater, karaoke-builder, shelfmark (formerly plex-library-manager).
- **lobomorir-projects/:** lobomorir-homelab, lobomorir-bootstrap, MackyGames.
- **syl-projects/:** SyL.
- **event-projects/** (temporary name): matrimonio-ivan-eliana, matrimonio-lobomorir, invitation-system.
- **github-apps/:** third-party MCPs, apps and tools Esteban asks to install (claudezilla, whatsapp-mcp, OpenEmu, OpenStore, mush8).
- **_temporal/:** git worktrees and throwaway clones only; may be emptied anytime.
- **Reference clones** go inside the repo that uses them, git-ignored (e.g. `<repo>/refs/`).

## Clone a new repo

1. Pick the category by who or what it is for: own product idea → `entrepreneur-projects`; lobomorir household/infra → `lobomorir-projects`; SyL → `syl-projects`; events → `event-projects`; someone else's tool to install → `github-apps`; worktree or throwaway → `_temporal`.
2. None fits: ask the user; do not create a category.
3. Clone with the GitHub repo name as the folder. Done when the repo sits at `~/GitHub/<category>/<repo>`.
4. A repo of ours with no board: run `setup-tracking <owner/repo>` (boards are keyed by GitHub repo, not folder).

## Move a repo without breaking things

Fix each check in the same step. Show the diff before editing any config.

1. **Absolute paths in config:** grep the old path in `~/.claude.json` (mcpServers, projects keys, githubRepoPaths), `~/Library/Application Support/Claude/claude_desktop_config.json` (MCP args, per-path permission modes), `~/Library/Application Support/Mozilla/NativeMessagingHosts/*.json`, `~/Library/LaunchAgents`.
2. **Worktrees:** `git worktree list` before moving; `git worktree repair` after.
3. **kb:** repo knowledge is found under `KB_PROJECTS_ROOT` (default `~/GitHub`), at most 4 levels deep (`<root>/<a>/<b>/<repo>/.claude/knowledge` is the deepest that works). Afterwards check `kb search --all` sees it.
4. **Claude Code memory and sessions** are keyed by path: `~/.claude/projects/<path with every non-alphanumeric char replaced by '-'>`. Rename that folder to the new key and fix paths inside its `memory/*.md`.
5. **Symlinks** pointing into the moved folder: `find ~ -maxdepth 4 -type l`, check targets.
6. **Repo docs** citing the old path: grep, fix in that repo's next PR.

Also:
- Never move a repo with uncommitted work unless it moves as is.
- Move to the Trash, never `rm`.
- Close Claude sessions open in that folder first.
- Restart Claude Desktop or the browser if an MCP path changed.

Worked example (dry-run by default, `--apply` to run): `shared/.claude/scripts/workspace-reorg.sh` in `lobomorir-ai-setup`, which automates the 2026-10-28 reorg.
