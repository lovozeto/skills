#!/usr/bin/env python3
"""VALIDACIÓN ÚNICA — una sola vara para TODA canción (torrent o IA). Sin sub-versiones:
o PASA, o se marca en la lista 'revisar' con el motivo. No re-genera nada, solo revisa.
Uso: validate.py "<carpeta>"        → imprime PASS / FLAG:motivos
     validate.py --all [dir]         → recorre el NAS, escribe revisar.txt con los que fallan
"""
import sys, os, re, unicodedata
NAS = "/Volumes/documents/Ultrastar"; KP = "/Users/eloboguerrero/karaoke-pipeline"

def read(p):
    raw = open(p, "rb").read()
    if raw.startswith(b"\xef\xbb\xbf"): raw = raw[3:]
    try: return raw.decode("utf-8")
    except: return raw.decode("cp1252", "replace")

def check(folder):
    files = [f for f in os.listdir(folder) if not f.startswith(".")]
    txts = [f for f in files if f.lower().endswith(".txt")]
    if not txts: return ["sin-txt"]
    c = read(os.path.join(folder, txts[0]))
    tags = {}; notes = 0; breaks = 0; beats = []; has_bom = c and False
    for l in c.splitlines():
        m = re.match(r"#([A-Z0-9]+):(.*)", l)
        if m: tags[m.group(1)] = m.group(2).strip(); continue
        if l[:1] in ":*FRG" and len(l.split()) >= 5:
            notes += 1
            try: beats.append(int(l.split()[1]))
            except: pass
        elif l.startswith("- "): breaks += 1
    bad = []
    # tags requeridos
    for k in ["TITLE", "ARTIST", "BPM"]:
        if not tags.get(k): bad.append(f"falta-#{k}")
    if not (tags.get("AUDIO") or tags.get("MP3")): bad.append("falta-audio-tag")
    if "GAP" not in tags: bad.append("falta-#GAP")
    # media resuelve (compara normalizado NFC ↔ NFD por los nombres con tilde de macOS)
    norm_files = {unicodedata.normalize("NFC", f) for f in files}
    for k in ["MP3", "AUDIO", "VIDEO", "COVER", "VOCALS", "INSTRUMENTAL", "BACKGROUND"]:
        v = tags.get(k)
        if v and unicodedata.normalize("NFC", v) not in norm_files: bad.append(f"#{k}→archivo-ausente")
    # cuerpo
    if notes < 5: bad.append(f"pocas-notas({notes})")
    if breaks < 1: bad.append("sin-saltos-de-línea")
    # beats monótonos (aprox; los duetos intercalan P1/P2 pero cada voz sube)
    backs = sum(1 for i in range(1, len(beats)) if beats[i] < beats[i-1]-16)   # ignora solapes chicos
    if backs > 3 and "P1" not in c:                                            # solo si hay varios
        bad.append(f"beats-desordenados({backs})")
    # GAP sano (acepta coma decimal europea: 12983,14 = 13s)
    try:
        g = int(float(re.sub(r"[^0-9,.\-]", "", tags.get("GAP", "0")).replace(",", ".") or 0))
        if g > 180000 or g < -60000: bad.append(f"GAP-raro({g})")   # negativos moderados son válidos
    except: pass
    # encoding
    if open(os.path.join(folder, txts[0]), "rb").read(3) == b"\xef\xbb\xbf": bad.append("tiene-BOM")
    return bad

if len(sys.argv) >= 2 and sys.argv[1] == "--all":
    root = sys.argv[2] if len(sys.argv) > 2 else NAS
    fails = []; ok = 0
    for d in sorted(os.listdir(root)):
        p = os.path.join(root, d)
        if not os.path.isdir(p) or d.startswith("."): continue
        bad = check(p)
        if bad: fails.append((d, bad)); print(f"FLAG {d}: {', '.join(bad)}")
        else: ok += 1
    open(f"{KP}/revisar.txt", "w", encoding="utf-8").write(
        "\n".join(f"{d}\t{', '.join(b)}" for d, b in fails) + ("\n" if fails else ""))
    print(f"\n=== PASA:{ok}  REVISAR:{len(fails)}  → {KP}/revisar.txt ===")
else:
    bad = check(sys.argv[1].rstrip("/"))
    print("FLAG:" + ", ".join(bad) if bad else "PASS")
