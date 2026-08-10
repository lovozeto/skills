#!/usr/bin/env python3
"""QA con el ALINEADOR NUEVO (letra verificada + alineación forzada + sílabas + melisma)
sobre las IA ya bajadas. Reemplaza al QA viejo de sub-versiones. Una sola vara:
  - align_lyrics reescribe el txt al estándar → marca #QA:aligned.
  - si no hay letra en la web (FLAG) → NO toca el txt (no corrompe), lo manda a revisar.txt.
Respalda cada txt antes. Uso: qa_align_batch.py [root]   (default: NAS)
"""
import os, sys, subprocess, shutil, time, re
NAS = "/Volumes/documents/Ultrastar"; KP = "/Users/eloboguerrero/karaoke-pipeline"
PYV = os.path.expanduser("~/UltraSinger/.venv/bin/python")
ROOT = sys.argv[1] if len(sys.argv) > 1 else NAS
BK = f"{KP}/qa_align_backups"; LOG = f"{KP}/qa_align.log"; os.makedirs(BK, exist_ok=True)
LANG = {"español":"es","espanol":"es","spanish":"es","english":"en","ingles":"en","inglés":"en",
        "français":"fr","francais":"fr","french":"fr","italiano":"it","português":"pt","portugues":"pt",
        "es":"es","en":"en"}
def read(p):
    r = open(p, "rb").read()
    if r.startswith(b"\xef\xbb\xbf"): r = r[3:]
    try: return r.decode("utf-8")
    except: return r.decode("cp1252", "replace")
def log(m): line=f"[{time.strftime('%H:%M:%S')}] {m}"; print(line,flush=True); open(LOG,"a").write(line+"\n")

targets = []
for d in sorted(os.listdir(ROOT)):
    p = os.path.join(ROOT, d)
    if not os.path.isdir(p) or d.startswith("."): continue
    files = [f for f in os.listdir(p) if not f.startswith(".")]
    txts = [f for f in files if f.lower().endswith(".txt")]
    if not txts: continue
    if not any("[Vocals]" in f for f in files): continue    # solo IA (con stem)
    c = read(os.path.join(p, txts[0]))
    if re.search(r"^#QA:aligned", c, re.M): continue         # ya con el aligner nuevo
    m = re.search(r"^#LANGUAGE:(.*)$", c, re.M)
    lang = LANG.get((m.group(1).strip().lower() if m else "es"), "es")
    targets.append((d, p, os.path.join(p, txts[0]), lang))

log(f"===== QA-align: {len(targets)} IA por procesar en {ROOT} =====")
ok = flag = fail = 0
for i, (d, p, tp, lang) in enumerate(targets, 1):
    log(f"[{i}/{len(targets)}] ({lang}) {d}")
    shutil.copy2(tp, os.path.join(BK, d + ".txt"))
    try:
        r = subprocess.run([PYV, f"{KP}/align_lyrics.py", p, lang], capture_output=True, text=True, timeout=1200)
        out = (r.stdout or "").strip().splitlines(); msg = out[-1] if out else (r.stderr or "?").strip()[-120:]
        if r.returncode == 0 and "OK align_lyrics" in (msg or ""):
            c = read(tp); lines = [l for l in c.splitlines() if not l.startswith("#QA:")]; o = []
            for l in lines:
                o.append(l)
                if l.upper().startswith("#TITLE:"): o.append("#QA:aligned")
            open(tp, "w", encoding="utf-8", newline="\n").write("\n".join(o) + "\n")
            log(f"    OK {msg}"); ok += 1
        else:
            open(f"{KP}/revisar.txt", "a").write(f"{d}\t{msg}\n")
            log(f"    FLAG {msg}"); flag += 1
    except Exception as e:
        log(f"    ERROR {e}"); fail += 1
log(f"===== FIN. aligned:{ok}  flag(revisar):{flag}  fail:{fail} (respaldos en {BK}) =====")
