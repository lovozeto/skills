#!/usr/bin/env python3
"""Agrega video de fondo (MV oficial, sin letras quemadas) vía yt-dlp, H.264/MP4.
Uso: add_video.py "<carpeta>" "<Artista>" "<Título>"
"""
import sys, os, subprocess, re, unicodedata

folder, ARTIST, TITLE = sys.argv[1], sys.argv[2], sys.argv[3]
base = os.path.basename(folder.rstrip("/"))
BAD=("karaoke","lyric","letra","cover","instrumental","reaction","sub español","subtitulado","1 hour","hora","loop",
     "live","en vivo","en concierto","in concert","concert","directo","vivo","awards","premios","grammy","billboard",
     "oscar","american music","world music","performance","tribute","homenaje","medley","remix","acoustic","acústico",
     "session","sesión","behind the","making of","interview","entrevista")

def pick():
    q=f"ytsearch8:{ARTIST} {TITLE} official video"
    out=subprocess.run(["yt-dlp","--no-warnings","--flat-playlist","--print",
        "%(id)s\t%(duration)s\t%(channel)s\t%(title)s",q],capture_output=True,text=True,timeout=120).stdout.strip().splitlines()
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
        if ARTIST.lower() in ch or "vevo" in ch or "official" in ch: s+=3
        if "official" in ti and "video" in ti: s+=2
        if TITLE.lower() in ti: s+=1
        if s>bs: bs=s; best=vid
    return best

vid=pick()
if not vid: print(f"SIN VIDEO: {ARTIST} - {TITLE}"); sys.exit(2)
out=os.path.join(folder, f"{base}.mp4")
r=subprocess.run(["yt-dlp","--no-warnings","--sleep-requests","2",
    "-f","bv*[vcodec^=avc1][height<=1080][ext=mp4]+ba[ext=m4a]/b[ext=mp4]/b",
    "--merge-output-format","mp4","-o",out,f"https://youtu.be/{vid}"],capture_output=True,text=True,timeout=420)
if r.returncode!=0 or not os.path.exists(out):
    err=(r.stderr or r.stdout or "").strip().splitlines()
    print(f"DL FAIL {ARTIST}-{TITLE}: {err[-1] if err else '?'}"); sys.exit(3)
# tag #VIDEO
txts=[f for f in os.listdir(folder) if f.lower().endswith(".txt")]
tp=os.path.join(folder,txts[0]); lines=open(tp,encoding="utf-8").read().splitlines()
vname=f"{base}.mp4"; done=False; o=[]
for l in lines:
    if l.upper().startswith("#VIDEO:"): o.append(f"#VIDEO:{vname}"); done=True
    else: o.append(l)
if not done:
    o2=[]
    for l in o:
        o2.append(l)
        if l.upper().startswith("#COVER:") or (not any(x.upper().startswith('#COVER:') for x in o) and l.upper().startswith('#TITLE:')):
            o2.append(f"#VIDEO:{vname}")
    o=o2
open(tp,"w",encoding="utf-8",newline="").write("\n".join(o)+"\n")
print(f"OK video [{vid}]: {ARTIST} - {TITLE}")
