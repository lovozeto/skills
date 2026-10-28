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
- `/delegation:init`: sets a Mac up (installs Ollama and opencode, server LaunchAgent, models
  from the user's catalog with a pinned `num_ctx`, opencode registration, fit and code
  measurements, machine profile) or re-evaluates newer models found by the `model-scout`
  agent (sonnet) against the current ones; can remove Ollama entirely (files to the Trash)
  when the machine goes cloud-only.
- Helpers: `delegation-machine-info`, `delegation-pull-model`, `delegation-ollama-env`,
  `delegation-remove-ollama`, `sync-ollama-to-opencode`.
- `bench-model`: fit probe (100% GPU, no hidden reasoning), `--runs`, and a replace decision
  against the current model (`--current`, `--class`).
- `ask-local` refuses a prompt larger than the model's `num_ctx` instead of letting Ollama
  cut it, prints Ollama's own errors, and exits 2 on bad arguments. `ask-opencode` turns bash
  off in text mode and for cloud models.
- Replaces the standalone `delegate`, `write-for-model` and `benchmark-model` skills.
