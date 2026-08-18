---
name: karaoke-builder
description: Build and repair an UltraStar Deluxe karaoke library. Download human-made songs from ultrastar-es.org by torrent, or generate missing ones with AI (yt-dlp video+audio → demucs stems → forced alignment against VERIFIED web lyrics, not Whisper transcription), all written to the UltraStar 1.1.0 standard and cleared by a single validation pass. Use when building, fixing, or extending karaoke songs for UltraStar / UltraStar WorldParty.
---

# karaoke-builder — one library, one standard

Human or AI, one bar. Songs come from a **human source** — USDB (`usdb.animux.de`, the big community DB — preferred) or ultrastar-es.org torrents — or from **AI generation** for whatever neither has. All converge on the same `organize → single validation → library` tail. There are **no sub-versions** — a song either passes or lands on a `revisar.txt` review list. Human-made songs are already well-timed and skip the AI align QA. All scripts ship in `scripts/`; the format spec, the full flow, and the USDB source live in `references/`.

## The core idea (why this works)

The hard part of AI karaoke is timing the lyrics. The naive path — Whisper *transcribes* the audio (guesses the words) then a QA pass corrects them — drifts and fails on damaged transcripts. This pipeline inverts it: fetch the **correct lyrics** from the web and use **forced alignment** (whisperX `align`) to place *known* words on the audio. Words are right by construction; only timing is computed. `align_lyrics.py` is that core. If the lyrics can't be found or don't align (coverage gate), the song is flagged — never silently downgraded.

## When it applies

- Building a karaoke library for a party / UltraStar install.
- A song sounds off (bad sync, wrong words, missing accents, wrong audio) and needs repair.
- Adding new songs (movie soundtracks, artists, specific tracks).

## Pipeline (see `references/pipeline.md` for the full diagram)

1. **Unified list** — `build_unified.py` merges queues and crosses them against what's already in the library so nothing is redone.
2. **USDB (primary human source)** — `usdb_fetch.sh` runs [Petzys/usdx_scraper](https://github.com/Petzys/usdx_scraper) over the "Artist - Title" list: searches USDB and downloads complete songs (txt + audio + video). Credentials come from env only (`USDX_USER`/`USDX_PASSWORD`). Biggest coverage, no browser needed. See `references/usdb.md`.
3. **Torrent branch (fallback)** — for USDB misses, `site_match.py` searches ultrastar-es.org and picks the correct torrent (exact artist+title, penalizing `again`/remix/live); the browser (logged in) fetches each `.torrent` and POSTs it to `torrent_bridge.py` (loopback bridge) → qBittorrent *watched* folder. `qbt_watch.py` cancels **stalled** torrents and reroutes them to AI. `torrent_fetch.js` runs in the browser tab.
4. **AI branch** — `ia_gen.py`: one yt-dlp pass for **video+audio** (h264/mp4, prefer official + `(latino)` where dubs matter) → `demucs` stems → cover (`add_cover.py`) → `align_lyrics.py` (verified lyrics + forced alignment). Falls back to Whisper only when no web lyrics exist.
5. **Organize** — `organize.py`: canonical naming, UTF-8 no-BOM, dedupe by quality, move to the library. `finalize.py` forces canonical identity when a generator misnames a folder.
6. **Single validation** — `validate.py --all` checks every song (tags, media resolves, GAP sane, notes/line-breaks present, beats monotonic). Pass → library; fail → `revisar.txt`.

## Repair tools

- `qa_align_batch.py` — re-align every AI song with the current `align_lyrics.py` (uses existing `[Vocals]` stems, no re-download). Backs up each txt.
- `qa_accents.py` — find and re-align songs with **dropped accents** (Spanish lyrics with no tildes) or `(bis)/(coro)/(x2)` annotations bleeding into the lyrics.
- `clean_tags.py` — strip dangling `#VIDEO/#BACKGROUND` tags on human songs, add missing `#GAP`.
- `usdb_match.py` — search USDB for every AI song → `usdb_matches.csv`; feed the confident matches back through `usdb_fetch.sh` to replace AI versions with human ones. See `references/usdb.md`.
- Wrong audio (a folder holding a different song): move the bad folder aside, then re-run `ia_gen.py` for that title.

## Hard-won conventions (do not relearn these)

- **Encoding:** UTF-8 **without BOM**, LF newlines, **no `#ENCODING` tag**. macOS stores filenames NFD → normalize to NFC. Skip AppleDouble `._` files (exFAT copies create them).
- **Format target:** `#VERSION:1.1.0` (== 1.0.0, universal). Declare `#VOCALS`/`#INSTRUMENTAL` stems, `[CO]` cover, optional `[BG]`. See `references/ultrastar-format.md`.
- **Syllables + melisma:** one note per **syllable** (PyHyphen), with `~` continuation notes for sustained pitch changes — capped so a held note never explodes into dozens of `~`.
- **Language:** `align_lyrics.py` auto-detects es/en/de/fr from the lyrics and loads the matching wav2vec align model; do not trust a possibly-wrong `#LANGUAGE` tag.
- **Disney / dubbed films:** always the **Latin American** dub unless asked otherwise. The movie goes in `#ARTIST` for findability; the singer in `#COMMENT`. Watch Spain vs latino titles (e.g. *Hermano Oso* [Spain] vs *Tierra de Osos* [latino]).
- **Same-language rule:** a foreign-language song stays **entirely in one language** — the movie/artist name matches the song's language: German *Die Eiskönigin – Lass jetzt los*, French *La Reine des Neiges – Libérée, délivrée* (not "Frozen – …"). This is also how USDB indexes them; `usdb_match.py` searches by title alone to find them regardless. `finalize.py` rewrites folder + tags to the localized name.
- **Lyrics sources (`fetch_lyrics.py`):** lyrics.ovh (keyed, but often strips accents) → letras.com → Genius (accented, title-verified, line-capped to reject wrong pages). Prefers the accent-bearing source for Spanish; strips `(bis)`-type annotations.
- **Coverage gate is the safety net:** a wrong-lyrics match yields low coverage → the song flags instead of getting garbage timing. Trust it; don't force.
- **No sub-versions.** One validation, one bar, one review list.

## Known limits (route to manual, don't fight)

- Obscure regional songs (some vallenatos) and a few old boleros have **no accented lyrics anywhere** → collect them in a review list for hand-entered lyrics.
- A song whose real recording repeats verses in a way the flat lyrics don't (heavy ad-libs) can defeat forced alignment (a multi-second note is the tell) → Whisper or manual.
- **Duets** (P1/P2 split) need speaker diarization (pyannote + a HuggingFace token) — out of scope here; duets generate as a single voice.

## Configuration (paths the scripts expect)

Edit these at the top of the scripts, or set the env vars, before running. See `references/config.md`.

- Library dir (`NAS`) — where finished songs live.
- Pipeline dir (`KP`) — where the scripts + logs + backups live.
- `USDX_USER` / `USDX_PASSWORD` — USDB login for `usdb_fetch.sh` (env only — never written to a file). Requires cloning usdx_scraper; see `references/usdb.md`.
- qBittorrent *watched*/*completed* dirs, and `QBT_HOST` / `QBT_USER` / `QBT_PASS` (password from env only — never written to a file).
- `IA_COOKIES` — `--cookies-from-browser firefox:<profile>` to avoid YouTube 429.

## Steps — common tasks

**Build a library:** `build_unified.py` → `usdb_fetch.sh <list> <out>` (USDB, most coverage) → `organize.py`; for what USDB lacks, `site_match.py` + torrent, then `ia_gen.py <misses>`; finally `organize.py` → `validate.py --all`.

**Fix all AI lyrics:** `qa_align_batch.py` then `qa_accents.py`, then `validate.py --all`; review `revisar.txt`.

**Add songs:** append `Artist|Title` lines to a queue, cross with `build_unified.py`, then run the source decision. Verify any ambiguous title/dub with a quick web check before queueing — never invent a localized title.
