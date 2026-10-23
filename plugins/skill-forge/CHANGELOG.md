# Changelog — skill-forge

All notable changes to this plugin are recorded here. Format: [Keep a Changelog]; versions
follow semver (patch = fix, minor = new capability, major = breaking).

## [Unreleased]

## [0.3.0] — 2026-10-22
### Added
- **Companion skills from `mattpocock-skills`** (soft dependency, built-in fallback):
  `grilling` drives the Ledger interview, `domain-modeling` the glossary/ADRs,
  `codebase-design` where agents are cut, `writing-for-agents` how every file is written,
  `wizard` the human-only setup steps, `tdd` shipped scripts, `code-review` the final
  Standards + Spec review. `wayfinder` / `to-spec` / `to-tickets` are recommended for work
  bigger than one session (Phase 0.5).
- **Phase 3b — invocation choice + always-loaded budget**: every generated skill justifies
  model- vs user-invoked; blanket "manual only" is treated as a hole.
- **Phase 5b — `agent-prompt-reviewer`** (opus): reviews drafted files against the KB and
  `writing-for-agents`; every finding cites rule + source; flags an expired KB.
- **KB expiry**: every KB file carries `last_verified` + `review_by` (volatility table in
  `kb/sources.md`); generated KBs get the same. Matt's `writing-for-agents` added as a source.
### Changed
- `forge-wizard` is now **model-invoked** (Claude reaches it when you ask to build or fix a
  skill, agent, or plugin).
- SessionStart hook trimmed to one pointer line (the rules live in the skill and `kb/`).
- `refresh-forge-kb` sets `review_by` on every refreshed file and runs when a file expires.

## [0.2.0] — 2026-08-21
### Changed
- Model catalog is now **Claude-first, cloud only**: Claude tiers are the base, with
  ChatGPT / OpenCode Zen / Kimi equivalents for coherent cross-provider instructions.
- Removed all **local-model** references from the catalog, `model-availability.md`, and the
  wizard's Phase 3 (local delegation stays in `offload-to-local`, separate).
### Added
- Hardened the **HTML approval view** into a non-skippable gate, ordered before
  `ExitPlanMode` / any build step.
- **Branch-per-work + versioning** mandate (Phase 5 branch, Phase 6 version & deliver);
  merge to `main` only when the artifact is complete. Added `CHANGELOG.md.tmpl`.
- Author set to `lovozeto`.

## [0.1.0] — 2026-08-21
### Added
- Initial skill-forge plugin: `forge-wizard` (zero-hole Definition Ledger, complexity-based
  type decision, orchestrator + single-task subagents, mandatory model, guardrail hooks,
  dependency handling), `refresh-forge-kb` maintainer, bundled KB, packaged templates, and
  guardrail hooks. Repo is also a plugin marketplace. `workshop-skill` moved to `_archive/`.
