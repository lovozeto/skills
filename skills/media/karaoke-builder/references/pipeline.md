# Pipeline — the full flow

```
                       ┌─────────────────┐
                       │  Unified list   │  build_unified.py (cross vs library, no repeats)
                       └────────┬────────┘
                                ▼
                     ¿on ultrastar-es.org?   site_match.py (exact artist+title, avoid again/remix/live)
                    ┌───────────┴───────────┐
                 yes│ (torrent)             │no → AI
                    ▼                        ▼
        Baja .torrent → bridge → watched    ia_gen.py
        (torrent_fetch.js + torrent_bridge) │  1) yt-dlp VIDEO+audio (1 pass, prefer official/(latino))
                    │                        │  2) demucs → [Vocals]/[Instrumental] stems
              ¿stalled?  qbt_watch.py        │  3) add_cover.py (iTunes)
             yes│ cancel → AI ──────────────▶│  4) align_lyrics.py (verified lyrics + forced alignment)
              no▼                            │       └ no web lyrics → Whisper fallback (flagged)
        Descarga completa                    │  5) duet? → single voice (diarization out of scope)
                    │                        ▼
                    └──────────┬─────────────┘
                               ▼
                 organize.py  (UTF-8 no BOM, dedupe by quality, canonical name → library)
                               ▼
                 validate.py --all   (ONE bar: tags, media, GAP, notes, breaks, monotonic beats)
                    ┌──────────┴──────────┐
                pass▼                     ▼fail
              Library (NAS)          revisar.txt  (manual review; NEVER a downgraded version)
```

## Why forced alignment beats transcribe-then-correct

Whisper transcription *guesses* words and drifts on damaged audio; correcting after the fact fights the drift. `align_lyrics.py` instead feeds whisperX the **known, verified lyrics** and only computes *when* each word is sung. Words are correct by construction. A **coverage gate** (fraction of lyric words that aligned, exact-match ratio, short-line ratio) rejects wrong-song / wrong-language matches → the song flags rather than accepting garbage. This is the single most important design choice.

## Lyrics sourcing (`fetch_lyrics.py`)

Order and safeguards, learned the hard way:
1. **lyrics.ovh** — keyed by artist+title (no wrong-song risk) but **frequently strips accents** on Spanish songs ("nubarrón" → "nubarrn").
2. **letras.com** — slug-based, verifies the page title; keeps accents and stanza structure.
3. **Genius** — search API + scrape `data-lyrics-container`; **keeps accents**, but title-verify the hit and cap line count (>120 lines ⇒ wrong/compilation page) or it returns garbage for obscure titles.
- Prefer the **accent-bearing** candidate for Spanish (detect: Spanish text with zero tildes ⇒ stripped ⇒ skip it).
- Strip `(bis)/(coro)/(x2)/(estribillo)` annotations — they are not lyrics.
- Duet/feature credits break keyed search → also try the **primary artist** (split on ` y `, ` ft`, ` feat`, `,`, `&`).

## Repair playbook

| Symptom | Fix |
|---|---|
| Wrong words / bad sync on AI songs | `qa_align_batch.py` (re-align all with current aligner, uses existing stems) |
| Missing accents / `(bis)` in lyrics | `qa_accents.py` (targets Spanish-no-tildes + annotation songs) |
| Dangling `#VIDEO/#BACKGROUND`, missing `#GAP` on human songs | `clean_tags.py` |
| Folder holds a different song (wrong audio) | move folder aside → re-run `ia_gen.py` for that title |
| Multi-second `~` note, coverage passes but sync is off | forced alignment can't handle the arrangement → Whisper or manual |
| Spanish/regional song with no accented source anywhere | manual lyrics (hand-entered) |

## Gotchas

- macOS filenames are **NFD**; shell globs with accented names miss the folder — iterate with Python `os.listdir` and match case-insensitively.
- exFAT copies (external SSDs) create `._` AppleDouble sidecars — skip files starting with `._`, and `rm -rf` can fail on them (delete contents explicitly then `rmdir`).
- Cross-volume `mv` (SMB↔local) can fail on `chflags`; move **within** the same volume, or copy then verify then remove.
- YouTube 429 → pass `IA_COOKIES="--cookies-from-browser firefox:<profile>"` (a browser logged into YouTube).
- The `#LANGUAGE` tag on existing songs is often wrong — auto-detect from the lyrics instead.
