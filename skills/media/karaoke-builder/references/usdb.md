# USDB source (primary human source)

USDB (`usdb.animux.de`) is the large community database of human-made UltraStar songs. It is bigger and better-curated than the ultrastar-es.org torrents, and each entry is a hand-timed `.txt` whose `#VIDEO` tag points at the media — so a "download" = fetch the txt + pull the media with yt-dlp. This is the **preferred human source**; the ultrastar-es torrent branch is a secondary fallback.

Human-made songs are already well-timed and well-segmented → they do **not** go through the AI align QA. Just `organize.py` + `validate.py`.

## Tool: Petzys/usdx_scraper

`github.com/Petzys/usdx_scraper` — a scriptable CLI scraper. Takes an **"Artist - Title"** list (exactly what `build_unified.py` produces), searches USDB, and downloads complete songs (txt + audio + video) to an output dir. Runs as a script (`python usdx_scraper.py`), not a pip package. **No LICENSE file in the repo** → do not vendor/redistribute it; clone it at setup time.

The skill ships a thin wrapper, `scripts/usdb_fetch.sh`, that runs it and points you at `organize.py` next.

## Setup (once)

```bash
git clone https://github.com/Petzys/usdx_scraper ~/karaoke-pipeline/usdx_scraper
<venv>/bin/python -m pip install -r ~/karaoke-pipeline/usdx_scraper/requirements.txt
```

Deps: `requests`, `python-dotenv`, `spotipy`, `beautifulsoup4`, `yt-dlp`.

## Credentials — environment only

A free USDB account is required. **Never hardcode or write the password.** usdx_scraper reads (via `load_dotenv` + `os.getenv`, falling back from the `-u/-p` flags):

- `USDX_USER`, `USDX_PASSWORD` — the USDB login.
- optional: `SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`, `SPOTIPY_PLAYLIST_ID` (Spotify-playlist input).

Set them as env vars, or put them in `usdx_scraper/.env` (gitignored). The wrapper only checks that one exists — it never reads or echoes the value.

## Usage

```bash
usdb_fetch.sh <list.txt> <output_dir> [MP3|MP4]      # list = "Artist - Title" per line
organize.py <output_dir> <library> --apply           # move into the library
validate.py --all <library>                          # single validation pass
```

Other input modes usdx_scraper supports: `-i <dir>` (match by local audio files), `-s <spotify playlist>` (needs Spotify creds), `-fa` (find ALL matches, not just one), `-ft MP3|MP4`, `-mvr <max video res>`.

## Where it slots in

```
Unified list  →  USDB (usdb_fetch.sh)  →  misses  →  ultrastar-es torrent  →  still missing  →  AI (ia_gen.py)
                        │                                                                              │
                        └────────────────────  organize.py → validate.py --all  ──────────────────────┘
```
Try USDB first (most coverage, complete media, no browser bridge needed); fall back to torrent, then AI.

## Required patches (usdx_scraper is outdated)

The upstream scraper has three breakages (fixed in `scripts/usdx_scraper.patch`; apply once after cloning):

```bash
cd ~/karaoke-pipeline/usdx_scraper && git apply <skill>/scripts/usdx_scraper.patch
```

1. **Zip filename hash** — USDB now serves `user-playlist-<hash>.zip`; the scraper built the URL without the hash → 404 on every txt. The patch parses the real URL from the ZIP_SAVE page.
2. **Video format** — it requested `bestvideo[ext=m4a]` (m4a is audio) → "Requested format is not available". The patch uses `avc1/mp4`.
3. **YouTube media (cookies + PO token + JS challenge)** — the Python API failed with "The page needs to be reloaded"; the patch switches `download_song` to the yt-dlp **CLI** with `--remote-components ejs:github`, cookies from env `USDX_YT_COOKIES="firefox:<profile>"`, and the **bgutil PO-token server** running. Full setup in `references/youtube-po-token.md` — this is required for all YouTube downloads now (USDB media *and* `ia_gen.py`).

Note: media download still fails per-song when the entry's `#VIDEO` URL is dead/region-locked — that's the entry's problem, not the pipeline. The **txt (human timing) always downloads**, which is the valuable part.

## Replacing AI songs in bulk — usdb_replace.py

`usdb_replace.py [limit]` reads `usdb_matches.csv`, and for every `exacto`/`por-titulo` row fetches the USDB version, finalizes it to the local name, backs up the AI folder, and swaps it in — **only if a complete song (txt + media) downloaded and validates**, otherwise it keeps the AI version. Excludes a keep-list (e.g. the first song you made). Needs the PO-token setup above.

## Same-language naming (foreign-language songs)

USDB (and good practice) keeps a song **entirely in one language**: the movie/artist name matches the song's language. The German "Let It Go" is **Die Eiskönigin – Lass jetzt los**, not "Frozen – Lass jetzt los"; the French is **La Reine des Neiges – Libérée, délivrée**. When searching USDB or naming a localized song, use the localized movie/artist name (`finalize.py` rewrites folder + tags). `usdb_match.py` also searches **by title alone** so it finds these regardless of the movie-name language.

## Finding AI songs to replace — usdb_match.py

`usdb_match.py [root]` walks every AI song (has a `[Vocals]` stem) and searches USDB for it (artist+title, then title-only). Writes `usdb_matches.csv` with `usdb_id` + `usdb_nombre` + a confidence column (`exacto` / `por-titulo` / `dudoso` / `no`). Review it, then feed the confident matches' "Artist - Title" back through `usdb_fetch.sh` to replace the AI versions with human ones. Search-only — downloads nothing.
