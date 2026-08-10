#!/usr/bin/env python3
"""MATCHER de ultrastar-es.org (la búsqueda es pública). Por cada 'Artista|Título'
busca en el sitio y elige el resultado correcto (match exacto de artista+título,
penalizando variantes tipo 'again'/remix/live). Devuelve el TOKEN del .torrent.
La descarga autenticada la hace el navegador (bridge); esto solo resuelve tokens.

Uso: site_match.py <lista.txt>   → escribe site_hits.txt (Artista|Título|token|encontrado)
                                    y site_miss.txt (los que no están → IA)
     site_match.py "Artista" "Título"   → prueba una sola (imprime candidatos)
"""
import sys, re, html, unicodedata, urllib.request, urllib.parse, time
KP = "/Users/eloboguerrero/karaoke-pipeline"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15) AppleWebKit/537.36 Chrome/124 Safari/537.36"
BAD = ("again", "remix", "karaoke", "cover", "live", "en vivo", "acoustic", "instrumental",
       "version", "versión", "sped", "8d", "nightcore", "reggaeton version")

def norm(s):
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", s)).strip()

def search(query):
    url = "https://ultrastar-es.org/en/canciones?busqueda=" + urllib.parse.quote(query)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    h = urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "replace")
    cands = []
    for m in re.finditer(r'title="Download torrent of (.*?)"\s+href="(/en/canciones/descargar/torrent/[^"]+)"', h):
        disp = html.unescape(m.group(1)); token = m.group(2).rsplit("/", 1)[-1]
        if " - " in disp:
            a, t = disp.split(" - ", 1); cands.append((a.strip(), t.strip(), token))
    return cands

def pick(artist, title, cands):
    na, nt = norm(artist), norm(title)
    best = None; bs = -1
    for a, t, tok in cands:
        ca, ct = norm(a), norm(t)
        s = 0
        if ca == na: s += 5
        elif na in ca or ca in na: s += 2
        if ct == nt: s += 5
        elif nt in ct or ct in nt: s += 2
        if any(b in ct and b not in nt for b in BAD): s -= 4      # penaliza variantes
        s -= 0.1 * abs(len(ct) - len(nt))                          # prefiere título más parecido
        if s > bs: bs = s; best = (a, t, tok)
    # exige calce sólido de ambos campos
    if best and bs >= 7: return best, bs
    return None, bs

def resolve(artist, title):
    for q in (f"{artist} {title}", title):
        try: cands = search(q)
        except Exception: cands = []
        if cands:
            best, sc = pick(artist, title, cands)
            if best: return best, sc
        time.sleep(0.4)
    return None, -1

if len(sys.argv) == 3:   # prueba de una sola
    a, t = sys.argv[1], sys.argv[2]
    cands = search(f"{a} {t}") or search(t)
    print(f"{len(cands)} candidatos; top 8:")
    for c in cands[:8]: print("   ", c[0], "—", c[1], "  ", c[2][:14])
    best, sc = resolve(a, t)
    print("ELEGIDO:", best, "score", sc)
    sys.exit(0)

LIST = sys.argv[1]
hits = []; miss = []
for ln in open(LIST, encoding="utf-8"):
    ln = ln.strip()
    if not ln or "|" not in ln: continue
    a, t = ln.split("|", 1); a, t = a.strip(), t.strip()
    best, sc = resolve(a, t)
    if best: hits.append((a, t, best[2], f"{best[0]} - {best[1]}")); print(f"HIT  {a} - {t}  → {best[0]} - {best[1]}")
    else:    miss.append((a, t)); print(f"MISS {a} - {t}  → IA")
    time.sleep(0.3)
open(f"{KP}/site_hits.txt", "w", encoding="utf-8").write("\n".join(f"{a}|{t}|{tok}|{nm}" for a, t, tok, nm in hits) + ("\n" if hits else ""))
open(f"{KP}/site_miss.txt", "w", encoding="utf-8").write("\n".join(f"{a}|{t}" for a, t in miss) + ("\n" if miss else ""))
print(f"\n=== {len(hits)} en el sitio (torrent) | {len(miss)} a IA ===")
