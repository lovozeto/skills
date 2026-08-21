# skill-forge KB — index

The wizard's source of truth. **Pointer, never copy** into generated artifacts. Every entry
carries a `tier`: `advisory` guides decisions; **only `proven` can back code** (someone ran
it and pasted the output). Seed entries are `advisory` and marked *unverified* until
`/refresh-forge-kb` confirms them against live sources.

| Entry | File | Tier | Last updated |
|---|---|---|---|
| Credible sources list | `sources.md` | advisory | seed (unverified) |
| Multi-provider model catalog | `model-catalog.md` | advisory | seed (unverified) |
| Best practices — agents | `best-practices/agents.md` | advisory | seed (unverified) |
| Best practices — skills | `best-practices/skills.md` | advisory | seed (unverified) |
| Best practices — plugins | `best-practices/plugins.md` | advisory | seed (unverified) |
| Best practices — hooks | `best-practices/hooks.md` | advisory | seed (unverified) |
| Best practices — prompting | `best-practices/prompting.md` | advisory | seed (unverified) |
| Best practices — UX heuristics | `best-practices/ux-heuristics.md` | advisory | seed (unverified) |

## Maintenance
Run `/refresh-forge-kb` to refresh entries from the sources in `sources.md`. It applies three
gates (pre-flight, curation, review), records provenance + tier, and updates the
`Last updated` column here. It also updates the packaged templates in `assets/templates/`
when best practices change.
