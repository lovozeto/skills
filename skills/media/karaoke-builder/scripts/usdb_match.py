#!/usr/bin/env python3
"""Recorre las canciones IA del NAS y busca cuáles están en USDB (usdb.animux.de) para
reemplazarlas por la versión humana. Solo BUSCA (no descarga). Credenciales por env
(USDX_USER/USDX_PASSWORD o el .env del scraper). Escribe usdb_matches.csv.
Uso: usdb_match.py [root]   (default NAS)
"""
import sys, os, re, csv, unicodedata, time
KP = os.path.expanduser("~/karaoke-pipeline")
SCRAPER = os.path.join(KP, "usdx_scraper")
sys.path.insert(0, SCRAPER)
from dotenv import load_dotenv
load_dotenv(os.path.join(SCRAPER, ".env"))
from src.sources.lyrics.UsdbAnimuxDe import UsdbAnimuxDe
NAS = sys.argv[1] if len(sys.argv) > 1 else "/Volumes/documents/Ultrastar"

def read(p):
    r = open(p, "rb").read()
    if r.startswith(b"\xef\xbb\xbf"): r = r[3:]
    try: return r.decode("utf-8")
    except: return r.decode("cp1252", "replace")
def norm(s):
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", s)

usdb = UsdbAnimuxDe({"user": None, "password": None, "output_path": "/tmp"})
print("USDB login OK", flush=True)

def find(artist, title):
    na, nt = norm(artist), norm(title)
    # 1) artista+título (preciso)
    try: r = usdb._execute_search(artist, title)
    except Exception: r = []
    for _id, name in r:
        if " - " in name:
            a, t = name.split(" - ", 1)
            if norm(t) == nt and (norm(a) == na or na in norm(a) or norm(a) in na):
                return _id, name, "exacto"
    # 2) título solo (resuelve idioma/nombre de película); acepta si el título calza
    try: r2 = usdb._execute_search("", title)
    except Exception: r2 = []
    for _id, name in r2:
        if " - " in name and norm(name.split(" - ", 1)[1]) == nt:
            return _id, name, "por-titulo"
    if r or r2:
        top = (r or r2)[0]
        return top[0], top[1], "dudoso"
    return None, None, "no"

targets = []
for d in sorted(os.listdir(NAS)):
    p = os.path.join(NAS, d)
    if not os.path.isdir(p) or d.startswith("."): continue
    files = [f for f in os.listdir(p) if not f.startswith(".")]
    if not any("[Vocals]" in f for f in files): continue     # solo IA
    txts = [f for f in files if f.lower().endswith(".txt")]
    if not txts: continue
    c = read(os.path.join(p, txts[0]))
    a = (re.search(r"^#ARTIST:(.*)$", c, re.M) or [None, ""])[1].strip()
    t = (re.search(r"^#TITLE:(.*)$", c, re.M) or [None, ""])[1].strip()
    targets.append((d, a, t))
print(f"IA a revisar: {len(targets)}", flush=True)

rows = []; hits = 0
for i, (d, a, t) in enumerate(targets, 1):
    _id, name, conf = find(a, t)
    if conf in ("exacto", "por-titulo"): hits += 1
    rows.append([d, a, t, _id or "", name or "", conf])
    if i % 25 == 0: print(f"  [{i}/{len(targets)}] en USDB hasta ahora: {hits}", flush=True)
    time.sleep(0.2)

with open(f"{KP}/usdb_matches.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["carpeta", "artista", "titulo", "usdb_id", "usdb_nombre", "confianza"])
    w.writerows(rows)
exact = sum(1 for r in rows if r[5] == "exacto"); bytit = sum(1 for r in rows if r[5] == "por-titulo")
print(f"\n=== {len(targets)} IA | en USDB: exacto {exact} + por-título {bytit} = {exact+bytit} candidatas a reemplazar | dudosas {sum(1 for r in rows if r[5]=='dudoso')} | no {sum(1 for r in rows if r[5]=='no')}")
print(f"→ {KP}/usdb_matches.csv")
