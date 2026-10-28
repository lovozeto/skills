# Trigger evals

Level-1 trigger sets for the `delegate` and `write-for-model` skills: a flat array of
`{query, should_trigger}`, 10 positives and 10 close-neighbour negatives each.

## How they were measured

The skills are installed globally, so `run_eval` would report 0 triggers. Measured by hand:
`claude -p "<query>" --model haiku --output-format stream-json --verbose --max-turns 2
--allowedTools Skill`, run from an empty directory, one run per query. A trigger is a `Skill`
tool_use naming the skill. `--append-system-prompt` told the model not to ask for the
session objective (the user's CLAUDE.md session rule otherwise answers first and nothing is
selected).

## Results (2026-10-28, haiku, 1 run per query)

| Skill | Pass | Positives | Negatives |
|---|---|---|---|
| delegate | 13/20 | 3/10 | 10/10 |
| write-for-model | 18/20 | 8/10 | 10/10 |

`delegate` misses the "summarize/extract/rewrite this long X" phrasings where no file is
attached: haiku answers or asks for the content instead of selecting the skill. It does
select it when the user says "delegate" or names a local/free model with a concrete job.
Misses for `write-for-model`: "Build the prompt I should send to the local model before
delegating this summary" and "The local model keeps asking questions... rewrite my prompt".

No description was changed. Treat these as a baseline for tuning the `delegate` description.
