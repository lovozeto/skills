#!/usr/bin/env python3
"""Generador IA NUEVO (pipeline unificado):
  1) yt-dlp baja VIDEO+audio en UNA pasada (h264/mp4).
  2) demucs separa voz/instrumental (stems).
  3) carátula (iTunes) + txt stub al estándar.
  4) align_lyrics: letra verificada + alineación forzada (sílabas + melisma).
     Si no hay letra en la web → fallback UltraSinger (Whisper), marcado para 'revisar'.
  5) validate.py y mover a DEST.
Cookies anti-429 vía env IA_COOKIES. Uso: ia_gen.py <cola.txt> [--dest DIR]
"""
import sys, os, re, subprocess, unicodedata, shutil, time, glob, json
KP = "/Users/eloboguerrero/karaoke-pipeline"
PYV = os.path.expanduser("~/UltraSinger/.venv/bin/python")
UV = os.path.expanduser("~/.local/bin/uv"); USINGER = os.path.expanduser("~/UltraSinger")
QUEUE = sys.argv[1]
DEST = sys.argv[sys.argv.index("--dest")+1] if "--dest" in sys.argv else \
       "/Users/eloboguerrero/Downloads/Karaoke-Vallenatos"
WORK = f"{KP}/ia_work"; os.makedirs(WORK, exist_ok=True); os.makedirs(DEST, exist_ok=True)
COOKIES = os.environ.get("IA_COOKIES", "").split()
LOG = f"{KP}/ia_gen.log"
def log(m): line=f"[{time.strftime('%H:%M:%S')}] {m}"; print(line,flush=True); open(LOG,"a").write(line+"\n")
def simp(s):
    s=unicodedata.normalize("NFC",s).lower().strip(); s=re.sub(r"\(.*?\)|\[.*?\]","",s)
    return re.sub(r"\s+"," ",re.sub(r"[^a-z0-9áéíóúñü ]","",s)).strip()
EXIST=[simp(d) for d in os.listdir(DEST) if os.path.isdir(os.path.join(DEST,d))]
def have(a,t):
    k=simp(f"{a} {t}"); A,T=simp(a),simp(t)
    return any(k in e or (A and T and A in e and T in e) for e in EXIST)

BAD=("karaoke","cover","instrumental","lyric","letra","live","en vivo","remix","sped up","8d","nightcore","reaction")
def pick_source(a,t):
    try:
        out=subprocess.run(["yt-dlp","--no-warnings",*COOKIES,"--flat-playlist","--print",
            "%(id)s\t%(duration)s\t%(channel)s\t%(title)s",f"ytsearch6:{a} {t} official video"],
            capture_output=True,text=True,timeout=120).stdout.strip().splitlines()
    except Exception as e: log(f"    search fail: {e}"); return None
    best=None; bs=-1
    for ln in out:
        p=ln.split("\t",3)
        if len(p)<4: continue
        vid=p[0]
        try: d=float(p[1])
        except: d=0
        ch,ti=p[2].lower(),p[3].lower()
        if d<60 or d>600 or any(b in ti for b in BAD): continue
        s=0
        if a.lower() in ch or "vevo" in ch or "official" in ch: s+=3
        if "official" in ti: s+=1
        if t.lower() in ti: s+=1
        if s>bs: bs=s; best=vid
    return best

def detect_lang(text):
    tl=text.lower()
    es=len(re.findall(r"[ñáéíóú¿¡]",tl))+len(re.findall(r"\b(que|de|la|el|los|una|con|por|para|te|se|es|mi|tu)\b",tl))
    en=len(re.findall(r"\b(the|you|and|to|of|it|is|my|me|in|that|your|for|with)\b",tl))
    return "es" if es>=en else "en"

def run(cmd,timeout):
    return subprocess.run(cmd,capture_output=True,text=True,timeout=timeout)

def demucs_stems(audio, base, folder):
    out=f"{WORK}/demucs"; shutil.rmtree(out,ignore_errors=True)
    r=run([PYV,"-m","demucs","--two-stems=vocals","-n","htdemucs","--out",out,audio],1800)
    stem_dir=f"{out}/htdemucs/"+os.path.splitext(os.path.basename(audio))[0]
    voc=f"{stem_dir}/vocals.wav"; ins=f"{stem_dir}/no_vocals.wav"
    if not os.path.exists(voc): return None,None
    vpath=os.path.join(folder,f"{base} [Vocals].m4a"); ipath=os.path.join(folder,f"{base} [Instrumental].m4a")
    run(["ffmpeg","-y","-i",voc,"-c:a","aac","-b:a","192k",vpath],300)
    run(["ffmpeg","-y","-i",ins,"-c:a","aac","-b:a","192k",ipath],300)
    return (os.path.basename(vpath) if os.path.exists(vpath) else None,
            os.path.basename(ipath) if os.path.exists(ipath) else None)

def generate(a,t):
    base=f"{a} - {t}"; base=re.sub(r'[/\\:*?"<>|]',"",base)
    folder=os.path.join(WORK,base); shutil.rmtree(folder,ignore_errors=True); os.makedirs(folder)
    vid=pick_source(a,t)
    if not vid: return "no-source"
    # 1) video+audio en una pasada
    mp4=os.path.join(folder,f"{base}.mp4")
    r=run(["yt-dlp","--no-warnings","--remote-components","ejs:github",*COOKIES,"--sleep-requests","2",
        "-f","bv*[vcodec^=avc1][height<=1080][ext=mp4]+ba[ext=m4a]/b[ext=mp4]/b",
        "--merge-output-format","mp4","-o",mp4,f"https://youtu.be/{vid}"],900)
    if not os.path.exists(mp4): return f"dl-fail"
    # audio principal
    audio=os.path.join(folder,f"{base}.m4a")
    run(["ffmpeg","-y","-i",mp4,"-vn","-c:a","aac","-b:a","256k",audio],300)
    # 2) stems
    voc_f,ins_f=demucs_stems(audio,base,folder)
    if not voc_f: return "demucs-fail"
    # 3) carátula
    subprocess.run(["python3",f"{KP}/add_cover.py",folder,a,t],capture_output=True,text=True,timeout=60)
    co=next((f for f in os.listdir(folder) if "[CO]" in f),None)
    # 4) letra + idioma
    try:
        j=json.loads(subprocess.run(["python3",f"{KP}/fetch_lyrics.py",a,t],capture_output=True,text=True,timeout=40).stdout)
        lyr=" ".join(l for st in j.get("stanzas",[]) for l in st)
    except Exception: lyr=""
    # stub txt (align_lyrics lee estos tags)
    stub=[f"#VERSION:1.1.0",f"#TITLE:{t}",f"#ARTIST:{a}"]
    if lyr: stub.append(f"#LANGUAGE:{'Spanish' if detect_lang(lyr)=='es' else 'English'}")
    stub+= [f"#MP3:{base}.m4a",f"#AUDIO:{base}.m4a",f"#VIDEO:{base}.mp4",f"#VOCALS:{voc_f}"]
    if ins_f: stub.append(f"#INSTRUMENTAL:{ins_f}")
    if co: stub.append(f"#COVER:{co}")
    stub+=["#BPM:300","#GAP:0","E"]
    open(os.path.join(folder,f"{base}.txt"),"w",encoding="utf-8",newline="\n").write("\n".join(stub)+"\n")
    # 5) timing
    flag=""
    if lyr:
        lang=detect_lang(lyr)
        r=run([PYV,f"{KP}/align_lyrics.py",folder,lang],1200)
        outl=(r.stdout or "").strip().splitlines()
        msg=outl[-1] if outl else ""
        if "OK align_lyrics" not in msg:            # fallback si el calce falló
            flag="align-flag"; _ultrasinger(folder,a,t,mp4)
    else:
        flag="no-web-lyrics"; _ultrasinger(folder,a,t,mp4)
    # 6) validar + mover
    v=subprocess.run(["python3",f"{KP}/validate.py",folder],capture_output=True,text=True).stdout.strip()
    dest=os.path.join(DEST,base)
    if os.path.exists(dest): shutil.rmtree(dest,ignore_errors=True)
    shutil.move(folder,dest)
    return f"OK ({'align_lyrics' if not flag else flag}) [{v}]"

def _ultrasinger(folder,a,t,mp4):
    """Fallback: UltraSinger (Whisper) para las sin letra en la web. Marca para revisar."""
    out=f"{WORK}/us_out"; shutil.rmtree(out,ignore_errors=True)
    subprocess.run([UV,"run","python","src/UltraSinger.py","-i",mp4,"-o",out,
        "--force_cpu","--whisper","large-v3"],cwd=USINGER,capture_output=True,text=True,timeout=2400)
    # copiar el txt de UltraSinger si salió (mejor esfuerzo) y marcar revisar
    open(f"{KP}/revisar.txt","a").write(f"{a} - {t}\tsin-letra-web (fallback Whisper)\n")

if __name__=="__main__":
    q=[ln.strip() for ln in open(QUEUE,encoding="utf-8") if ln.strip() and "|" in ln and not ln.startswith("#")]
    log(f"=== ia_gen: {len(q)} en cola → {DEST} ===")
    for i,ln in enumerate(q,1):
        a,t=[x.strip() for x in ln.split("|",1)]
        if have(a,t): log(f"[{i}/{len(q)}] SKIP (existe): {a} - {t}"); continue
        log(f"[{i}/{len(q)}] {a} - {t}")
        try: r=generate(a,t); log(f"    {r}"); EXIST.append(simp(f"{a} {t}"))
        except Exception as e: log(f"    ERROR {e}")
