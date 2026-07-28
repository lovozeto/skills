---
name: commit
description: Stage and commit the current changes following Conventional Commits. Manual only.
disable-model-invocation: true
allowed-tools: Bash(git add *), Bash(git commit *), Bash(git status *), Bash(git diff *)
argument-hint: "[optional: files or scope]"
---

# commit — apply the Conventional Commits standard

Effective skill — you trigger it, not Claude automatically.

## Steps

1. Run `git status` + `git diff` to see what changed. Group into **one commit = one coherent change**; if there are unrelated changes, make multiple commits.
2. Draft the message (format below).
3. `git add` the files for this commit and `git commit -m "<message>"`.
4. Confirm what was committed and with what message.

## Format — Conventional Commits

- **`type: summary`**
- **`type`** ∈ `feat` · `fix` · `docs` · `refactor` · `chore` · `test`
- **Summary:** English, imperative mood, **≤ 50 characters**, no trailing period.
  Example: `fix: guard window access behind Platform.OS`
- **Body (optional):** only if it adds something — what and why, in English, ~72-char lines.

## Hard rules

- Ask before starting a new change whether it goes on a new branch or the existing one.
- Commit messages go in **English**.
- Never merge directly to `main` when working with branches — use a PR on GitHub.
