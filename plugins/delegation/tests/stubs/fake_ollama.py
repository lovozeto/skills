"""Fake Ollama API for tests: /api/version, /api/tags, /api/ps, /api/chat (echoes the model).

Usage: python3 fake_ollama.py <port-file> <last-request-file>
"""
import json, sys
from http.server import BaseHTTPRequestHandler, HTTPServer

TAGS = {"models": [{"name": "big-coder:30b", "size": 13_000_000_000},
                   {"name": "tiny:1b", "size": 900_000_000},
                   {"name": "mid:7b", "size": 5_400_000_000}]}


LAST = {"model": ""}


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, obj):
        body = json.dumps(obj).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/ps":
            # Models named *cpu* load partly on the CPU; the rest fully on the GPU.
            self._send({"models": [{"name": LAST["model"], "size": 100,
                                    "size_vram": 80 if "cpu" in LAST["model"] else 100}]})
            return
        self._send({"version": "0.0.0"} if self.path == "/api/version" else TAGS)

    def do_POST(self):
        req = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        if self.path == "/api/show":
            # Models named *nopin* have no pinned num_ctx.
            self._send({"parameters": "" if "nopin" in req["model"] else "num_ctx 16384", "model_info": {}})
            return
        if req.get("model") == "missing":
            body = json.dumps({"error": "model 'missing' not found"}).encode()
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
            return
        open(sys.argv[2], "w").write(json.dumps(req))
        LAST["model"] = req["model"]
        msg = {"content": "model=" + req["model"]}
        if "think" in req["model"]:
            msg["thinking"] = "Let me think about this."
        self._send({"message": msg})


srv = HTTPServer(("127.0.0.1", 0), H)
open(sys.argv[1], "w").write(str(srv.server_port))
srv.serve_forever()
