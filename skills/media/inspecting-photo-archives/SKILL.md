---
name: inspecting-photo-archives
description: Inspect folders of old photos and videos (copied from CDs, DVDs, or external drives) and produce a read-only metadata report for importing them with judgement — capture date, camera, timezone, dates lost in the copy, at-risk formats. Use when the user mentions old or scanned photos, photos from CDs, EXIF or metadata, photos with no date or out of order ("fotos viejas", "fotos sin fecha"), auditing a photo folder before importing it, or asks which camera or date a photo has. Not for converting, renaming, or moving files.
---

# Inspect old photo archives

Produces a report for importing old photos **with judgement**: what is there, what metadata
it has, what was lost when it was copied off the CD, and which formats deserve a look.

> **Hard rule: this skill is READ-ONLY.** NEVER modify, move, rename, or convert a file in
> the original archive: originals are irreplaceable. If the user asks to convert, say that
> conversion is outside this skill and comes only after this report is approved.

Copy this checklist and tick it as you go:

```
- [ ] Step 0: dependency preflight
- [ ] Step 1: scan metadata (read-only)
- [ ] Step 2: summarize
- [ ] Step 3: judge at-risk formats (ffprobe)
- [ ] Step 4: infer dates from names
- [ ] Step 5: ask the user for estimated dates
- [ ] Step 6: write the report
```

**Output folder.** `OUT` = `$HOME/Documents/photo-archive-reports/<scope>/<YYYY-MM-DD>`, where
`<scope>` is the folder or CD name. Always expand it to an absolute path; `~` inside quotes is
not expanded. Dated folders are a deliberate exception to the house "no dated folders" rule:
these reports live outside any repo, so the dates are their only history.

## Step 0 — Dependency preflight

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/check_deps.sh"
```

It exits 3 with an `install_command` when something is missing. Then:

1. Tell the user **what** is missing and **what it is for** (`exiftool` reads photo and video
   metadata; `ffmpeg`/`ffprobe` identify the real codec inside a video).
2. **Ask for explicit confirmation before installing** — installing changes their system.
3. With the OK: `brew install <what is missing>`.

Without the OK, the two degrade differently:

| Missing | Consequence |
|---|---|
| `exiftool` | **Blocking.** `scan_archive.sh` exits 2; there is no scan. Say so and stop. |
| `ffprobe` | **Degradable.** Everything runs except Step 3; videos stay **unclassified**. Continue and list them as unverified in the report. |

Done when `check_deps.sh` exits 0, or `exiftool` is present and the missing `ffprobe` is recorded.

## Step 1 — Scan (read-only)

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/scan_archive.sh" "<archive folder>" "$OUT/raw-scan.json"
```

Done when it exits 0 and `raw-scan.json` exists. Exit 2 = stop and report the error.

## Step 2 — Summarize

```bash
PHOTO_ARCHIVE_HOME_OFFSET="-05:00" python3 "${CLAUDE_SKILL_DIR}/scripts/summarize_scan.py" \
  "$OUT/raw-scan.json" "$OUT/summary.json"
```

Set `PHOTO_ARCHIVE_HOME_OFFSET` to the user's home UTC offset (default `-05:00`, Colombia).
Read only `summary.json`; `raw-scan.json` can be megabytes, so query single records from it
with `jq`:

```bash
jq '.[] | select(.FileName=="IMG_0042.JPG")' "$OUT/raw-scan.json"
```

Per folder, the summary has the count, year range, cameras, formats, and these flags with
examples:

| Flag | Meaning |
|---|---|
| `no_capture_date` | No `DateTimeOriginal` or `CreateDate` — when it was taken is unknown |
| `impossible_date` | Year < 1990 or in the future — a dead camera battery reset the clock; treated as no date |
| `placeholder_time` | Real date, time `00:00:00` — the camera stored the day, not the clock. **The day is usable, the time is not** |
| `identical_timestamps` | The whole folder shares one timestamp — the order inside it is unknown |
| `filedate_mismatch` | EXIF date and file date differ by > 1 year — **the date was lost copying off the CD** |
| `tz_missing` | No timezone offset (normal for old cameras) |
| `tz_not_home` | An offset other than the home one — a trip, or a camera never reconfigured |
| `legacy_container` | `.avi`, `.wmv`, `.mpg`, `.bmp`… — a candidate to look at, **not** to convert yet |

Done when `summary.json` is read and every flag count is noted per folder. If
`date_hint_candidates_total` is larger than the list, say so and pull the rest from
`raw-scan.json` with `jq`.

## Step 3 — Judge at-risk formats

Read `reference/format-risk.md` before classifying anything. Then run `ffprobe` (exact command
there) on every entry in `videos_to_probe`, and classify each high / medium / low with the
concrete reason. Done when every entry has a classification or is marked unverified.

## Step 4 — Infer dates from names

Candidates: every entry in `date_hint_candidates` (both `no_capture_date` and
`impossible_date`). File and folder names often carry the date (`Cartagena 2004`,
`IMG_20030714`, `Navidad 99`).

Do this yourself, in this conversation. Delegate nothing: names in a family archive are
personal data, and the only active delegation route is free cloud models. Apply the rules,
examples, and QA checks in `reference/date-hint-rules.md` to each batch.

Every inferred date enters the report marked **inferred**, never as hard data. Done when every
candidate has a hint or `null`, and the QA checks passed.

## Step 5 — Ask for estimated dates

Where there is no trustworthy EXIF date (missing or `impossible_date`) and no usable hint, ask
the user **per folder** (not per file) for an estimated date, showing the context you already
have: folder name, photo count, cameras found, the year range of neighbouring folders. Offer
"I don't know" as a valid answer — a folder without a date is a legitimate result. Done when
every such folder has an answer.

## Step 6 — Write the report

Write in `$OUT/`:

- **`report.json`** — structured, English keys, for another step or skill to consume.
- **`report.md`** — readable, in the user's language, for deciding. Per folder: what is there,
  date range, cameras, what is wrong, formats to look at, and the **suggested action** (not
  executed).

Close with one sentence: how many files, how many without a reliable date, how many at-risk
formats, and the concrete next step. Done when both files are written and the sentence is said.

Scope: inspect and report only. Verification history: `evals/`.
