"""Fit probe for a local Ollama model: does it run 100% on the GPU at its pinned context,
and does it answer a trivial prompt without hidden reasoning?

Prints two TSV rows: task, seconds, pass|fail, note  (tasks: gpu, thinking).
CLI: python3 probe.py <ollama-model-id>      (server: $OLLAMA_HOST_URL or 127.0.0.1:11434)
"""
import json
import os
import sys
import time
import urllib.request

BASE = os.environ.get("OLLAMA_HOST_URL", "http://127.0.0.1:11434")


def api(path, body=None):
    req = urllib.request.Request(BASE + path, data=json.dumps(body).encode() if body else None,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as resp:
        return json.load(resp)


def main(model):
    start = time.time()
    body = {"model": model, "stream": False,
            "messages": [{"role": "user", "content": "Reply with exactly: OK"}]}
    try:
        try:
            reply = api("/api/chat", body)
        except OSError:
            # A model created seconds ago can answer 500 on its first load; retry once.
            time.sleep(3)
            reply = api("/api/chat", body)
    except OSError as exc:
        print("gpu\t0\tfail\tno reply: %s" % exc)
        print("thinking\t0\tfail\tno reply")
        return
    secs = round(time.time() - start)
    loaded = [m for m in api("/api/ps").get("models", []) if m.get("name") == model or m.get("model") == model]
    if loaded and loaded[0].get("size"):
        share = 100 * loaded[0].get("size_vram", 0) / loaded[0]["size"]
        print("gpu\t%d\t%s\t%d%% GPU" % (secs, "pass" if share >= 99.5 else "fail", share))
    else:
        print("gpu\t%d\tfail\tnot listed by /api/ps" % secs)
    thinking = (reply.get("message") or {}).get("thinking") or ""
    print("thinking\t%d\t%s\t%d chars" % (secs, "pass" if not thinking.strip() else "fail", len(thinking)))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
