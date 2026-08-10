#!/usr/bin/env python3
"""Baja la letra CORRECTA con estructura de líneas/estrofas.
Primario: lyrics.ovh (keyed por artista+título → sin riesgo de canción equivocada).
Respaldo: letras.com (slug + VERIFICA que el título de la página coincida).
Uso: fetch_lyrics.py "<Artista>" "<Título>"  → imprime JSON {stanzas:[[line,...]], source}
"""
import sys, json, re, html, unicodedata, urllib.request, urllib.parse

ARTIST, TITLE = sys.argv[1], sys.argv[2]
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
def norm(s):
    s=unicodedata.normalize("NFKD",s.lower())
    s="".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]','',s)
def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA})
    return urllib.request.urlopen(req,timeout=20).read().decode("utf-8","replace")

def from_ovh(a,t):
    url=f"https://api.lyrics.ovh/v1/{urllib.parse.quote(a)}/{urllib.parse.quote(t)}"
    try: d=json.loads(get(url))
    except Exception: return None
    ly=d.get("lyrics")
    if not ly: return None
    ly=ly.replace("\r","")
    ly=re.sub(r'^.*?Paroles de la chanson.*?\n','',ly)  # a veces prefijo
    stanzas=[[l.strip() for l in bloc.split("\n") if l.strip()]
             for bloc in re.split(r'\n\s*\n', ly)]
    stanzas=[s for s in stanzas if s]
    return stanzas if stanzas else None

def from_letras(a,t):
    slug=f"{re.sub(r'[^a-z0-9]+','-',norm2(a)).strip('-')}/{re.sub(r'[^a-z0-9]+','-',norm2(t)).strip('-')}"
    try: h=get(f"https://www.letras.com/{slug}/")
    except Exception: return None
    # VERIFICAR título de la página
    mt=re.search(r'<h1[^>]*>(.*?)</h1>', h, re.S)
    page_t=re.sub(r'<[^>]+>','',mt.group(1)).strip() if mt else ""
    if norm(page_t) and norm(TITLE) not in norm(page_t) and norm(page_t) not in norm(TITLE):
        return None  # canción equivocada (ej. Heart of Glass)
    m=re.search(r'<div[^>]*class="[^"]*lyric-original[^"]*"[^>]*>(.*?)</div>', h, re.S)
    if not m: return None
    stanzas=[]
    for p in re.findall(r'<p[^>]*>(.*?)</p>', m.group(1), re.S):
        lines=[html.unescape(re.sub(r'<[^>]+>','',x)).strip() for x in re.split(r'<br\s*/?>',p)]
        lines=[l for l in lines if l]
        if lines: stanzas.append(lines)
    return stanzas or None

def norm2(s):  # para slug: conserva espacios→guiones
    s=unicodedata.normalize("NFKD",s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))

def variants(a):  # artista principal como fallback (los créditos de dueto rompen la búsqueda)
    v=[a]
    for sep in [" y ", " & ", " ft.", " ft ", " feat", " con ", ",", " x ", " + "]:
        if sep in a.lower():
            p=re.split(re.escape(sep), a, flags=re.I)[0].strip()
            if p and p not in v: v.append(p)
    return v

def from_genius(query):  # trae TILDES correctas; verifica que el título coincida (anti-basura).
    try: j=json.loads(get("https://genius.com/api/search/multi?q="+urllib.parse.quote(query)))
    except Exception: return None
    hits=[h for s in j.get("response",{}).get("sections",[]) for h in s.get("hits",[]) if h.get("type")=="song"]
    if not hits: return None
    res=hits[0]["result"]; ht=norm(res.get("title","")); nt=norm(TITLE)
    if nt and ht and nt not in ht and ht not in nt: return None      # título no coincide → basura
    try: h=get(res["url"])
    except Exception: return None
    parts=re.findall(r'<div data-lyrics-container="true"[^>]*>(.*?)</div>\s*(?=<div|$)', h, re.S)
    raw="\n".join(parts)
    raw=re.sub(r'<br\s*/?>','\n',raw); raw=re.sub(r'<[^>]+>','',raw); raw=html.unescape(raw)
    raw=re.sub(r'^.{0,300}?\bLyrics\b','',raw,count=1,flags=re.S)
    raw=re.sub(r'\[[^\]]*\]','',raw)
    JUNK=("contributor","translation","embed","you might also like","get tickets","read more","see ")
    out=[l.strip() for l in raw.split("\n") if not (l.strip() and (any(j in l.lower() for j in JUNK) or len(l.split())>=15))]
    stanzas=[]; cur=[]
    for l in out:
        if l: cur.append(l)
        elif cur: stanzas.append(cur); cur=[]
    if cur: stanzas.append(cur)
    n=sum(len(s) for s in stanzas)
    return stanzas if 6 <= n <= 120 else None                        # tope: >120 líneas = página equivocada

_ANNOT=re.compile(r'\s*\(\s*(?:bis|coro|x\s?\d+|\d+\s?x|estribillo|se\s*repite|repite|recitado|hablado|tarareo)\s*\)\s*', re.I)
def clean_stanzas(stanzas):     # quita anotaciones (bis)/(coro)/(x2) que no van en la letra
    out=[]
    for st in stanzas:
        ns=[]
        for l in st:
            l=_ANNOT.sub(' ', l); l=re.sub(r'\s{2,}',' ',l).strip(" \t-–—")
            if l and l.lower() not in ("bis","coro","estribillo"): ns.append(l)
        if ns: out.append(ns)
    return out
def accents_ok(stanzas):        # detecta letra española con las tildes borradas (lyrics.ovh)
    text=" ".join(l for st in stanzas for l in st); tl=text.lower()
    if len(text.split())<25: return True
    if len(re.findall(r'\b(que|de|la|el|los|una|con|por|mas|mi|tu|se|es|un|no)\b', tl))<4: return True
    return bool(re.search(r'[áéíóúñ]', text))

cands=[]
for a in variants(ARTIST):
    r=from_ovh(a,TITLE)
    if r: cands.append((r,"lyrics.ovh"))
    r=from_letras(a,TITLE)
    if r: cands.append((r,"letras.com"))
    if cands: break
if not any(accents_ok(r) for r,_ in cands):     # ovh/letras vino sin tildes → Genius (que sí las trae)
    for q in (f"{ARTIST} {TITLE}", TITLE):
        r=from_genius(q)
        if r: cands.append((r,"genius")); break
st=src=None
for r,s in cands:
    if accents_ok(r): st,src=r,s; break
if not st and cands: st,src=cands[0]
st=clean_stanzas(st) if st else None
if not st:
    print(json.dumps({"stanzas":[], "source":None, "error":"no encontrada"})); sys.exit(2)
print(json.dumps({"stanzas":st, "source":src, "lines":sum(len(s) for s in st)}, ensure_ascii=False))
