#!/usr/bin/env python3
"""Compila la LISTA UNIFICADA de pendientes desde todas las colas y la cruza contra
lo que ya existe en el NAS (para no repetir). Salida: unified_need.txt (Artista|Título
que faltan) + resumen. Uso: build_unified.py
"""
import os, re, unicodedata, glob
KP = "/Users/eloboguerrero/karaoke-pipeline"
NAS = "/Volumes/documents/Ultrastar"
SOURCES = [f"{KP}/queue_all.txt", f"{KP}/queue_vallenatos.txt", f"{KP}/queue.txt"]

def simplify(s):
    s = unicodedata.normalize("NFKD", s).lower().strip()
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"\(.*?\)|\[.*?\]", "", s)
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", "", s)).strip()

# 1) juntar y dedup
seen = {}; order = []
for src in SOURCES:
    if not os.path.exists(src): continue
    for ln in open(src, encoding="utf-8"):
        ln = ln.strip()
        if not ln or ln.startswith("#") or "|" not in ln: continue
        a, t = ln.split("|", 1); a, t = a.strip(), t.strip()
        key = simplify(f"{a} {t}")
        if key and key not in seen:
            seen[key] = (a, t); order.append(key)

# 2) existentes en el NAS
existing = []
if os.path.isdir(NAS):
    existing = [simplify(d) for d in os.listdir(NAS)
                if os.path.isdir(os.path.join(NAS, d)) and not d.startswith(".")]
exset = set(existing)
def have(a, t):
    key = simplify(f"{a} {t}"); A, T = simplify(a), simplify(t)
    if key in exset: return True
    return any(A and T and A in e and T in e for e in existing)

# 3) clasificar
need = []; havec = 0
for key in order:
    a, t = seen[key]
    if have(a, t): havec += 1
    else: need.append((a, t))

with open(f"{KP}/unified_need.txt", "w", encoding="utf-8") as f:
    for a, t in need: f.write(f"{a}|{t}\n")

print(f"colas: {len(order)} únicas | ya en NAS: {havec} | FALTAN: {len(need)}")
print(f"→ escrito {KP}/unified_need.txt ({len(need)} canciones)")
