---
name: kb-curate
description: Extract atomic, sourced rules from a documentation page, article, standard or URL into the team's knowledge base in the format the `kb` CLI indexes. Use when the user shares a source and wants its principles captured, says "agrega esto a la KB", "curar", "extrae las reglas", or asks to correct or extend a KB file.
model: sonnet
---

# kb-curate — extraction into the knowledge base

Turns one source at a time into atomic rules inside `$KB_ROOT` (default `~/dev/claude-kb`).
**Model: Sonnet or better.** Rules are quoted facts; a light model paraphrases them wrong.

## One source per pass

Read one publisher at a time and write only what that publisher says. Two philosophies in
the same context get averaged into a rule nobody wrote. If the user gives several sources,
do them one after another, each as its own pass.

## The format `kb` indexes (follow it exactly)

Each base is a folder (`ux/`, `ui/`, `accessibility/`, `content/`, `brand/`, `swift/`, …) and
each file a topic. A file:

```markdown
---
summary: Forms: field design, validation, error messages, inline errors
tier: advisory            # advisory = from docs; proven = measured on this machine
last_verified: 2026-11-10
review_by: 2027-05-10     # kb stale flags the file after this date
sources:
  - publisher: GOV.UK Design System
    url: https://design-system.service.gov.uk/patterns/validation/
---

# Forms

## Validation
<!-- tags: topic=forms,error-handling; platform=web; concern=a11y; keywords=error summary, inline error -->
- Show the error next to the field and repeat it in a summary at the top of the page. [GOV.UK: https://design-system.service.gov.uk/patterns/validation/]
- Validate on submit, not while the user is still typing. [GOV.UK: https://design-system.service.gov.uk/patterns/validation/]
```

Rules of the format:

- A rule is one `- ` bullet, one or two sentences (~50 tokens), actionable, with its source
  in a trailing `[Publisher: url]`. No prefix, no ref inside the bullet.
- `##` sections carry a `<!-- tags: … -->` line. `topic`, `platform` and `concern` values
  must exist in `TAXONOMY.md`; `keywords` is free text. A `###` inherits its parent's tags.
- Keep the raw capture (what you read, lightly cleaned) in `<base>/.raw/<publisher>.md` as the
  audit trail. `.raw/` is indexed only with `--raw`.
- Register the publisher once in `sources.yml` if it is new.
- Our own decisions go in `CONVENTIONS.md` (`kind: decisions`), dated instead of sourced.

## Procedure

1. Decide the base and file: `kb search "<topic>"` to see where similar rules live. Extend an
   existing file before creating one.
2. Read the source once, in an isolated pass if it is long (a subagent that returns only the
   rules keeps 50k tokens of page out of this context).
3. Write or update the file: frontmatter (`summary`, `tier`, dates, `sources`), tagged
   sections, sourced bullets. Save the raw capture.
4. When a new rule contradicts an existing one from another publisher, keep both, and set
   `status: ambiguous` in the frontmatter so `kb stale` surfaces the file for the owner.
5. Regenerate the router and lint: `kb router --write && kb lint`. Fix every error; report
   the warnings that remain.
6. Tell the user in one line: file, sections touched, number of rules, lint result.
