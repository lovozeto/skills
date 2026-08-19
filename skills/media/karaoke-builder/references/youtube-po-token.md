# YouTube downloads — the current anti-bot gauntlet (required)

As of 2026, YouTube challenges yt-dlp downloads on two layers. Metadata still comes back, but the **actual media stream** fails with `ERROR: The page needs to be reloaded.` unless BOTH are handled. This affects **every** yt-dlp download in this pipeline — `ia_gen.py` (AI generation) and `usdb_fetch.sh` (USDB media). Browser cookies alone are no longer enough.

## The two layers

1. **PO token (SABR).** YouTube requires a Proof-of-Origin token for stream URLs. Solved by the **bgutil** provider: a small Node server that mints tokens, plus a yt-dlp plugin that fetches them.
2. **JS challenge (n-sig / signature).** YouTube ships an obfuscated JS challenge that must be solved to decipher stream URLs. yt-dlp offloads this to an **EJS** (External JavaScript) solver script — the bundled one is stale, so yt-dlp must be told to download the current one.

## Setup (once)

```bash
# 1) PO-token plugin (into the same venv as yt-dlp)
<venv>/bin/python -m pip install -U yt-dlp bgutil-ytdlp-pot-provider

# 2) PO-token server (Node ≥ 18)
git clone https://github.com/Brainicism/bgutil-ytdlp-pot-provider ~/karaoke-pipeline/bgutil
cd ~/karaoke-pipeline/bgutil/server && npm install && npx tsc
node build/main.js            # runs on 127.0.0.1:4416 — keep it running while downloading
```

## Per-download requirements

Every yt-dlp download command must include:

- `--remote-components ejs:github` — lets yt-dlp fetch the up-to-date EJS challenge solver (one-time download, then cached). Needs **Deno** or **Node** on PATH as the JS runtime.
- `--cookies-from-browser firefox:<profile>` — a browser logged into YouTube (Zen/Firefox). Refresh the login if it goes stale.
- the **bgutil server running** on :4416 (the plugin auto-detects it).

`ia_gen.py` and the `usdx_scraper.patch`'d `download_song` both add `--remote-components ejs:github`; the cookies come from `IA_COOKIES` / `USDX_YT_COOKIES`. Start the bgutil server before any run.

## Symptoms → cause

| Error | Meaning |
|---|---|
| `Sign in to confirm you're not a bot` | no cookies — add `--cookies-from-browser` |
| `The page needs to be reloaded` | PO token and/or JS challenge unsolved — start bgutil server **and** add `--remote-components ejs:github` |
| `Challenge solver lib script version 0.x is not supported` | EJS solver stale — `--remote-components ejs:github` downloads the supported one |
| `Requested format is not available` (only some clients) | that player client exposed no formats without a token — not the format string |

This is a moving target; when it breaks again, update yt-dlp + the bgutil provider first.

## Gotcha: the server process name

The server runs as `node build/main.js` (relative argv) — it does **not** contain the string "bgutil". A watchdog like `pgrep -f 'bgutil.*main.js'` will never match it, think the server is down, and spawn duplicates that die with `EADDRINUSE: address already in use :::4416` while the real one keeps working. Detect it by port instead: `curl -s http://127.0.0.1:4416/ping`. The server is stable on its own (hours of uptime) — you rarely need a watchdog at all.
