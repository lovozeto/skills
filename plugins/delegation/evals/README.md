# Trigger evals

Level-1 trigger sets for the `delegate` and `write-for-model` skills: a flat array of
`{query, should_trigger}`, 10 positives and 10 close-neighbour negatives each.

## Run

```bash
python3 run_triggers.py <plugin-dir> <label> <model> [runs-per-query]
```

The skills are installed globally, so skill-creator's `run_eval` reports 0 triggers; this
script measures selection by hand instead. For each query it runs `claude -p` with
`--plugin-dir <plugin-dir>` (that copy replaces the installed plugin), `--max-turns 3`,
`Skill` and `Read` allowed, in `workdir/`, where `make_fixtures.py` writes the long files
the queries name (a 4,000-line log, a 1,500-message mailbox, 30 docs, 40 classes...). A
trigger is a `Skill` tool_use naming the skill. A run that does not end in a `result` event
is retried once, then counted as invalid, never as a miss. `--append-system-prompt` only
says not to ask for the session objective (the user's CLAUDE.md session rule otherwise
answers first). Raw transcripts land in `raw/` (ignored by git).

## Results (2026-10-28, `claude-opus-5-5`, 3 runs per query)

| Skill | `delegate` description | Positives | Negatives | Invalid |
|---|---|---|---|---|
| delegate | `main` | 26/30 | 30/30 | 0 |
| delegate | widened (task classes, "use ollama") | 28/30 | 30/30 | 0 |
| write-for-model | `main` (unchanged) | 28/30 | 30/30 | 0 |
| write-for-model | `main` (unchanged), fixed query | 30/30 | 30/30 | 0 |

The widened `delegate` description gained 2 trials, both on "extract every subject and date
from mailbox.mbox". With the `main` description Opus did that with `grep` instead, which
costs no model tokens: the better choice. So the gain is not an improvement and the
`main` description is kept. The one `write-for-model` miss was a query with no prompt to
tune; the query now includes one.

Earlier runs on haiku (pasted text, no fixtures, errored runs counted as misses, A/B in
parallel) gave 3-10/30 for `delegate` with +-6 trials of noise; they measured the harness,
not the descriptions, and are superseded.
