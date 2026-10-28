"""Text benchmark tasks for bench-model: T4 (extract a WhatsApp RSVP to JSON, plain and
with a JSON schema) and T5 (rewrite a reminder in warm Colombian Spanish).

Prompts are the measured instruments: changing them breaks comparison with earlier results.
T5's check covers only the objective constraints; tone needs a human read (see `note`).

CLI: python3 tasks.py run <model> <ask-local> <ask-opencode> [t5-file]
     prints one TSV row per task: task, seconds, pass|fail, note;
     writes T5's rewrite to t5-file so a human can judge its tone
"""
import json
import re
import subprocess
import sys
import time

T4 = ('Extract the RSVP from this WhatsApp message. Output ONLY JSON, no code fences, matching '
      'exactly: {"asistira": boolean, "total": integer, "adultos": integer, "ninos": integer, '
      '"restricciones": [{"persona": string, "restriccion": string}], "llegada": string|null '
      '(24h HH:MM)}. Use "yo" for the person writing. Mensaje: "Hola!! sí vamos, somos 3 conmigo, '
      'mi esposo Carlos y la niña (7 años). Carlos es vegetariano 🙏 y yo no puedo con mariscos. '
      'Ah y llegamos tarde como a las 8 de la noche"')
T5 = ('Rewrite this reminder in warm, close Colombian Spanish (tú, not usted), at most 40 words, '
      'keeping {nombre} and {link} exactly and keeping the deadline, without pressuring the guest. '
      'Output ONLY the rewritten text. Texto: "Estimado(a) {nombre}: Le recordamos que el plazo '
      'para confirmar su asistencia vence próximamente. Agradecemos diligenciar el formulario en '
      '{link} a la mayor brevedad posible."')
SCHEMA = {
    "type": "object",
    "properties": {
        "asistira": {"type": "boolean"},
        "total": {"type": "integer"},
        "adultos": {"type": "integer"},
        "ninos": {"type": "integer"},
        "restricciones": {"type": "array", "items": {
            "type": "object",
            "properties": {"persona": {"type": "string"}, "restriccion": {"type": "string"}},
            "required": ["persona", "restriccion"]}},
        "llegada": {"type": ["string", "null"]},
    },
    "required": ["asistira", "total", "adultos", "ninos", "restricciones", "llegada"],
}
DEADLINE_WORDS = ("plazo", "vence", "pronto", "próxim", "se acerca", "poquito", "fecha", "antes de")


def check_t4(text):
    """Return (passed, note)."""
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    try:
        d = json.loads(text)
    except ValueError:
        return False, "not JSON"
    want = {"asistira": True, "total": 3, "adultos": 2, "ninos": 1, "llegada": "20:00"}
    wrong = [k for k, v in want.items() if d.get(k) != v]
    r = [(str(x.get("persona", "")).lower(), str(x.get("restriccion", "")).lower())
         for x in d.get("restricciones") or [] if isinstance(x, dict)]
    if not any("carlos" in p and "veget" in s for p, s in r):
        wrong.append("Carlos vegetarian")
    if not any(p == "yo" and "marisc" in s for p, s in r):
        wrong.append("yo no seafood")
    return not wrong, "wrong: " + ", ".join(wrong) if wrong else ""


def check_t5(text):
    """Objective constraints only; tone is left to a human."""
    low = text.lower()
    wrong = [p for p in ("{nombre}", "{link}") if p not in text]
    if len(text.split()) > 40:
        wrong.append("over 40 words")
    if re.search(r"\busted\b|estimad[oa]|\ble recordamos\b|\bsu asistencia\b", low):
        wrong.append("formal (usted)")
    if not any(w in low for w in DEADLINE_WORDS):
        wrong.append("deadline dropped")
    return not wrong, ("wrong: " + ", ".join(wrong)) if wrong else "tone: human review"


def ask(model, prompt, ask_local, ask_opencode, fmt=None):
    if model.startswith(("opencode/", "google/")):
        cmd = [ask_opencode, "--model", model, prompt]
    else:
        cmd = [ask_local, "--model", model.removeprefix("ollama/"), prompt]
        if fmt:
            cmd[1:1] = ["--format", json.dumps(fmt)]
    start = time.time()
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    return round(time.time() - start), out.returncode, out.stdout


def run(model, ask_local, ask_opencode, t5_file=None):
    runs = [("T4", T4, None, check_t4), ("T5", T5, None, check_t5)]
    if not model.startswith(("opencode/", "google/")):
        runs.insert(1, ("T4-schema", T4, SCHEMA, check_t4))
    for name, prompt, fmt, check in runs:
        try:
            secs, rc, text = ask(model, prompt, ask_local, ask_opencode, fmt)
        except subprocess.TimeoutExpired:
            secs, rc, text = 900, -1, ""
        if name == "T5" and t5_file:
            with open(t5_file, "w") as fh:
                fh.write(text)  # empty on failure, so no stale rewrite survives
        if rc == -1:
            print("%s\t900\tfail\ttimeout" % name, flush=True)
            continue
        ok, note = check(text) if rc == 0 else (False, "exit %d" % rc)
        print("%s\t%s\t%s\t%s" % (name, secs, "pass" if ok else "fail", note), flush=True)


if __name__ == "__main__":
    if len(sys.argv) in (5, 6) and sys.argv[1] == "run":
        run(*sys.argv[2:])
    else:
        sys.exit(__doc__)
