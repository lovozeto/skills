---
name: benchmark-model
description: Measure a model on the delegation benchmark (12 code tasks, up to 3 text tasks) and compare it with the models measured before on this machine.
disable-model-invocation: true
argument-hint: "<model> [--tasks code|text|all]"
---

# benchmark-model

Run the benchmark on **$ARGUMENTS** and turn the result into a routing decision the user
approves. A model enters the agent map only after it passes this benchmark.

## 1. Confirm the run

- Local model: confirm it appears in `ollama list`. Cloud model: confirm it matches
  `opencode/*-free` or `google/gemini-*-flash*` (cloud models run 2 text tasks: no schema
  variant).
- Tell the user the cost before starting: code tasks take 1–10 min each on a local model
  (up to ~2 h for all 12), and the model holds the GPU meanwhile. `--tasks text` takes
  minutes.
- Compilers missing on this machine (`tsc`, `swiftc`, `clang++`, `rustc`) skip their tasks.

Start only after the user says yes.

## 2. Run

Run `bench-model <model> [--tasks ...]` in the background and wait for it to finish.
Results append to `$DELEGATION_BENCH_DIR` (default `~/.local/share/delegation/bench/`).
Exit 2 → report its stderr line and stop.

## 3. Report

Show the comparison `bench-model` prints, then say in plain terms:
- per class (code, text): passes, median time, and the verdict against each earlier model;
- which tasks failed or were skipped;
- that T5 checks only objective rules: read the rewrite in the `*_T5.txt` file next to this
  model's TSV in `$DELEGATION_BENCH_DIR` (the model id with `/` and `:` turned into `_`,
  bare names prefixed `ollama_`) and judge the tone. If T5 timed out or exited non-zero, there
  is no rewrite to judge.

One run per task guides; it does not settle. Before replacing a current model on a close
result, offer a second run.

## 4. Propose the knowledge update

If the user keeps a delegation knowledge base (`kb` or `$KB_ROOT`), draft the rows as an edit
to the base's Markdown file (the result with today's date, and any routing change it
supports). Apply the edit only after the user approves. Done when the user has approved,
changed, or declined the edit.
