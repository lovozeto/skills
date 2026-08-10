#!/usr/bin/env python3
"""Núcleo del pipeline nuevo: TIMING desde la LETRA VERIFICADA por alineación forzada.
A diferencia del viejo retime (que alineaba las palabras ya escritas, mal transcritas),
este le da a whisperX la letra CORRECTA de la web y solo calcula cuándo se canta cada
palabra → palabras correctas + timing en un paso. Sirve igual para regenerar IA ya bajadas
(usa el stem [Vocals] que ya existe, sin volver a descargar).

Uso: align_lyrics.py "<carpeta>" [lang]
Salida: escribe song.txt al estándar y sale 0 si el calce es bueno.
        sale 3 (FLAG) si no hay letra en la web o el calce es malo (→ lista 'revisar').
"""
import sys, os, re, json, math, subprocess, unicodedata, warnings
warnings.filterwarnings("ignore")
import numpy as np, librosa
KP = "/Users/eloboguerrero/karaoke-pipeline"
FOLDER = sys.argv[1].rstrip("/")
LANG = sys.argv[2] if len(sys.argv) > 2 else "es"
base = os.path.basename(FOLDER)

def read(p):
    raw = open(p, "rb").read()
    if raw.startswith(b"\xef\xbb\xbf"): raw = raw[3:]
    try: return raw.decode("utf-8")
    except: return raw.decode("cp1252", "replace")

def nw(w):
    w = unicodedata.normalize("NFKD", w.lower())
    w = "".join(c for c in w if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", w)

# --- silabación (para 1 nota por sílaba, como los karaokes hechos por humanos) ---
try:
    from hyphen import Hyphenator
    _HY = Hyphenator({"es":"es_ES","en":"en_US","de":"de_DE","fr":"fr_FR","it":"it_IT","pt":"pt_PT"}.get(LANG,"en_US"))
except Exception:
    _HY = None
def syllabify(word):
    m = re.match(r"^([^0-9A-Za-zÀ-ÿ]*)(.*?)([^0-9A-Za-zÀ-ÿ]*)$", word)
    pre, core, suf = m.group(1), m.group(2), m.group(3)
    parts = None
    if _HY and len(core) >= 4:
        try: parts = _HY.syllables(core)
        except Exception: parts = None
    if not parts: parts = [core] if core else [word]
    parts = list(parts); parts[0] = pre+parts[0]; parts[-1] = parts[-1]+suf
    return parts

def detect_lang(text):
    tl = text.lower(); sc = {}
    sc["es"] = 2*len(re.findall(r"[ñ¿¡]", tl)) + len(re.findall(r"[áéíóú]", tl)) + len(re.findall(r"\b(que|de|la|el|los|una|con|por|para|te|se|es|mi|tu|no|yo|un|su)\b", tl))
    sc["en"] = len(re.findall(r"\b(the|you|and|to|of|it|is|my|me|in|that|your|for|with|not|i|we|are)\b", tl))
    sc["de"] = 2*len(re.findall(r"[äöüß]", tl)) + len(re.findall(r"\b(der|die|das|und|ich|du|ist|nicht|ein|zu|wir|mir|dich|jetzt|los|mehr|sein|auf|mich|wie|noch)\b", tl))
    sc["fr"] = 2*len(re.findall(r"[àâçèêëîïôûù]", tl)) + len(re.findall(r"\b(le|les|je|tu|et|est|pas|une|dans|plus|qui|des|mon|ma|ne|pour|vais|c'est|je|libérée|délivrée)\b", tl))
    return max(sc, key=sc.get)

# --- leer txt + tags ---
txts = [f for f in os.listdir(FOLDER) if f.lower().endswith(".txt") and not f.startswith("._")]
if not txts: print("FLAG:no-txt"); sys.exit(3)
txtpath = os.path.join(FOLDER, txts[0])
content = read(txtpath); tags = {}
for l in content.splitlines():
    m = re.match(r"#([A-Z0-9]+):(.*)", l)
    if m: tags[m.group(1)] = m.group(2)

FILES = [f for f in os.listdir(FOLDER) if not f.startswith("._") and not f.startswith(".")]
voc = next((f for f in FILES if "[Vocals]" in f), None)
if not voc: print("FLAG:no-vocals-stem"); sys.exit(3)
vocpath = os.path.join(FOLDER, voc)

# --- letra verificada de la web ---
try:
    j = json.loads(subprocess.run(["python3", f"{KP}/fetch_lyrics.py",
        tags.get("ARTIST",""), tags.get("TITLE","")],
        capture_output=True, text=True, timeout=40).stdout)
    stanzas = j.get("stanzas", []); lyr_src = j.get("source")
except Exception:
    stanzas = []; lyr_src = None
lines = [ln.split() for st in stanzas for ln in st if ln.split()]
if not lines: print("FLAG:no-lyrics"); sys.exit(3)
canon = [w for ln in lines for w in ln]           # palabras planas (en orden)
line_of = []                                       # índice de línea por palabra
for li, ln in enumerate(lines):
    line_of += [li]*len(ln)
full = " ".join(canon)
# autodetectar idioma desde la letra (ignora #LANGUAGE mal puesto → modelo correcto)
_det = detect_lang(full)
if _det and _det != LANG:
    LANG = _det
    try:
        from hyphen import Hyphenator
        _HY = Hyphenator({"es":"es_ES","en":"en_US","de":"de_DE","fr":"fr_FR","it":"it_IT","pt":"pt_PT"}.get(LANG, "en_US"))
    except Exception: pass

# --- alineación forzada (letra → voz) ---
import whisperx
dev = "cpu"; audio = whisperx.load_audio(vocpath); sr = 16000; dur = len(audio)/sr
rms = librosa.feature.rms(y=audio, frame_length=2048, hop_length=512)[0]
thr = max(rms)*0.06; fr = np.where(rms > thr)[0]
vstart = max(0.0, (fr[0]*512/sr)-0.15) if len(fr) else 0.0
vend = min(dur, (fr[-1]*512/sr)+0.3) if len(fr) else dur
ma, meta = whisperx.load_align_model(language_code=LANG, device=dev)
res = whisperx.align([{"start": float(vstart), "end": float(vend), "text": full}],
                     ma, meta, audio, dev, return_char_alignments=False)
AW = [w for s in res["segments"] for w in s.get("words", [])]
if not AW: print("FLAG:align-empty"); sys.exit(3)

# --- mapear palabras alineadas ↔ palabras canónicas (dos punteros por texto normalizado) ---
timed = [None]*len(canon)   # (start,end) por palabra canónica
i = j2 = 0
while i < len(canon) and j2 < len(AW):
    cw = nw(canon[i]); aw = nw(AW[j2].get("word",""))
    if not aw: j2 += 1; continue
    if cw == aw or cw.startswith(aw) or aw.startswith(cw):
        s, e = AW[j2].get("start"), AW[j2].get("end")
        if s is not None: timed[i] = (float(s), float(e if e is not None else s+0.2))
        i += 1; j2 += 1
    else:
        j2 += 1   # descartar palabra alineada que no calza; avanzar
# interpolar huecos (palabras sin timing) entre vecinos con timing
known = [k for k in range(len(canon)) if timed[k]]
if len(known) < max(4, 0.5*len(canon)):
    print(f"FLAG:bad-align cov={len(known)/max(1,len(canon)):.2f} src={lyr_src}"); sys.exit(3)
for k in range(len(canon)):
    if timed[k]: continue
    lo = max([x for x in known if x < k], default=None)
    hi = min([x for x in known if x > k], default=None)
    if lo is not None and hi is not None:
        (ls,le),(hs,he) = timed[lo], timed[hi]
        span = hs-le; step = span/max(1,(hi-lo))
        pos = k-lo; s = le+step*(pos-0.5); timed[k] = (max(le,s), max(le,s)+min(0.35,step*0.8))
    elif lo is not None:
        ls,le = timed[lo]; timed[k] = (le+0.05*(k-lo), le+0.05*(k-lo)+0.2)
    elif hi is not None:
        hs,he = timed[hi]; timed[k] = (max(0,hs-0.05*(hi-k)-0.2), max(0.05,hs-0.05*(hi-k)))

# --- pitch (pyin) ---
y, _ = librosa.load(vocpath, sr=22050, mono=True)
f0, _, _ = librosa.pyin(y, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C6"),
                        sr=22050, frame_length=2048)
tf0 = librosa.times_like(f0, sr=22050, hop_length=512)
def midi_at(t0, t1):
    m = (tf0 >= t0) & (tf0 <= max(t1, t0+0.04)); ff = f0[m]; ff = ff[~np.isnan(ff)]
    return int(round(69+12*math.log2(np.median(ff)/440.0))) if len(ff) else None

BPM = float(str(tags.get("BPM", "300")).replace(",", "."))
mspb = 15000.0/BPM
GAPms = round(timed[known[0]][0]*1000)
def beat(t): return int(round((t*1000-GAPms)/mspb))

def pitch_runs(t0, t1, prev):
    """Tono estable de la sílaba. Solo parte en melisma ('~') si un tono nuevo se SOSTIENE
    >=0.15s (evita el temblor de pyin). Sílabas cortas = una sola nota."""
    m = (tf0 >= t0) & (tf0 <= max(t1, t0+0.04)); ts = list(tf0[m]); fs = list(f0[m])
    seq = [(float(tt), 69+12*math.log2(ff/440.0)) for tt, ff in zip(ts, fs) if not np.isnan(ff)]
    if not seq: return [(t0, max(t1, t0+0.05), prev)]
    tvec = [t for t, _ in seq]
    # suavizado por mediana móvil (mata glitches de octava de 1 frame)
    raw = [p for _, p in seq]
    sm = [int(round(np.median(raw[max(0, i-3):i+4]))) for i in range(len(raw))]
    med = int(round(np.median(sm)))
    def fold(v):                                     # pliega octavas hacia la mediana
        while v-med >= 7: v -= 12
        while med-v >= 7: v += 12
        return v
    if (t1-t0) < 0.5:                                # sílaba corta → una nota
        return [(t0, max(t1, tvec[-1]), fold(med))]
    runs = []; seg_lvl = sm[0]; seg_start = tvec[0]; k = 1
    while k < len(sm):
        if abs(sm[k]-seg_lvl) >= 4:                  # salto real (melisma), no temblor
            lvl = sm[k]; kk = k
            while kk < len(sm) and abs(sm[kk]-lvl) < 4: kk += 1
            if tvec[min(kk, len(tvec)-1)] - tvec[k] >= 0.25:   # y se sostiene
                runs.append((seg_start, tvec[k], fold(seg_lvl)))
                seg_lvl = lvl; seg_start = tvec[k]; k = kk; continue
        k += 1
    runs.append((seg_start, max(t1, tvec[-1]), fold(seg_lvl)))
    if len(runs) > 4:                                # tope: máx 4 notas por sílaba (1 + 3 '~')
        runs = runs[:3] + [(runs[3][0], runs[-1][1], runs[3][2])]
    return runs

notes = []; prev = 60; cur_line = line_of[0]
for k in range(len(canon)):
    ws, we = timed[k]
    if line_of[k] != cur_line:                      # salto de línea real
        notes.append(("break", beat(ws)-1)); cur_line = line_of[k]
    sylls = syllabify(canon[k])
    lens = [max(1, len(re.sub(r"\W", "", s))) for s in sylls]; tot = sum(lens) or 1
    acc = ws
    for si, syl in enumerate(sylls):                # repartir el tiempo de la palabra por sílaba
        se = acc + (we-ws)*lens[si]/tot; ss = acc; acc = se
        runs = pitch_runs(ss, se, prev)
        for ri, (r0, r1, rm) in enumerate(runs):
            b0 = beat(r0); L = max(1, beat(r1)-b0); prev = rm or prev
            last = (si == len(sylls)-1 and ri == len(runs)-1)
            txt = (syl if ri == 0 else "~") + (" " if last else "")
            notes.append(("note", b0, L, prev, txt))

# --- media tags desde archivos reales (estándar) ---
def find(*suf):
    for f in FILES:
        if all(x in f for x in suf) and not f.lower().endswith(".txt"): return f
    return None
main_audio = next((f for f in FILES
    if f.lower().endswith((".mp3",".m4a",".ogg",".opus")) and "[" not in f), None)
media = {}
if main_audio: media["MP3"] = main_audio; media["AUDIO"] = main_audio
voc_f = find("[Vocals]");    media["VOCALS"] = voc_f if voc_f else None
ins_f = find("[Instrumental]"); media["INSTRUMENTAL"] = ins_f if ins_f else None
vid_f = next((f for f in FILES if f.lower().endswith((".mp4",".webm",".avi"))), None)
if vid_f: media["VIDEO"] = vid_f
co_f = find("[CO]");  media["COVER"] = co_f if co_f else None
bg_f = find("[BG]");  media["BACKGROUND"] = bg_f if bg_f else None

out = ["#VERSION:1.1.0"]
for k in ["TITLE","ARTIST","LANGUAGE","GENRE","YEAR","EDITION","CREATOR"]:
    if tags.get(k): out.append(f"#{k}:{tags[k]}")
for k in ["MP3","AUDIO","VOCALS","INSTRUMENTAL","VIDEO","COVER","BACKGROUND"]:
    if media.get(k): out.append(f"#{k}:{media[k]}")
out.append(f"#BPM:{tags.get('BPM', str(BPM))}")
out.append(f"#GAP:{GAPms}")
out.append(f"#COMMENT:{tags.get('COMMENT','')}" if tags.get("COMMENT") else "#COMMENT:align_lyrics")
for nt in notes:
    out.append(f": {nt[1]} {nt[2]} {nt[3]} {nt[4]}" if nt[0]=="note" else f"- {nt[1]}")
out.append("E")
open(txtpath, "w", encoding="utf-8", newline="\n").write("\n".join(out)+"\n")
cov = len(known)/max(1,len(canon))
print(f"OK align_lyrics: {len(canon)} palabras, {len(lines)} líneas | letra:{lyr_src} cov:{cov:.2f} | #GAP {GAPms}ms")
