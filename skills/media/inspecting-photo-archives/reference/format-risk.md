# Format risk — operative rule for this skill

Used by SKILL.md Step 3. Format knowledge lives in the user's KB, not here: read the
`media-formats` base through the KB index the user's `CLAUDE.md` names (files
`preservation-doctrine.md`, `video-codecs.md`, `image-formats.md`). If no KB is available, say
so and classify from `ffprobe` output only, marking each result unverified.

## The container does not decide compatibility; the codec inside does

An `.avi` can hold MJPEG (opens fine) or Indeo (does not open by double-click). Classify only
from the real codec:

```bash
ffprobe -v error -select_streams v:0 \
  -show_entries stream=codec_name,codec_long_name,width,height \
  -show_entries format=format_name,duration -of json "<file>"
```

This judgement stays with Claude: it needs world knowledge. Measured 2026-07-23, a small local
model got 2 of 4 wrong and invented that "Apple deprecated QuickTime in 2017".

## Two different problems — name which one

- **"Does not open in the system player"** (QuickTime Player, Photos, Preview) → an
  inconvenience. True of almost every legacy codec; `ffmpeg` decodes them (codec list in
  `video-codecs.md`).
- **"Cannot be decoded"** → real loss. Rare today.

Mixing them up turns an inconvenience into a false emergency. **For a family archive the real
urgency is the physical CD degrading, not the codec.**

## How to report (the user decides)

For each candidate:
1. **What it is** — container + real codec from `ffprobe`, not the extension.
2. **Which of the two problems** it has.
3. **What converting would gain and lose.**
4. **A recommendation, not executed** — this skill is read-only.

NEVER recommend re-compressing a JPEG: it is loss without gain. Lossless optimization exists
(`jpegtran` works on DCT coefficients; `cjpeg` re-encodes and degrades); details in
`image-formats.md`.
