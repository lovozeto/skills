#!/usr/bin/env python3
"""Fuerza identidad canónica en una carpeta de canción UltraStar generada.
Renombra carpeta + archivos a 'Artista - Título[ sufijo]' y fija #ARTIST/#TITLE + tags de media.
Detecta roles por sufijo de archivo (no confía en los tags que UltraSinger adivinó mal).
Uso: finalize.py "<carpeta>" "<Artista>" "<Título>"
"""
import sys, os, re, unicodedata

folder, ARTIST, TITLE = sys.argv[1], sys.argv[2], sys.argv[3]
base = f"{ARTIST} - {TITLE}"

def read(p):
    raw=open(p,'rb').read()
    if raw.startswith(b'\xef\xbb\xbf'): raw=raw[3:]
    try: return raw.decode('utf-8')
    except: return raw.decode('cp1252')

files=[f for f in os.listdir(folder) if not f.startswith('.')]
def ext(f): return f.rsplit('.',1)[-1].lower() if '.' in f else ''
roles={}   # archivo_actual -> nombre_nuevo
txt=None
for f in files:
    e=ext(f); low=f.lower()
    if e=='txt': roles[f]=f"{base}.txt"; txt=f
    elif '[vocals]' in low: roles[f]=f"{base} [Vocals].{e}"
    elif '[instrumental]' in low: roles[f]=f"{base} [Instrumental].{e}"
    elif '[co]' in low or e in ('jpg','jpeg','png') and '[bg]' not in low: roles[f]=f"{base} [CO].{e}"
    elif '[bg]' in low: roles[f]=f"{base} [BG].{e}"
    elif e in ('mp4','mkv','webm','avi','mov'): roles[f]=f"{base}.{e}"
    elif e=='mid': roles[f]=f"{base}.mid"
    elif e in ('m4a','mp3','ogg','opus','wav'): roles[f]=f"{base}.{e}"   # audio principal
    else: roles[f]=f  # dejar igual

# reescribir el txt: #ARTIST/#TITLE + tags de media apuntando a los nombres nuevos
tp=os.path.join(folder,txt); content=read(tp); out=[]
audio_new=next((v for k,v in roles.items() if ext(k) in ('m4a','mp3','ogg','opus','wav') and '[Vocals]' not in v and '[Instrumental]' not in v), '')
voc=next((v for v in roles.values() if '[Vocals]' in v),'')
ins=next((v for v in roles.values() if '[Instrumental]' in v),'')
cov=next((v for v in roles.values() if '[CO]' in v),'')
vid=next((v for k,v in roles.items() if ext(k) in ('mp4','mkv','webm','avi','mov')),'')
setmap={'ARTIST':ARTIST,'TITLE':TITLE,'MP3':audio_new,'AUDIO':audio_new,
        'VOCALS':voc,'INSTRUMENTAL':ins,'COVER':cov,'VIDEO':vid}
seen=set()
for line in content.splitlines():
    if line.startswith('#') and ':' in line:
        k=line[1:].split(':',1)[0].upper()
        if k in setmap:
            seen.add(k)
            if setmap[k]: out.append(f"#{k}:{setmap[k]}")
            continue
    out.append(line)
# asegurar #ARTIST/#TITLE presentes (insertar tras #VERSION o al inicio)
header=[]
if 'ARTIST' not in seen: header.append(f"#ARTIST:{ARTIST}")
if 'TITLE' not in seen: header.append(f"#TITLE:{TITLE}")
if header:
    # insertarlos después de la primera línea # si existe
    out = header + out
open(tp,'w',encoding='utf-8',newline='').write("\n".join(out)+"\n")

# renombrar archivos, luego la carpeta
for old,new in roles.items():
    if old!=new: os.rename(os.path.join(folder,old),os.path.join(folder,new))
parent=os.path.dirname(folder.rstrip('/'))
newfolder=os.path.join(parent, base)
if os.path.abspath(folder)!=os.path.abspath(newfolder):
    if os.path.exists(newfolder):
        print(f"YA EXISTE destino, no piso: {base}"); sys.exit(2)
    os.rename(folder,newfolder)
print(f"OK -> {base}")
