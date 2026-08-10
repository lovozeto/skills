# Configuration

The scripts were built for one machine and carry hardcoded paths at the top of each file. Before reuse, set these to your environment (edit the constants, or adapt to env vars).

## Paths

| Constant | Meaning | Example |
|---|---|---|
| `NAS` (in most scripts) | Library dir where finished songs live | `/Volumes/documents/Ultrastar` |
| `KP` | Pipeline dir: scripts, logs, backups, queues | `~/karaoke-pipeline` |
| `PYV` / venv | Python with `whisperx`, `librosa`, `demucs`, `hyphen` installed | `~/UltraSinger/.venv/bin/python` |
| *watched* | qBittorrent auto-load folder (drop `.torrent` here) | `/Volumes/media/downloads/Torrent/watched` |
| *completed* | qBittorrent finished downloads (organize reads here) | `/Volumes/media/downloads/Torrent/completed` |

## Environment variables

- `IA_COOKIES` — e.g. `--cookies-from-browser firefox:/path/to/profile` (a browser logged into YouTube; avoids 429). `ia_gen.py` splits it into yt-dlp args.
- `QBT_HOST` / `QBT_USER` / `QBT_PASS` — qBittorrent Web API (used by `qbt_watch.py`). **`QBT_PASS` is read from the environment only — never written to a file.**
- `STALL_MIN` / `POLL` — `qbt_watch.py` tuning (default: cancel after 8 min with 0 seeders, poll 60 s).

## Dependencies

- `ffmpeg`, `yt-dlp`, `demucs` (htdemucs), Python: `whisperx` (+ its wav2vec align models, downloaded per language on first use), `librosa`, `soundfile`, `PyHyphen` (es/en/de/fr dicts).
- A browser logged into **ultrastar-es.org** for the torrent branch (search is public; download needs the session). `torrent_bridge.py` runs a loopback HTTP bridge on `127.0.0.1:8899`; `torrent_fetch.js` runs in the browser tab and POSTs each `.torrent` to it.
- Optional: qBittorrent with a *watched* folder; a browser logged into YouTube for cookies.

## Not included

- **Duet diarization** (pyannote.audio + a HuggingFace token) — duets generate as a single voice.
- Orchestration wrappers (the overnight `*.sh` chains) were session-specific; compose the scripts to taste.
