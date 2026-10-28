"""Write the files the trigger-eval queries refer to into a directory (default: ./workdir)."""
import pathlib, random, sys

out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "workdir")
rnd = random.Random(7)
(out / "docs").mkdir(parents=True, exist_ok=True)
(out / "src/models").mkdir(parents=True, exist_ok=True)

(out / "build.log").write_text("\n".join(
    f"[{i:05d}] {'ERROR step compile-' + str(i) + ': exit 1' if i % 613 == 0 else 'INFO step ' + str(i) + ' ok'}"
    for i in range(1, 4001)))
(out / "CHANGELOG.md").write_text("\n".join(
    f"- {rnd.choice(['Finally fixed', 'Killed', 'Ripped out', 'Added awesome'])} thing #{i}!!" for i in range(200)))
(out / "mailbox.mbox").write_text("\n\n".join(
    f"From: user{i}@example.com\nSubject: Topic {i}\nDate: 2026-0{i % 9 + 1}-1{i % 9}\n\nBody {i}" for i in range(1500)))
(out / "legacy.py").write_text("\n\n".join(
    f"def f{i}(x):\n    y = [v * {i} for v in x if v % {i % 7 + 2} == 0]\n    return sum(y) - {i}" for i in range(750)))
(out / "transcript.txt").write_text("\n".join(
    f"{rnd.choice(['Ana', 'Luis', 'Marta'])}: point {i} about the release plan." for i in range(2500)))
(out / "schema.txt").write_text("\n".join(f"column_{i}: {rnd.choice(['int', 'text', 'date'])}, nullable" for i in range(3000)))
for i in range(30):
    (out / "docs" / f"page{i}.md").write_text(f"# Página {i}\n\n" + "Contenido en español. " * 200)
for i in range(40):
    (out / "src/models" / f"Model{i}.java").write_text(f"class Model{i} {{ String name; int age; String email; String foo; }}\n")
