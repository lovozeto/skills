#!/usr/bin/env bash
# Read-only metadata scan of a photo/video archive.
#
# Walks <directory> recursively and writes one JSON array of per-file metadata
# records to <output_file>. Input files are only ever READ — exiftool is invoked
# without any write/modify tag, so the archive cannot be altered by this script.
#
# Usage: scan_archive.sh <directory> <output_file>
#
# Exit codes: 0 = ok · 2 = bad usage or missing dependency.

set -uo pipefail

DIR="${1:-}"
OUT="${2:-}"

if [ -z "$DIR" ] || [ -z "$OUT" ]; then
  echo "ERROR: usage: scan_archive.sh <directory> <output_file>" >&2
  exit 2
fi
if [ ! -d "$DIR" ]; then
  echo "ERROR: not a directory: $DIR" >&2
  exit 2
fi
if ! command -v exiftool >/dev/null 2>&1; then
  echo "ERROR: exiftool not found. Run check_deps.sh first." >&2
  exit 2
fi

mkdir -p "$(dirname "$OUT")"

# Deliberately small tag set. A full exiftool dump is enormous and most tags are
# irrelevant for deciding how to import a photo. These answer exactly four
# questions: when was it taken, what took it, what timezone, what format is it.
TAGS=(
  -FileName -Directory -FileSize -FileType -MIMEType
  -DateTimeOriginal -CreateDate -ModifyDate
  -OffsetTime -OffsetTimeOriginal
  -Make -Model
  -GPSLatitude -GPSLongitude
  -FileModifyDate -FileCreateDate
  -ImageWidth -ImageHeight
  -Duration -VideoCodec -CompressorID -EncodingProcess
)

# Whitelist of media extensions. Anything else in the archive (thumbs.db,
# autorun.inf, readme.txt from the original CD) is intentionally ignored.
EXTS=(
  -ext jpg -ext jpeg -ext png -ext gif -ext bmp -ext tif -ext tiff
  -ext heic -ext webp -ext cr2 -ext nef -ext dng
  -ext avi -ext mov -ext mp4 -ext m4v -ext mpg -ext mpeg -ext wmv -ext 3gp -ext mkv
)

exiftool -j -q -r "${EXTS[@]}" "${TAGS[@]}" "$DIR" > "$OUT"
status=$?

# exiftool exits 1 when SOME files produced warnings (common with old/corrupt
# files from CDs) but still writes valid JSON for the rest. That is not fatal
# here — a partial scan is exactly what we want to report on.
if [ $status -ne 0 ] && [ $status -ne 1 ]; then
  echo "ERROR: exiftool failed with status $status" >&2
  exit $status
fi

if [ ! -s "$OUT" ]; then
  echo "ERROR: no media files matched under: $DIR" >&2
  exit 2
fi

count=$(grep -c '"SourceFile"' "$OUT" 2>/dev/null || echo 0)
echo "scanned $count media file(s) -> $OUT"
exit 0
