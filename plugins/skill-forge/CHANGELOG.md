# Changelog — skill-forge

All notable changes to this plugin are recorded here. Format: [Keep a Changelog]; versions
follow semver (patch = fix, minor = new capability, major = breaking).

## [Unreleased]

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
