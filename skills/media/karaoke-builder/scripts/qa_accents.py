#!/usr/bin/env python3
"""Encuentra las IA afectadas por (a) tildes/ñ borradas (letra española sin acentos) o
(b) anotaciones '(bis)/(coro)/(x2)' metidas como letra, y las RE-ALINEA con el fetch_lyrics
corregido. Respalda cada txt. Uso: qa_accents.py [--scan]   (--scan solo cuenta, no procesa)
"""
import os, re, subprocess, shutil, time, sys
NAS="/Volumes/documents/Ultrastar"; KP="/Users/eloboguerrero/karaoke-pipeline"
PYV=os.path.expanduser("~/UltraSinger/.venv/bin/python")
BK=KP+"/qa_accents_backups"; LOG=KP+"/qa_accents.log"; os.makedirs(BK,exist_ok=True)
SCAN="--scan" in sys.argv
def read(p):
    r=open(p,'rb').read()
    if r.startswith(b'\xef\xbb\xbf'): r=r[3:]
    try: return r.decode('utf-8')
    except: return r.decode('cp1252','replace')
def log(m): line=f"[{time.strftime('%H:%M:%S')}] {m}"; print(line,flush=True); open(LOG,"a").write(line+"\n")
def note_text(c):
    out=[]
    for l in c.splitlines():
        if l[:1] in ':*FRG':
            p=l.split(' ',4)
            if len(p)>=5: out.append(p[4])
    return " ".join(out).replace('~',' ')
def affected(c):
    txt=note_text(c); tl=txt.lower()
    if re.search(r'\(\s*(bis|coro|x\s?\d|\d\s?x|estribillo)', tl): return "bis"
    if len(txt.split())<25: return None
    es=len(re.findall(r'\b(que|de|la|el|los|las|una|con|por|para|mas|mi|tu|se|es|un|yo|te|su|como|pero|sin|muy)\b', tl))
    en=len(re.findall(r'\b(the|you|and|to|of|it|is|my|me|in|that|your|for|with|not|i|we|are|be|this|on)\b', tl))
    if es>=6 and es>en*1.3 and not re.search(r'[áéíóúñ]', txt): return "sin-tildes"   # español real sin tildes
    return None

targets=[]
for d in sorted(os.listdir(NAS)):
    p=os.path.join(NAS,d)
    if not os.path.isdir(p) or d.startswith('.'): continue
    files=[f for f in os.listdir(p) if not f.startswith('.')]
    if not any('[Vocals]' in f for f in files): continue           # solo IA con stem
    txts=[f for f in files if f.lower().endswith('.txt')]
    if not txts: continue
    tp=os.path.join(p,txts[0]); c=read(tp); why=affected(c)
    if why: targets.append((d,p,tp,why))
nb=sum(1 for t in targets if t[3]=="bis"); nt=sum(1 for t in targets if t[3]=="sin-tildes")
log(f"===== AFECTADAS: {len(targets)}  (sin-tildes:{nt}  bis:{nb}) =====")
if SCAN:
    for d,_,_,why in targets[:40]: log(f"   [{why}] {d}")
    sys.exit(0)
ok=flag=0
for i,(d,p,tp,why) in enumerate(targets,1):
    log(f"[{i}/{len(targets)}] ({why}) {d}")
    shutil.copy2(tp, os.path.join(BK,d+".txt"))
    try:
        r=subprocess.run([PYV,f"{KP}/align_lyrics.py",p],capture_output=True,text=True,timeout=1200)
        msg=(r.stdout or "").strip().splitlines()[-1:] or [(r.stderr or "?")[-80:]]
        if r.returncode==0 and "OK align_lyrics" in (msg[0] if msg else ""): log(f"    OK {msg[0]}"); ok+=1
        else: log(f"    FLAG {msg[0] if msg else ''}"); flag+=1
    except Exception as e: log(f"    ERROR {e}"); flag+=1
log(f"===== FIN. re-alineadas:{ok} flag:{flag} (respaldos en {BK}) =====")
