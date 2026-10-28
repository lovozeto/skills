# agent-team

Run a repo's work as tracked tickets through a team of single-task agents. You describe a
change; `run-task` has `pm` draft the ticket, opens it as a GitHub issue on the repo's board,
waits for your approval, then dispatches the agents the ticket lists, one at a time, through
plan → brand → experience → interface → build → quality gate → close. Every push, PR and
merge waits for you.

The plugin is installed once and acts only in repos that opt in with `.claude/agent-team.json`.

## What ships

| Piece | What it does |
|---|---|
| `run-task` (skill, model-invoked) | The orchestrator: ticket lifecycle, briefs, gates, log. Format and stages: `skills/run-task/references/tickets.md` |
| `pm` | Drafts one ticket under `.scratch/issues/` |
| `architect` | Technical plan: data, API, files and owners, order, risks |
| `reference-scout`, `brand` | Visual references for owner approval; brand guidelines from the owners' inputs |
| `ux`, `content` | Flow review; source-language copy and review of translations |
| `ui`, `ui-mui` | Library-agnostic UI decisions; their MUI recipe |
| `backend`, `frontend`, `web-graphics` | The build, each inside its write scope |
| `qa`, `vqa` | Quality gate and visual check; only they write their verdicts |
| `memory-keeper` | Closes the ticket into `QUICK-STATE.md` and the decisions file |
| hooks | `guard_ticket`, `guard_write_scope`, `guard_knowledge` (on `kb stale`), `preflight`: see [`hooks/README.md`](hooks/README.md) |

Models: `run-task` and `pm` on `opus`; `memory-keeper` on `haiku`; the rest on `sonnet`.

## Requirements

`python3`, `gh` (authenticated, the repo has a board: `setup-tracking <owner/repo>`), and the
`kb` CLI with the global KB for knowledge checks. The SessionStart hook names what is missing.
Optional: the MUI MCP registered under the server key `mui-mcp` (`ui-mui`, `frontend` in MUI repos), the built-in browser (`vqa`,
`reference-scout`), the `delegation` plugin (translation drafts) and the
`track-work` skill (board columns).

## Set a repo up

1. **`.claude/agent-team.json`**: each agent's write scope and knowledge files (format in
   [`hooks/README.md`](hooks/README.md#the-repo-config)). Map knowledge one file at a time.
2. **`.claude/knowledge/agent-team.md`**: the facts the generic agents need about this repo,
   one section per agent that needs them. Agents read `## Project` plus their own section; a
   missing section means "nothing specific".

   | Section | Holds |
   |---|---|
   | `## Project` | stack, the plan and spec files to read, audiences and languages, project-local agents (name, stage, extra brief) |
   | `## pm` | when each project-local agent belongs in a ticket |
   | `## architect` | schema and migration conventions, data access, vendored docs |
   | `## backend` | migration and verification commands, server conventions |
   | `## frontend` | UI library and its docs tool, i18n files and languages per surface |
   | `## web-graphics` | where the graphics components live |
   | `## ux` | audiences, devices, the flows and where they live |
   | `## content` | source language and voice, translated languages, copy files and placeholders |
   | `## ui` / `## ui-mui` | current theme files (the baseline while the guidelines are `PENDING`), library version |
   | `## qa` | lint/types/build/test commands (with CI placeholders), project rules |
   | `## vqa` | the dev server's name in `.claude/launch.json` |
   | `## memory-keeper` | state file (default `QUICK-STATE.md`), decisions file and its table shape, any further record to update |

3. Add `/.scratch/issues/` to `.gitignore`. Project-local agents stay in `.claude/agents/`.

Brand material, when the repo has it, lives in `.claude/knowledge/brand/` (`inputs/`,
`reference-board.md`, `guidelines.md`); the write-scope hook special-cases the board.

## Tests

```bash
python3 plugins/agent-team/hooks/tests/run_tests.py
```
