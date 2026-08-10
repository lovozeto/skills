#!/usr/bin/env python3
"""Remediación mecánica segura de canciones HUMANAS (sin stem [Vocals], no las toca el rescate):
  - quita tags #VIDEO/#BACKGROUND colgados (apuntan a archivo inexistente) → cosmético, la canción suena igual.
  - agrega #GAP:0 si falta (default del parser).
Escribe solo si hay cambios. Uso: clean_tags.py
"""
import os, re, unicodedata
NAS = "/Volumes/documents/Ultrastar"
def read(p):
    raw = open(p, "rb").read()
    if raw.startswith(b"\xef\xbb\xbf"): raw = raw[3:]
    try: return raw.decode("utf-8")
    except: return raw.decode("cp1252", "replace")
vid=gap=0; touched=0
for d in sorted(os.listdir(NAS)):
    p = os.path.join(NAS, d)
    if not os.path.isdir(p) or d.startswith("."): continue
    files = [f for f in os.listdir(p) if not f.startswith(".")]
    if any("[Vocals]" in f for f in files): continue          # IA → lo maneja el rescate
    txts = [f for f in files if f.lower().endswith(".txt")]
    if not txts: continue
    tp = os.path.join(p, txts[0]); lines = read(tp).splitlines()
    norm = {unicodedata.normalize("NFC", f) for f in files}
    out = []; changed = False; has_gap = False; bpm_i = -1
    for l in lines:
        m = re.match(r"#(VIDEO|BACKGROUND):(.*)", l)
        if m and unicodedata.normalize("NFC", m.group(2).strip()) not in norm:
            changed = True; vid += 1; continue                  # tag colgado → fuera
        if l.upper().startswith("#GAP:"): has_gap = True
        if l.upper().startswith("#BPM:"): bpm_i = len(out)
        out.append(l)
    if not has_gap:
        ins = bpm_i + 1 if bpm_i >= 0 else 0
        out.insert(ins, "#GAP:0"); changed = True; gap += 1
    if changed:
        open(tp, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
        touched += 1
print(f"canciones tocadas: {touched}  | tags colgados quitados: {vid}  | #GAP agregados: {gap}")
