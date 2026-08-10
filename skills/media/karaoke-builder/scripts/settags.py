#!/usr/bin/env python3
"""Fija/actualiza tags en un song.txt (en su lugar, sin renombrar).
Uso: settags.py "<carpeta>" --COMMENT "Cantante" --EDITION "Disney"
"""
import sys, os
folder=sys.argv[1]; args=sys.argv[2:]
kv={}; i=0
while i<len(args):
    if args[i].startswith("--"): kv[args[i][2:].upper()]=args[i+1]; i+=2
    else: i+=1
def read(p):
    raw=open(p,'rb').read()
    if raw.startswith(b'\xef\xbb\xbf'): raw=raw[3:]
    try: return raw.decode('utf-8')
    except: return raw.decode('cp1252','replace')
txts=[f for f in os.listdir(folder) if f.lower().endswith('.txt')]
if not txts: print("sin txt"); sys.exit(1)
tp=os.path.join(folder,txts[0]); lines=read(tp).splitlines()
seen=set(); out=[]
for l in lines:
    if l.startswith('#') and ':' in l:
        k=l[1:].split(':',1)[0].upper()
        if k in kv: out.append(f"#{k}:{kv[k]}"); seen.add(k); continue
    out.append(l)
# insertar los que faltan tras #TITLE
miss=[k for k in kv if k not in seen]
if miss:
    o=[]
    for l in out:
        o.append(l)
        if l.upper().startswith('#TITLE:'):
            for k in miss: o.append(f"#{k}:{kv[k]}")
    out=o
open(tp,'w',encoding='utf-8',newline='').write("\n".join(out)+"\n")
print(f"tags OK: {', '.join(kv)}")
