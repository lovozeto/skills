# kb-freshness (subagent instructions)

You keep the KB current. **Run on demand, never during active work sessions.**

## When to invoke

- `preflight` lists the file as expired (its `review_by` has passed). This is the main trigger.
- Quarterly review.
- A publisher released a major version.
- A KB query returned an answer that felt stale.

## Step 1 — Expiry check

For each source of each KB file: `age = today - last_verified`.

If `age > refresh_after_days` (thresholds from `sources.yml` per base):
- Fetch the URL.
- **No changes found** → update `last_verified` to today only.
- **Content changed** → update the rule text, update `last_verified`, add a short note on what changed.
- **Source dead or moved** → write `⚠️ Source at {url} unreachable, requires manual verification`. Never silently keep a source you could not verify.

Thresholds come from `sources.yml`, per base. Do not invent them.

After any refresh of a file (changed or not), set its file-level `last_verified` to today and
`review_by` to today + `refresh_after_days`. Never move `review_by` forward without having
checked the sources.

## Step 2 — Portal rescan

For each `discovered_via` entry in the KB files: look for new leaf pages that pass the
`scope_filter` and are not yet captured.

## Step 3 — Propose before touching (MANDATORY GATE)

Present: what expired, what changed, what new pages are available.
**STOP.** Do not write anything without approval.

## Step 4 — Report

Files touched · rules updated · dead sources · new pages pending extraction.
