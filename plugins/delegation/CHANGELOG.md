# Changelog — delegation

All notable changes to this plugin are recorded here. Format: [Keep a Changelog]; versions
follow semver (patch = fix, minor = new capability, major = breaking).

## [Unreleased]

## [0.1.0] — 2026-10-28
### Added
- `ask-local`: one text task through Ollama's API. Model from `--model`, `$ASK_LOCAL_MODEL`,
  or the smallest installed model.
- `ask-opencode`: one task through an isolated opencode `lean` agent. Allows only
  `opencode/*-free`, Google Flash/Flash-Lite and `ollama/*`; scans prompt and `--dir` for
  data before any cloud call (exit 3); never guesses a model.
- `bench-model` + `bench/`: 12 agentic code tasks with compile-and-run checkers, 3 text
  tasks, and a comparison against earlier results; selftests for every checker.
- Skills `delegate` (routing), `write-for-model` (prompts via `prompt-master`) and
  `benchmark-model` (user-invoked).
- Hooks: SessionStart dependency sensor; PreToolUse guard on `ask-opencode` models and
  `--unsafe`.
- Replaces the standalone `delegate`, `write-for-model` and `benchmark-model` skills.
