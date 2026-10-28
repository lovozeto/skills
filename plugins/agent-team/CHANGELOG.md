# Changelog — agent-team

All notable changes to this plugin are recorded here. Format: [Keep a Changelog]; versions
follow semver (patch = fix, minor = new capability, major = breaking).

## [Unreleased]

## [0.1.0] — 2026-10-28
### Added
- `run-task` orchestrator (model-invoked) and `references/tickets.md`: one ticket from draft to
  PR. The record is the repo's GitHub issue (body plus one comment per log entry);
  `.scratch/issues/` holds only the in-flight working file, deleted once the PR is open.
- Agents, one task each: `pm`, `architect`, `reference-scout`, `brand`, `ux`, `content`, `ui`,
  `ui-mui`, `backend`, `frontend`, `web-graphics`, `qa`, `vqa`, `memory-keeper`. Generalized
  from matrimonio-ivan-eliana's team (itself from invitation-system and matrimonio-lobomorir);
  repo facts move to each repo's `.claude/knowledge/agent-team.md`.
- Hooks, active only with `.claude/agent-team.json`: `guard_ticket` (stages, verdict owners,
  ask before `ready-for-agent`), `guard_write_scope`, `guard_knowledge` (on `kb stale`, one
  mapped file at a time), and a SessionStart preflight for `gh` and `kb`.
- Hook harness: `hooks/tests/run_tests.py`.
