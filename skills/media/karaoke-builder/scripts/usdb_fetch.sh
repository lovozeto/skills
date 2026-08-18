#!/bin/bash
# Fetch COMPLETE UltraStar songs from USDB (usdb.animux.de) via Petzys/usdx_scraper.
# Human-made, well-timed songs → they do NOT need the AI align QA; just organize + validate.
# Credentials come from the ENVIRONMENT ONLY (USDX_USER / USDX_PASSWORD) or a .env in the
# scraper dir — never hardcoded, never written by this skill.
#
# Setup (once):
#   git clone https://github.com/Petzys/usdx_scraper ~/karaoke-pipeline/usdx_scraper
#   <venv>/bin/python -m pip install -r ~/karaoke-pipeline/usdx_scraper/requirements.txt
#   export USDX_USER=...  USDX_PASSWORD=...       # or put them in usdx_scraper/.env
#
# Usage: usdb_fetch.sh <list.txt "Artist - Title" per line> <output_dir> [MP3|MP4]
set -euo pipefail
LIST="${1:?lista 'Artista - Título' requerida}"; OUT="${2:?dir de salida requerido}"; FT="${3:-MP4}"
PY="${KARAOKE_PY:-$HOME/UltraSinger/.venv/bin/python}"
SCRAPER="${USDX_SCRAPER_DIR:-$HOME/karaoke-pipeline/usdx_scraper}"
[ -f "$SCRAPER/usdx_scraper.py" ] || { echo "usdx_scraper no está en $SCRAPER — clónalo primero."; exit 1; }
if [ -z "${USDX_USER:-}" ] && [ ! -f "$SCRAPER/.env" ]; then
  echo "Falta credencial USDB: exporta USDX_USER/USDX_PASSWORD o crea $SCRAPER/.env (nunca se escriben aquí)."; exit 1
fi
# usdx_scraper upstream está roto (hash del zip, formato de video, cookies) — hay que aplicar el patch
if ! grep -q "PATCH: USDB now appends" "$SCRAPER/src/sources/lyrics/UsdbAnimuxDe.py" 2>/dev/null; then
  echo "usdx_scraper SIN parchar → aplica una vez:  cd $SCRAPER && git apply <skill>/scripts/usdx_scraper.patch  (ver references/usdb.md)"; exit 1
fi
# cookies de YouTube para evitar 403 (opcional pero recomendado): export USDX_YT_COOKIES="firefox:<perfil>"
mkdir -p "$OUT"
( cd "$SCRAPER" && "$PY" usdx_scraper.py -it "$LIST" -o "$OUT" -ft "$FT" -mvr 720 )
echo "USDB → $OUT listo. Siguiente: organize.py \"$OUT\" <biblioteca> --apply && validate.py --all <biblioteca>"
