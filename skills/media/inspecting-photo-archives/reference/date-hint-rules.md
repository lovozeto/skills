# Date hints from file and folder names

Used by SKILL.md Step 4. Claude applies these rules itself: the input is personal data (family
folder names), so it is not delegated (see the dormant appendix).

## Rules

Work in batches of ~40 candidates. For each `{"file", "folder", "reason"}` produce:

```
{"file":"<file>","date_hint_iso":"YYYY"|"YYYY-MM"|"YYYY-MM-DD"|null,"confidence":"high"|"medium"|"low","source":"filename"|"folder"|"none"}
```

- Read BOTH the file name and the folder name; use whichever states a date.
- Year only → `"2004"`. Year and month → `"2001-09"`. Full date → `"2003-07-14"`.
- A 2-digit year: `99` or `'99` → 1999; `00`–`09` → 2000–2009.
- Valid years are 1990 to the current year; outside that range there is no hint.
- If the text states no date: `date_hint_iso` null, confidence `"low"`, source `"none"`.
  NEVER guess a date that is not written in the text.
- `reason: impossible_date` means the EXIF date is noise: ignore it and read the names.
- confidence: `"high"` for a full date or year+month, `"medium"` for a bare year, `"low"` when
  absent or uncertain.

## Examples

| file | folder | → date_hint_iso | confidence | source |
|---|---|---|---|---|
| `IMG_20030714.JPG` | `CD1` | `2003-07-14` | high | filename |
| `P1010023.JPG` | `Vacaciones Cartagena 2004` | `2004` | medium | folder |
| `foto12.jpg` | `Navidad 99` | `1999` | medium | folder |
| `DSC0001.JPG` (impossible_date) | `Boda Ana 2002` | `2002` | medium | folder |
| `escaneo5.jpg` | `fotos mama sept 2001` | `2001-09` | high | folder |
| `DSC00123.JPG` | `CD backup` | null | low | none |

## QA (every batch, before using it)

1. One output per input, same order.
2. Each `date_hint_iso` is null or matches `^\d{4}(-\d{2}(-\d{2})?)?$`.
3. Each year is between 1990 and the current year.
4. `confidence` ∈ {high, medium, low}; `source` ∈ {filename, folder, none}.
5. When `date_hint_iso` is null, `source` is `none`.
6. **Spot-check 3–5 cases** against the real name: is the date really written there? This is
   the check that catches invented dates; the others only validate the shape.

A batch that fails is redone, item by item, before it enters the report.

---

A delegation prompt for small local models (tuned 2026-07-23, now dormant because local
delegation is paused and this input is personal data) is in git history, commit `0d3be5e`.
If a local route returns, rebuild it from the Rules and Examples above.
