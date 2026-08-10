#!/usr/bin/env python3
"""Puente local: el navegador (logueado en ultrastar-es) hace fetch del .torrent y lo
POSTea aquí; esto lo escribe en watched/ para que qBittorrent lo ingiera.
CORS abierto para que la página HTTPS pueda postear a 127.0.0.1. Uso: torrent_bridge.py"""
import http.server, urllib.parse, os, sys
WATCHED="/Volumes/media/downloads/Torrent/watched"
LOG="/Users/eloboguerrero/karaoke-pipeline/torrent_bridge.log"
def log(m):
    open(LOG,"a").write(m+"\n"); print(m,flush=True)
class H(http.server.BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin","*")
        self.send_header("Access-Control-Allow-Methods","POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers","*")
    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.end_headers()
    def do_GET(self):
        if self.path.startswith("/list"):
            import json
            rows = []
            try:
                for ln in open("/Users/eloboguerrero/karaoke-pipeline/torrent_tokens.txt", encoding="utf-8"):
                    ln = ln.strip()
                    if "|" in ln:
                        n, tok = ln.rsplit("|", 1); rows.append({"name": n, "token": tok})
            except Exception: pass
            body = json.dumps(rows, ensure_ascii=False).encode()
            self.send_response(200); self._cors()
            self.send_header("Content-Type", "application/json"); self.end_headers()
            self.wfile.write(body); return
        self.send_response(200); self._cors(); self.end_headers(); self.wfile.write(b"bridge up")
    def do_POST(self):
        q=urllib.parse.urlparse(self.path).query
        name=urllib.parse.parse_qs(q).get("name",["song"])[0]
        name="".join(c for c in name if c not in '/\\:*?"<>|').strip() or "song"
        if not name.endswith(".torrent"): name+=".torrent"
        n=int(self.headers.get("Content-Length",0)); data=self.rfile.read(n)
        ok = data[:11]==b"d8:announce" or data[:1]==b"d"
        if ok:
            open(os.path.join(WATCHED,name),"wb").write(data); log(f"OK {name} ({n}b)")
            self.send_response(200)
        else:
            log(f"REJECT {name}: no parece torrent ({n}b)"); self.send_response(422)
        self._cors(); self.end_headers(); self.wfile.write(b"ok" if ok else b"bad")
    def log_message(self,*a): pass
http.server.HTTPServer(("127.0.0.1",8899),H).serve_forever()
