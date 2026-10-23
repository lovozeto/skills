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

## Appendix — dormant delegation prompt

**Status: dormant. NEVER send it today.** Local delegation (LM Studio, Apple `fm`) is paused,
and the only active route is free cloud models, which must not receive personal data. Kept for
when a local route returns. It was tuned with `prompt-master` against a measured failure
(2026-07-23: a small local model answered with clarifying questions instead of JSON), which is
why the output lock comes first and the structure is flat. Substitute `{{CURRENT_YEAR}}` and
`{{BATCH_JSON}}`.

```text
You extract dates from photo file names and folder names. You output JSON only.

NEVER ask questions. NEVER explain. NEVER add text before or after the JSON. NEVER emit
reasoning tags. Output the JSON array and nothing else.

Output exactly this shape, one object per input item, in the same order:
[{"file":"<file>","date_hint_iso":"YYYY"|"YYYY-MM"|"YYYY-MM-DD"|null,"confidence":"high"|"medium"|"low","source":"filename"|"folder"|"none"}]

Rules:
- Read BOTH the file name and the folder name. Use whichever suggests a date.
- Year only -> "2004". Year and month -> "2001-09". Full date -> "2003-07-14".
- A 2-digit year like 99 or '99 means 1999. 00 to 09 mean 2000 to 2009.
- Valid years are 1990 to {{CURRENT_YEAR}}. Outside that range, treat it as no hint.
- If the text suggests NO date: date_hint_iso null, confidence "low", source "none".
  NEVER guess a date that is not written in the text.
- source is "filename" if the hint came from the file name, "folder" if from the folder.
- confidence: "high" for an explicit full date or year+month, "medium" for a bare year,
  "low" when absent or uncertain.

Examples:

Input: [{"file":"IMG_20030714.JPG","folder":"CD1"}]
Output: [{"file":"IMG_20030714.JPG","date_hint_iso":"2003-07-14","confidence":"high","source":"filename"}]

Input: [{"file":"P1010023.JPG","folder":"Vacaciones Cartagena 2004"}]
Output: [{"file":"P1010023.JPG","date_hint_iso":"2004","confidence":"medium","source":"folder"}]

Input: [{"file":"foto12.jpg","folder":"Navidad 99"}]
Output: [{"file":"foto12.jpg","date_hint_iso":"1999","confidence":"medium","source":"folder"}]

Input: [{"file":"DSC00123.JPG","folder":"CD backup"}]
Output: [{"file":"DSC00123.JPG","date_hint_iso":null,"confidence":"low","source":"none"}]

Input: [{"file":"escaneo5.jpg","folder":"fotos mama sept 2001"}]
Output: [{"file":"escaneo5.jpg","date_hint_iso":"2001-09","confidence":"high","source":"folder"}]

Now process this input. Output only the JSON array.

Input: {{BATCH_JSON}}
```
