#!/usr/bin/env python3
"""Aggregate a raw exiftool scan into a compact, context-cheap summary.

Reads the JSON array produced by scan_archive.sh and writes a summary JSON that
answers, per folder: how many files, what date range, which cameras, and what is
wrong (missing dates, impossible dates, unknown/foreign timezone, legacy
containers, dates lost in transfer).

The raw scan of a full CD can be megabytes. This summary is what gets read into
the conversation; individual records are looked up on demand.

Usage: summarize_scan.py <raw_scan.json> <summary.json>
Exit codes: 0 = ok · 2 = bad usage or unreadable input.
"""

import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime

# --- Tunable constants (documented so they are not voodoo values) -----------

# Consumer digital cameras with EXIF clocks are a 1990s-onward thing. A capture
# date before this almost always means a dead camera battery reset the clock,
# not a genuinely older photograph.
MIN_PLAUSIBLE_YEAR = 1990

# Colombia (America/Bogota) is UTC-05:00 year-round — no daylight saving.
COLOMBIA_UTC_OFFSET = "-05:00"

# A capture date and a filesystem date more than this many years apart means the
# original date did not survive the copy off the CD.
FILEDATE_MISMATCH_YEARS = 1

# Cap examples per flag per folder so the summary stays small enough to read.
MAX_EXAMPLES = 8

# Containers whose age alone warrants a look. For video the CONTAINER does not
# decide compatibility — the codec inside does — so these are flagged for
# inspection, never auto-classified. See reference/format-risk.md.
LEGACY_CONTAINERS = {"avi", "wmv", "mpg", "mpeg", "3gp", "bmp"}

EXIF_DATE_RE = re.compile(r"^(\d{4}):(\d{2}):(\d{2})")

# Cameras that stored a date but no clock write "00:00:00". Seen in the wild on a
# Skanhex SX-130F (2001): the day is real, the time is a placeholder. Treating it
# as a real timestamp would sort a whole folder to midnight.
PLACEHOLDER_TIME_RE = re.compile(r"\s00:00:00\s*$")


def parse_year(value):
    """Return the year from an exiftool date string, or None."""
    if not value or not isinstance(value, str):
        return None
    m = EXIF_DATE_RE.match(value.strip())
    if not m:
        return None
    try:
        return int(m.group(1))
    except ValueError:
        return None


def capture_date(rec):
    """Best available capture timestamp: the original beats a later re-encode."""
    for key in ("DateTimeOriginal", "CreateDate"):
        val = rec.get(key)
        if val and parse_year(val):
            return val
    return None


def tz_offset(rec):
    """Timezone the PHOTO was taken in, or None if the file does not say.

    Only EXIF offset tags count. The offset glued onto FileModifyDate is the
    timezone of the machine that copied the file, not of the camera that shot
    it — trusting it would make every photo on a Colombian Mac look correctly
    stamped -05:00 and silently defeat the whole timezone check.
    """
    for key in ("OffsetTimeOriginal", "OffsetTime"):
        val = rec.get(key)
        if val and isinstance(val, str) and val.strip():
            return val.strip()
    return None


def main():
    if len(sys.argv) != 3:
        print("ERROR: usage: summarize_scan.py <raw_scan.json> <summary.json>",
              file=sys.stderr)
        return 2

    raw_path, out_path = sys.argv[1], sys.argv[2]
    try:
        with open(raw_path, "r", encoding="utf-8", errors="replace") as fh:
            records = json.load(fh)
    except (OSError, ValueError) as exc:
        print("ERROR: cannot read scan file %s: %s" % (raw_path, exc),
              file=sys.stderr)
        return 2

    if not isinstance(records, list):
        print("ERROR: expected a JSON array from exiftool", file=sys.stderr)
        return 2

    this_year = datetime.now().year
    folders = defaultdict(lambda: {
        "file_count": 0,
        "cameras": set(),
        "formats": defaultdict(int),
        "capture_years": [],
        "capture_stamps": [],
        "flags": defaultdict(int),
        "examples": defaultdict(list),
    })
    date_hint_candidates = []
    videos_to_probe = []

    for rec in records:
        source = rec.get("SourceFile") or rec.get("FileName") or "?"
        folder = rec.get("Directory") or os.path.dirname(source) or "."
        name = rec.get("FileName") or os.path.basename(source)
        ext = (os.path.splitext(name)[1].lstrip(".") or "").lower()
        mime = str(rec.get("MIMEType", ""))

        f = folders[folder]
        f["file_count"] += 1
        f["formats"][ext or "?"] += 1

        make = str(rec.get("Make", "")).strip()
        model = str(rec.get("Model", "")).strip()
        camera = (make + " " + model).strip()
        if camera:
            f["cameras"].add(camera)

        def flag(name_, example=None):
            f["flags"][name_] += 1
            if example and len(f["examples"][name_]) < MAX_EXAMPLES:
                f["examples"][name_].append(example)

        cap = capture_date(rec)
        cap_year = parse_year(cap)

        if not cap:
            flag("no_capture_date", name)
            # Folder + filename often still encode a date. Extracting that from
            # messy text is the one genuinely delegable subtask in this skill.
            date_hint_candidates.append({
                "file": name,
                "folder": os.path.basename(folder),
            })
        else:
            f["capture_years"].append(cap_year)
            f["capture_stamps"].append(cap)
            if cap_year < MIN_PLAUSIBLE_YEAR or cap_year > this_year:
                flag("impossible_date", "%s (%s)" % (name, cap))

            # The day is usable, the time is not. Matters because sorting by
            # timestamp would collapse the whole folder onto midnight.
            if PLACEHOLDER_TIME_RE.search(cap):
                flag("placeholder_time", "%s (%s)" % (name, cap))

            file_year = parse_year(rec.get("FileModifyDate"))
            if file_year and abs(file_year - cap_year) > FILEDATE_MISMATCH_YEARS:
                flag("filedate_mismatch",
                     "%s (exif %s / file %s)" % (name, cap_year, file_year))

        offset = tz_offset(rec)
        if offset is None:
            flag("tz_missing", name)
        elif offset != COLOMBIA_UTC_OFFSET:
            flag("tz_not_bogota", "%s (%s)" % (name, offset))

        if ext in LEGACY_CONTAINERS:
            flag("legacy_container", "%s (.%s)" % (name, ext))

        if mime.startswith("video/"):
            codec = rec.get("VideoCodec") or rec.get("CompressorID") or None
            if len(videos_to_probe) < 200:
                videos_to_probe.append({
                    "file": source,
                    "container": ext,
                    "codec_from_exif": codec,
                })

    summary = {
        "scanned_files": len(records),
        "folder_count": len(folders),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "conventions": {
            "colombia_utc_offset": COLOMBIA_UTC_OFFSET,
            "min_plausible_year": MIN_PLAUSIBLE_YEAR,
        },
        "folders": [],
        # Handed to a local model for date-hint extraction (see SKILL.md).
        "date_hint_candidates": date_hint_candidates[:500],
        # Containers alone do not decide video compatibility; Claude probes these.
        "videos_to_probe": videos_to_probe,
    }

    for folder, data in sorted(folders.items()):
        years = sorted(y for y in data["capture_years"] if y)
        stamps = data["capture_stamps"]

        # Every file sharing one timestamp means the camera stamped a date but
        # never a real clock reading — the order within the folder is unknown.
        if len(stamps) > 1 and len(set(stamps)) == 1:
            data["flags"]["identical_timestamps"] = len(stamps)
            data["examples"]["identical_timestamps"] = [
                "todas las %d comparten %s" % (len(stamps), stamps[0])
            ]

        summary["folders"].append({
            "folder": folder,
            "file_count": data["file_count"],
            "cameras": sorted(data["cameras"]),
            "formats": dict(sorted(data["formats"].items())),
            "capture_year_range": [years[0], years[-1]] if years else None,
            "flags": dict(sorted(data["flags"].items())),
            "examples": {k: v for k, v in sorted(data["examples"].items())},
        })

    try:
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(summary, fh, indent=2, ensure_ascii=False)
    except OSError as exc:
        print("ERROR: cannot write summary %s: %s" % (out_path, exc),
              file=sys.stderr)
        return 2

    print("summarized %d file(s) across %d folder(s) -> %s"
          % (len(records), len(folders), out_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
