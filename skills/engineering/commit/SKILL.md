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

## Format

Follow the user's commit conventions; their `CLAUDE.md` points to them (in this setup,
`CONVENTIONS.md` → "Commits", the only home of the format). With no conventions, use
Conventional Commits: `type: summary`, English, imperative, ≤ 50 characters.

Branch, PR and merge rules are not this skill's job: they live in the same conventions.
