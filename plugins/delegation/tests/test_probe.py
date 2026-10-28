"""Seam: probe.py's fit rows against a fake Ollama API."""
import os
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROBE = HERE.parent / "bench" / "probe.py"


class Probe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        port_file = os.path.join(cls.tmp, "port")
        cls.srv = subprocess.Popen(["python3", str(HERE / "stubs" / "fake_ollama.py"), port_file,
                                    os.path.join(cls.tmp, "req")])
        for _ in range(50):
            if os.path.exists(port_file) and open(port_file).read():
                break
            time.sleep(0.1)
        cls.env = dict(os.environ, OLLAMA_HOST_URL="http://127.0.0.1:" + open(port_file).read())

    @classmethod
    def tearDownClass(cls):
        cls.srv.kill()

    def probe(self, model):
        out = subprocess.run(["python3", str(PROBE), model], env=self.env, capture_output=True, text=True).stdout
        return {r.split("\t")[0]: r.split("\t")[2] for r in out.strip().splitlines()}

    def test_full_gpu_and_no_thinking_pass(self):
        self.assertEqual(self.probe("mid:7b"), {"gpu": "pass", "thinking": "pass"})

    def test_partial_cpu_fails_gpu(self):
        self.assertEqual(self.probe("big-cpu:30b")["gpu"], "fail")

    def test_hidden_reasoning_fails_thinking(self):
        self.assertEqual(self.probe("think:14b")["thinking"], "fail")


if __name__ == "__main__":
    unittest.main()
