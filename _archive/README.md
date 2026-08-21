# _archive

Superseded artifacts kept for reference and history. Nothing here is active — skills and
plugins in this folder are **not** meant to trigger or be installed.

## Convention

When a skill/agent/plugin is replaced, it is **moved here** (never deleted), mirroring its
original path so provenance is obvious. Example:

```
skills/engineering/workshop-skill/   →   _archive/skills/engineering/workshop-skill/
```

Use `git mv` so history is preserved. Add a short note at the top of the moved artifact
stating what replaced it and when.

The `skill-forge` plugin is aware of this convention: when its wizard replaces an existing
artifact, it moves the old one here instead of deleting it.

## Contents

| Archived | Replaced by | When |
|---|---|---|
| `skills/engineering/workshop-skill/` | `plugins/skill-forge/` (`/forge-wizard`) | 2026-08-21 |
