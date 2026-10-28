"""Fake Ollama API for tests: /api/version, /api/tags, /api/chat (echoes the model used).

Usage: python3 fake_ollama.py <port-file> <last-request-file>
"""
import json, sys
from http.server import BaseHTTPRequestHandler, HTTPServer

TAGS = {"models": [{"name": "big-coder:30b", "size": 13_000_000_000},
                   {"name": "tiny:1b", "size": 900_000_000},
                   {"name": "mid:7b", "size": 5_400_000_000}]}


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
        self._send({"version": "0.0.0"} if self.path == "/api/version" else TAGS)

    def do_POST(self):
        req = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        open(sys.argv[2], "w").write(json.dumps(req))
        self._send({"message": {"content": "model=" + req["model"]}})


srv = HTTPServer(("127.0.0.1", 0), H)
open(sys.argv[1], "w").write(str(srv.server_port))
srv.serve_forever()
