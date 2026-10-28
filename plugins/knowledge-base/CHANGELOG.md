# Changelog — knowledge-base

All notable changes to this plugin are recorded here. Format: [Keep a Changelog]; versions
follow semver (patch = fix, minor = new capability, major = breaking).

## [Unreleased]

## [0.1.0] — 2026-10-28
### Added
- Skills `ask-knowledge-base` and `update-knowledge-base` (model-invoked) and `kb-pipeline`
  (user-invoked: `/knowledge-base:kb-pipeline`, orchestrator on `opus`), moved here from
  `skills/engineering/` with their history.
- Agents `kb-scout` (haiku, read-only), `kb-extractor` (sonnet, writes only its `.raw/`
  file), `kb-merge` and `kb-freshness` (sonnet, propose-only). They were instruction files
  under `kb-pipeline/subagents/`; each now pins its model and a restrictive tool list.
- Hooks: SessionStart sensor for the `kb` CLI; PreToolUse gate that asks before any write
  inside the KB root outside `.raw/`.
- Tests for both hooks (`tests/run.sh`).
### Changed
- All three skills read the KB with `kb search` / `kb get` / `kb stale` / `kb lint` first,
  falling back to `INDEX.md` when `kb` is missing or fails; a failing `kb` is reported as "KB
  could not be read", never as "not covered".
- `kb-pipeline` writes the merged file and `INDEX.md` row itself, only after the review
  gate; `--refresh` runs one freshness agent per expired file and gates before any write.
  Conflicts are resolved by the user at the review gate (no longer sent to `/arbitrate`).
- `kb-merge` adds TAXONOMY tags to every section; `update-knowledge-base` follows the real
  KB format (bullets with `[Publisher: URL]`, per-source `last_verified`, `SUPERSEDED` prefix)
  and runs `kb lint` after writing.
- No skill pre-approves `Write`; only `Bash(kb *)` is pre-approved for the CLI.
