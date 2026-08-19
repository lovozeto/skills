#!/usr/bin/env python3
"""Trae un pack de canciones NUEVAS: USDB primero (humano), IA si USDB no la tiene con media.
Por canción: usdb_fetch → si baja completa (txt+media) la finaliza y la mete al NAS; si no, ia_gen.
Necesita server bgutil + USDX_YT_COOKIES/IA_COOKIES. Uso: fiesta_gen.py <cola Artist|Title>
"""
import os, sys, subprocess, shutil, unicodedata, time
kp = os.path.expanduser("~/karaoke-pipeline"); NAS = "/Volumes/documents/Ultrastar"
SK = "/Users/eloboguerrero/GitHub/skills/skills/media/karaoke-builder"
TMP = f"{kp}/fiesta_tmp"; LOG = f"{kp}/fiesta.log"
QUEUE = sys.argv[1]
def log(m): line=f"[{time.strftime('%H:%M:%S')}] {m}"; print(line,flush=True); open(LOG,"a").write(line+"\n")
def simp(s):
    s=unicodedata.normalize("NFKD",s).lower(); s="".join(c for c in s if not unicodedata.combining(c))
    return "".join(c for c in s if c.isalnum() or c==" ").strip()
EXIST=[simp(d) for d in os.listdir(NAS) if os.path.isdir(os.path.join(NAS,d))]
def have(a,t):
    k=simp(f"{a} {t}"); A,T=simp(a),simp(t)
    return any(k in e or (A and T and A in e and T in e) for e in EXIST)
def has_media(p): return any(os.path.splitext(f)[1].lower() in (".mp4",".mp3",".m4a",".webm") for f in os.listdir(p))

q=[ln.strip() for ln in open(QUEUE,encoding="utf-8") if ln.strip() and "|" in ln and not ln.startswith("#")]
log(f"===== FIESTA: {len(q)} canciones =====")
usdb=ia=skip=fail=0
for i,ln in enumerate(q,1):
    a,t=[x.strip() for x in ln.split("|",1)]
    if have(a,t): log(f"[{i}/{len(q)}] SKIP (ya está): {a} - {t}"); skip+=1; continue
    log(f"[{i}/{len(q)}] {a} - {t}")
    # 1) USDB
    shutil.rmtree(TMP,ignore_errors=True); os.makedirs(TMP)
    open(f"{TMP}/q.txt","w",encoding="utf-8").write(f"{a} - {t}\n")
    try: subprocess.run(["bash",f"{SK}/scripts/usdb_fetch.sh",f"{TMP}/q.txt",TMP,"MP4"],capture_output=True,text=True,timeout=900)
    except Exception as e: log(f"    usdb error: {e}")
    got=[d for d in os.listdir(TMP) if os.path.isdir(os.path.join(TMP,d)) and has_media(os.path.join(TMP,d))]
    if got:
        src=os.path.join(TMP,got[0])
        subprocess.run(["python3",f"{kp}/finalize.py",src,a,t],capture_output=True,text=True)
        fin=os.path.join(TMP,f"{a} - {t}"); src=fin if os.path.isdir(fin) else src
        mp4=next((f for f in os.listdir(src) if f.lower().endswith(".mp4")),None)
        if mp4: subprocess.run(["python3",f"{kp}/settags.py",src,"--MP3",mp4,"--AUDIO",mp4],capture_output=True)
        dest=os.path.join(NAS,f"{a} - {t}"); shutil.rmtree(dest,ignore_errors=True)
        subprocess.run(["cp","-R",src,dest],capture_output=True)
        v=subprocess.run(["python3",f"{kp}/validate.py",dest],capture_output=True,text=True).stdout.strip()
        if v=="PASS": log(f"    ✅ USDB [{v}]"); usdb+=1; EXIST.append(simp(f"{a} {t}")); continue
        shutil.rmtree(dest,ignore_errors=True); log(f"    USDB no validó ({v}) → IA")
    # 2) no está en USDB
    if os.getenv("FIESTA_USDB_ONLY"):
        open(f"{kp}/fiesta_misses.txt","a",encoding="utf-8").write(f"{a}|{t}\n")
        log("    → miss (para UltraStar España / IA)"); continue
    # IA fallback
    open(f"{kp}/_fiesta1.txt","w",encoding="utf-8").write(f"{a}|{t}\n")
    try:
        subprocess.run(["python3",f"{kp}/ia_gen.py",f"{kp}/_fiesta1.txt","--dest",NAS],capture_output=True,text=True,timeout=1800)
        d=os.path.join(NAS,f"{a} - {t}")
        if os.path.isdir(d): log(f"    ✅ IA"); ia+=1; EXIST.append(simp(f"{a} {t}"))
        else: log(f"    ❌ no se pudo (ni USDB ni IA)"); fail+=1
    except Exception as e: log(f"    IA error: {e}"); fail+=1
shutil.rmtree(TMP,ignore_errors=True)
log(f"===== FIN. USDB:{usdb}  IA:{ia}  skip:{skip}  fail:{fail} =====")
