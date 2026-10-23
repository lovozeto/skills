# kb-merge (subagent instructions)

You merge the `.raw/` intermediates for one base into the final KB file. Mechanical work.

## What you do

- Deduplicate identical rules, preserving **all** attributions.
- Group by topic.
- Compose the final frontmatter: `id`, `category`, `sources` (all, with publisher and
  `last_verified`), `discovered_via`, `created`, `refresh_after_days`, `tier: advisory`, and
  file-level `last_verified` + `review_by` (`review_by` = `last_verified` + `refresh_after_days`).
  `preflight` reads `review_by` to flag expired files at session start.
- Every rule keeps its inline attribution.

## What you do NOT do

- Do not decide between conflicting sources.
- Do not rewrite rules to make them sound coherent with each other.
- Do not add anything that is not in a `.raw/` file.

## Conflicts

If two sources genuinely contradict each other, write both with attribution and mark:

```
⚠️ unresolved conflict
- {Publisher A} says X [url]
- {Publisher B} says Y [url]
```

Do not choose. The review gate resolves it, or `/arbitrate` is invoked.

## After merging

- **Do NOT delete `.raw/`**. The intermediates stay and are committed as an audit trail —
  they are the only way to trace back which source produced each rule if the final file
  is later edited.
- Update `INDEX.md` with the new file's row (one line).
- Report: files created, total rules, unresolved conflicts.
