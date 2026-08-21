# Verification procedure

Read this in Phase 5. Configuring policy is not the same as measuring that the artifact
works. This measurement layer is the official `skill-creator` plugin — do not reimplement
it, call it.

## Locate skill-creator

```
~/.claude/plugins/marketplaces/claude-plugins-official/plugins/skill-creator/skills/skill-creator
```

Assign it to `<SC>` in the commands below. If it is not installed, run only Level 0's strict
YAML parse (below) and **state that trigger testing was not run**.

> **Precondition:** the scripts need **Python ≥ 3.10** with `pyyaml`. The macOS Command Line
> Tools Python 3.9.6 fails (`TypeError: unsupported operand type(s) for |` — PEP 604). Use a
> venv with Python ≥ 3.10 + pyyaml, assigned to `$PY`. If it does not exist, that is a host
> dependency — do not install it from here; say so and stop at that level.
>
> **Invoke as a module** (`-m scripts.x`), not a standalone script, or you get
> `ModuleNotFoundError: No module named 'scripts'`. Use `PYTHONPATH=<SC>` **without** `cd`.

## Level 0 — structural (always, free)

```bash
PYTHONPATH=<SC> $PY -m scripts.quick_validate <skill-path>
```

> **Known false positives** (validator checks the portable agentskills.io subset; Claude
> Code extends it). These fields are **valid in Claude Code** — do not remove them:
> `disable-model-invocation`, `argument-hint`, `when_to_use`, `model`, `allowed-tools`.
> A genuine error: a key that exists in neither standard (e.g. a bare `version:` — it belongs
> under `metadata:`).

`quick_validate` only inspects `SKILL.md`. For every other file (agents, commands,
templates) do a strict YAML parse of the frontmatter — it catches the most common bug, an
unquoted `description` containing `:` or `{}`:

```bash
$PY - <<'PY'  # run on every SKILL.md / agent / command / template
import re, yaml, sys
m = re.match(r'^---\n(.*?)\n---', open(sys.argv[1]).read(), re.S)
yaml.safe_load(m.group(1)); print("frontmatter OK")
PY
```

**Rule: any `description` containing `:` or `{}` must be quoted.**

## Level 1 — trigger testing (opt-in: spends Claude tokens)

1. Write the eval set: a **flat array** of `{"query": "...", "should_trigger": true|false}`,
   with positives and close-neighbor negatives.
2. Run from the **project root where you want to measure** (not from `<SC>`):
   ```bash
   PYTHONPATH=<SC> $PY -m scripts.run_eval --eval-set <set.json> --skill-path <skill> \
     --model haiku --runs-per-query 3 --verbose
   ```

> **Trap — measure selection, not execution.** `run_eval` writes a temporary command with
> the `description` into `<project_root>/.claude/commands/` and measures whether *that* fires.
> If the real skill is installed globally, it competes with the temporary one and the harness
> reports **0 triggers** across all queries. Symptom: all positives at `rate=0/N`, negatives
> pass — that pattern is the diagnostic, not a result. Run from a project where the skill is
> **not** installed. If there is no escape, measure manually with
> `claude -p "<query>" --model haiku --output-format stream-json`, discard the init event,
> and count a trigger when the skill is **selected**.

> **CLAUDE.md interference in headless mode.** A session-goal rule ("ask the objective first")
> can fire before the skill in `claude -p`. Claude still identifies the correct skill; measure
> **selection**, not execution, or you will blame the `description` for zeros.

3. Optimize the `description` from the results (same project root):
   ```bash
   PYTHONPATH=<SC> $PY -m scripts.improve_description --eval-results <res.json> \
     --skill-path <skill> --model <model>
   ```
   Keep the one that **measures** better, not the one that sounds better.

## Artifact-specific checks

- **Ledger:** dry-run a case with a missing field → confirm generation is blocked while any
  field is `PENDING` and nothing is invented.
- **Type decision:** three cases (simple searcher agent / skill + 2 agents / multi-skill) →
  confirm the recommended type and the confirmation step.
- **Universal deps:** a case with a missing binary (e.g. `ffmpeg`) → the preflight hook
  detects it, asks permission, and **blocks** if declined.
- **HTML approval view:** confirm it renders and that no artifact file is written before
  approval.
