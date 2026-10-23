# skill-forge KB — index

The wizard's source of truth. **Pointer, never copy** into generated artifacts. Every entry
carries a `tier`: `advisory` guides decisions; **only `proven` can back code** (someone ran
it and pasted the output). Entries were seeds until the first
`/refresh-forge-kb` (2026-10-23) checked them against live sources.

| Entry | File | Tier | Last updated |
|---|---|---|---|
| Credible sources list | `sources.md` | advisory | 2026-10-23 |
| Multi-provider model catalog | `model-catalog.md` | advisory | 2026-10-23 |
| Best practices — agents | `best-practices/agents.md` | advisory | 2026-10-23 |
| Best practices — skills | `best-practices/skills.md` | advisory | 2026-10-23 |
| Best practices — plugins | `best-practices/plugins.md` | advisory | 2026-10-23 |
| Best practices — hooks | `best-practices/hooks.md` | advisory | 2026-10-23 |
| Best practices — prompting | `best-practices/prompting.md` | advisory | 2026-10-23 |
| Best practices — UX heuristics | `best-practices/ux-heuristics.md` | advisory | 2026-10-23 |

## Expiry
Each file's frontmatter carries `last_verified` and `review_by` (volatility table in
`sources.md`). Seed files start as `last_verified: unknown` and are due for refresh.

## Maintenance
Run `/refresh-forge-kb` to refresh entries from the sources in `sources.md`. It applies three
gates (pre-flight, curation, review), records provenance + tier, and updates the
`Last updated` column here. It also updates the packaged templates in `assets/templates/`
when best practices change.
