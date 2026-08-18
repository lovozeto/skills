#!/usr/bin/env python3
"""Reemplaza canciones IA por la versión HUMANA de USDB, para las que el buscador marcó
'exacto'/'por-titulo' en usdb_matches.csv. Por cada una: baja de USDB (txt+media), finaliza
al nombre nuestro, respalda la IA y la reemplaza — SOLO si bajó completa con media.
Necesita: server bgutil (PO-token) arriba + USDX_YT_COOKIES. Uso: usdb_replace.py [limite]
"""
import os, sys, csv, subprocess, shutil, unicodedata, time
kp = os.path.expanduser("~/karaoke-pipeline"); NAS = "/Volumes/documents/Ultrastar"
SK = "/Users/eloboguerrero/GitHub/skills/skills/media/karaoke-builder"
BK = "/Volumes/documents/_no_karaoke"; TMP = f"{kp}/usdb_repl_tmp"
LOG = f"{kp}/usdb_replace.log"
LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else 9999
def log(m): line = f"[{time.strftime('%H:%M:%S')}] {m}"; print(line, flush=True); open(LOG, "a").write(line + "\n")
def has_media(p): return any(os.path.splitext(f)[1].lower() in (".mp4", ".mp3", ".m4a", ".webm") for f in os.listdir(p))

rows = [r for r in csv.reader(open(f"{kp}/usdb_matches.csv", encoding="utf-8"))][1:]
EXCLUDE = ("scooby",)   # no reemplazar (valor sentimental: la primera que hicimos)
todo = [r for r in rows if len(r) >= 6 and r[5] in ("exacto", "por-titulo")
        and not any(x in r[0].lower() for x in EXCLUDE)][:LIMIT]
log(f"===== reemplazo USDB: {len(todo)} candidatas =====")
os.makedirs(BK, exist_ok=True)
ok = nomedia = skip = fail = 0
for i, r in enumerate(todo, 1):
    folder, artist, title = r[0], r[1], r[2]
    dest = os.path.join(NAS, folder)
    if not os.path.isdir(dest): log(f"[{i}/{len(todo)}] SKIP (ya no está): {folder}"); skip += 1; continue
    log(f"[{i}/{len(todo)}] {folder}")
    shutil.rmtree(TMP, ignore_errors=True); os.makedirs(TMP)
    lst = f"{TMP}/q.txt"; open(lst, "w", encoding="utf-8").write(f"{artist} - {title}\n")
    try:
        subprocess.run(["bash", f"{SK}/scripts/usdb_fetch.sh", lst, TMP, "MP4"],
                       capture_output=True, text=True, timeout=900)
    except Exception as e:
        log(f"    ERROR fetch: {e}"); fail += 1; continue
    got = [d for d in os.listdir(TMP) if os.path.isdir(os.path.join(TMP, d)) and has_media(os.path.join(TMP, d))]
    if not got:
        log(f"    sin media en USDB → dejo la IA"); nomedia += 1; continue
    src = os.path.join(TMP, got[0])
    subprocess.run(["python3", f"{kp}/finalize.py", src, artist, title], capture_output=True, text=True)
    fin = os.path.join(TMP, f"{artist} - {title}"); src = fin if os.path.isdir(fin) else src
    mp4 = next((f for f in os.listdir(src) if f.lower().endswith(".mp4")), None)
    if mp4: subprocess.run(["python3", f"{kp}/settags.py", src, "--MP3", mp4, "--AUDIO", mp4], capture_output=True)
    bk = os.path.join(BK, folder + " [IA-reemplazada]"); shutil.rmtree(bk, ignore_errors=True)
    shutil.move(dest, bk)                                   # respaldar IA
    subprocess.run(["cp", "-R", src, dest], capture_output=True)   # USDB → NAS
    v = subprocess.run(["python3", f"{kp}/validate.py", dest], capture_output=True, text=True).stdout.strip()
    if v == "PASS": log(f"    ✅ reemplazada [{v}]"); ok += 1
    else:                                                   # si no valida, revertir a la IA
        shutil.rmtree(dest, ignore_errors=True); shutil.move(bk, dest); log(f"    revertido (USDB no validó: {v})"); fail += 1
    time.sleep(1)
shutil.rmtree(TMP, ignore_errors=True)
log(f"===== FIN. reemplazadas:{ok}  sin-media:{nomedia}  skip:{skip}  fail:{fail} =====")
