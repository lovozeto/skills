#!/usr/bin/env python3
"""VIGÍA de qBittorrent. Detecta torrents STALLED (sin seeders / sin avance) y los
cancela → su canción va a la cola de IA (stalled_to_ia.txt). Marca completos para organize.
La contraseña NUNCA se escribe: se lee de la env QBT_PASS.
  QBT_HOST=192.168.86.43:8080  QBT_USER=estejuan  QBT_PASS=***  python3 qbt_watch.py [--once]
Regla: 0 seeders y sin avance por STALL_MIN minutos → cancelar y mandar a IA.
"""
import os, sys, time, json, urllib.request, urllib.parse, http.cookiejar
HOST = os.environ.get("QBT_HOST", "192.168.86.43:8080")
USER = os.environ.get("QBT_USER", "estejuan")
PASS = os.environ.get("QBT_PASS", "")
BASE = f"http://{HOST}"
KP = "/Users/eloboguerrero/karaoke-pipeline"
STALL_MIN = float(os.environ.get("STALL_MIN", "8"))
POLL = int(os.environ.get("POLL", "60"))
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def api(path, data=None):
    url = BASE + path
    body = urllib.parse.urlencode(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers={"Referer": BASE})
    return op.open(req, timeout=20).read().decode("utf-8", "replace")

def login():
    if not PASS:
        print("ERROR: falta QBT_PASS en el entorno (no se escribe en archivos)."); sys.exit(1)
    r = api("/api/v2/auth/login", {"username": USER, "password": PASS})
    if "Ok" not in r: print(f"login falló: {r!r}"); sys.exit(2)
    print("qBittorrent: login OK")

def torrents():
    return json.loads(api("/api/v2/torrents/info"))

def cancel(h):
    api("/api/v2/torrents/delete", {"hashes": h, "deleteFiles": "true"})

def log(m):
    line = f"[{time.strftime('%H:%M:%S')}] {m}"; print(line, flush=True)
    open(f"{KP}/qbt_watch.log", "a").write(line + "\n")

def to_ia(name):
    a, t = (name.split(" - ", 1) + [""])[:2] if " - " in name else (name, "")
    open(f"{KP}/stalled_to_ia.txt", "a").write(f"{a.strip()}|{t.strip()}\n")

def sweep(state):
    stalled = done = active = 0
    for tr in torrents():
        h, name, st, prog = tr["hash"], tr["name"], tr["state"], tr["progress"]
        seeds = tr.get("num_seeds", 0)
        if prog >= 1.0 or st in ("uploading", "stalledUP", "pausedUP", "queuedUP", "forcedUP"):
            done += 1; continue
        active += 1
        prev = state.get(h)
        if prev and abs(prev["prog"] - prog) < 1e-6 and seeds == 0:
            idle = time.time() - prev["since"]
            if idle >= STALL_MIN * 60:
                log(f"STALLED → IA: {name}  (idle {idle/60:.1f}m, seeds 0)")
                to_ia(name); cancel(h); state.pop(h, None); stalled += 1; continue
        else:
            state[h] = {"prog": prog, "since": time.time()}
    log(f"barrido: activos {active}, completos {done}, cancelados-stalled {stalled}")

if __name__ == "__main__":
    login(); state = {}
    once = "--once" in sys.argv
    while True:
        try: sweep(state)
        except Exception as e: log(f"error: {e}")
        if once: break
        time.sleep(POLL)
