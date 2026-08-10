#!/usr/bin/env python3
"""Agrega/corrige carátula vía iTunes Search API.
Uso: add_cover.py "<carpeta>" "<Artista>" "<Título>"
"""
import sys, os, json, urllib.request, urllib.parse, re, unicodedata

folder, ARTIST, TITLE = sys.argv[1], sys.argv[2], sys.argv[3]
base = os.path.basename(folder.rstrip("/"))

def clean(s):
    s=unicodedata.normalize("NFKD", s.lower())
    s="".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9 ]','',s).strip()

term = urllib.parse.quote(f"{ARTIST} {TITLE}")
url = f"https://itunes.apple.com/search?term={term}&entity=song&limit=15"
try:
    data = json.load(urllib.request.urlopen(url, timeout=20))
except Exception as e:
    print(f"iTunes fail: {e}"); sys.exit(1)

res = data.get("results", [])
def score(r):
    a=clean(r.get("artistName","")); t=clean(r.get("trackName",""))
    s=0
    if clean(ARTIST) in a or a in clean(ARTIST): s+=3
    if clean(TITLE)==t: s+=3
    elif clean(TITLE) in t or t in clean(TITLE): s+=1
    return s
res=[r for r in res if r.get("artworkUrl100")]
# EXIGIR que el artista coincida (evita canciones homónimas de otros artistas)
am=[r for r in res if clean(ARTIST) in clean(r.get("artistName","")) or clean(r.get("artistName","")) in clean(ARTIST)]
res = am or res
if not res: print("sin resultados con arte"); sys.exit(2)
res.sort(key=score, reverse=True)
best=res[0]
if not (clean(ARTIST) in clean(best.get("artistName","")) or clean(best.get("artistName","")) in clean(ARTIST)):
    print(f"artista no coincide ({best.get('artistName')}) -> no piso"); sys.exit(3)
if score(best)<3:
    print(f"match dudoso ({best.get('artistName')} - {best.get('trackName')}) -> no piso"); sys.exit(3)
art=best["artworkUrl100"].replace("100x100bb","600x600bb")
cover=os.path.join(folder, f"{base} [CO].jpg")
try:
    urllib.request.urlretrieve(art, cover)
except Exception as e:
    print(f"download fail: {e}"); sys.exit(4)

# agregar/actualizar #COVER en el txt
txts=[f for f in os.listdir(folder) if f.lower().endswith(".txt")]
if txts:
    tp=os.path.join(folder,txts[0]); lines=open(tp,encoding="utf-8").read().splitlines()
    covname=f"{base} [CO].jpg"; done=False; out=[]
    for l in lines:
        if l.upper().startswith("#COVER:"): out.append(f"#COVER:{covname}"); done=True
        else: out.append(l)
    if not done:
        out2=[]
        for l in out:
            out2.append(l)
            if l.upper().startswith("#TITLE:"): out2.append(f"#COVER:{covname}")
        out=out2
    open(tp,"w",encoding="utf-8",newline="").write("\n".join(out)+"\n")
print(f"OK cover: {best.get('artistName')} - {best.get('trackName')} [{best.get('collectionName')}]")
