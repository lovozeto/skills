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
### Changed (prompt review, opus)
- forge-wizard rewritten after `agent-prompt-reviewer` findings: one source per rule (approval
  gate, branching), positive phrasing, per-companion fallbacks, checkable completion criteria
  per phase, a final "Done when" checklist, archiving moved to `references/archiving.md`,
  `Skill` added to `allowed-tools`, skill calls phrased "Call the Skill tool with …".
- Phase 0 reads the user's and the target repo's conventions into the Ledger.
- Phase 3b keeps invocation in sync across Claude Code and Codex (`agents/openai.yaml`).
- Phase 5c runs `claude plugin validate` on every touched plugin.
- `agent-prompt-reviewer`: absolute KB path, defined severity/verdict, file fallback for
  `writing-for-agents`, KB rules in the checklist, explicit "no findings".
- `refresh-forge-kb`: confirmation before any write; global-index pointer opt-in; scheduled
  runs stop before writing.
- SessionStart hook is silent unless a `kb/` file has expired.
### Changed
- `forge-wizard` is now **model-invoked** (Claude reaches it when you ask to build or fix a
  skill, agent, or plugin).
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
