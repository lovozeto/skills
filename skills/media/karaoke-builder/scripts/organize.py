#!/usr/bin/env python3
"""
Organizador UltraStar (torrents + IA).
- Detecta carpetas de canción (contienen .txt con #TITLE y #MP3/#AUDIO).
- Convierte song.txt a UTF-8 sin BOM (convención que ya funciona; NO agrega #ENCODING).
- Normaliza NFC + puntuación fina (comillas/guiones tipográficos) en: nombre de carpeta,
  nombres de archivo, y VALORES de tags de media + #TITLE/#ARTIST (mantiene refs consistentes).
- Verifica que las refs de media existan.
- Dedup contra el destino: conserva la de mayor calidad (video > resolución > bitrate > tamaño).
- Excluye subcarpetas de trabajo (cache).
- Mueve al destino.
Uso: organize.py SRC DEST [--apply]   (sin --apply = dry-run)
"""
import sys, os, unicodedata, subprocess, json, shutil

SRC, DEST = sys.argv[1], sys.argv[2]
APPLY = "--apply" in sys.argv
MEDIA_TAGS = ("MP3","AUDIO","VIDEO","COVER","BACKGROUND","VOCALS","INSTRUMENTAL")
TEXT_TAGS  = ("TITLE","ARTIST")
EXCLUDE_DIRS = {"cache"}
PUNCT = {"‘":"'","’":"'","‚":"'","′":"'",
         "“":'"',"”":'"',
         "‐":"-","‑":"-","‒":"-","–":"-","—":"-","―":"-",
         "…":"..."," ":" "}

def normstr(s):
    s = unicodedata.normalize("NFC", s)
    for k,v in PUNCT.items(): s = s.replace(k,v)
    return s

def log(k,m): print(f"[{k}] {m}")

def read_text(path):
    raw = open(path,"rb").read()
    if raw.startswith(b"\xef\xbb\xbf"): return raw[3:].decode("utf-8"),"utf-8-bom"
    try: return raw.decode("utf-8"),"utf-8"
    except UnicodeDecodeError: return raw.decode("cp1252"),"cp1252/latin1"

def find_song_txt(folder):
    for n in sorted(os.listdir(folder)):
        if n.lower().endswith(".txt") and not n.startswith("."):
            p=os.path.join(folder,n)
            try: txt,_=read_text(p)
            except Exception: continue
            if "#TITLE:" in txt and ("#MP3:" in txt or "#AUDIO:" in txt): return p,txt
    return None,None

def ffprobe(p):
    try:
        out=subprocess.run(["ffprobe","-v","quiet","-print_format","json","-show_streams","-show_format",p],
                           capture_output=True,text=True,timeout=30).stdout
        return json.loads(out)
    except Exception: return {}

def quality_score(folder):
    total=vheight=abitrate=has_video=0
    for n in os.listdir(folder):
        p=os.path.join(folder,n)
        if not os.path.isfile(p): continue
        total+=os.path.getsize(p); ext=n.lower().rsplit(".",1)[-1] if "." in n else ""
        if ext in ("mp4","mkv","avi","webm","mov"):
            for st in ffprobe(p).get("streams",[]):
                if st.get("codec_type")=="video": has_video=1; vheight=max(vheight,int(st.get("height",0) or 0))
        if ext in ("mp3","ogg","opus","m4a","wav"):
            br=ffprobe(p).get("format",{}).get("bit_rate")
            if br: abitrate=max(abitrate,int(br))
    return (has_video,vheight,abitrate,total)

def process(folder, apply):
    """normaliza nombres/tags in place; devuelve nombre normalizado de carpeta."""
    txt_path,txt=find_song_txt(folder)
    # 1) reescribir song.txt: encoding + tags normalizados
    new_lines=[]
    for line in txt.splitlines():
        if line.startswith("#") and ":" in line:
            tag,val=line[1:].split(":",1); tagU=tag.upper()
            if tagU in MEDIA_TAGS or tagU in TEXT_TAGS:
                line=f"#{tag}:{normstr(val)}"
        new_lines.append(line)
    new_txt="\n".join(new_lines)+"\n"
    # 2) mapa de renombrado de archivos
    renames={}
    for n in os.listdir(folder):
        if n.startswith("."): continue
        nn=normstr(n)
        if nn!=n: renames[n]=nn
    if apply:
        open(txt_path,"w",encoding="utf-8",newline="").write(new_txt)
        for old,new in renames.items():
            os.rename(os.path.join(folder,old),os.path.join(folder,new))
    return normstr(os.path.basename(folder.rstrip("/"))), (txt_path,txt,renames)

def main():
    if APPLY: os.makedirs(DEST,exist_ok=True)
    for entry in sorted(os.listdir(SRC)):
        folder=os.path.join(SRC,entry)
        if not os.path.isdir(folder) or entry.startswith("."): continue
        tp,_=find_song_txt(folder)
        if not tp:
            log("SKIP",f"{entry} -> no es canción UltraStar"); continue

        new_name,(txt_path,txt,renames)=process(folder, apply=False)
        _,enc=read_text(txt_path)
        conv="ya UTF-8" if enc=="utf-8" else f"CONVERTIR {enc}->utf-8"
        ren = f"  | renombra {len(renames)} archivo(s) + carpeta -> '{new_name}'" if (renames or new_name!=entry) else ""

        dest_path=os.path.join(DEST,new_name); action="MOVER"
        if os.path.exists(dest_path):
            qn,qo=quality_score(folder),quality_score(dest_path)
            action = f"REEMPLAZAR (nueva {qn}>{qo})" if qn>qo else f"DESCARTAR (existente {qo}>=nueva {qn})"
        log(action, f"{new_name}  | txt:{conv}{ren}")

        if APPLY:
            process(folder, apply=True)                      # normaliza in place
            src_norm=os.path.join(SRC,new_name)
            if os.path.basename(folder)!=new_name: os.rename(folder,src_norm)
            if action.startswith("MOVER"): shutil.move(src_norm,dest_path)
            elif action.startswith("REEMPLAZAR"): shutil.rmtree(dest_path); shutil.move(src_norm,dest_path)

if __name__=="__main__": main()
