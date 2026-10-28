---
name: delegate
description: Hand a token-heavy, low-reasoning task to a free local or cloud model instead of spending Claude tokens. Use before summarizing or extracting from long text or logs, translating or rewriting prose, converting formats, mechanical code edits or boilerplate, or reading long code; and when the user says "delegate" or "use a free/local model".
argument-hint: "[task description]"
---

# delegate

Route one task to the cheapest free model that clears its quality bar, then verify what
comes back. The measured knowledge (which model does what, on which machine) lives in the
user's knowledge base, base `delegation`; this skill is the procedure.

## 1. Decide whether to delegate

Delegate when the task is **large in tokens, simple in reasoning, and returns something
compact** (a summary, JSON, a diff). A small task costs more to coordinate than to do.

Keep on Claude: architecture, decisions, critical code, web search, QA of delegated output,
and any classification that needs knowledge of the world (is this library deprecated?):
small models answer those with confident inventions.

Done when you can name the task class (summarize, extract, rewrite, translate, convert,
edit code, read code) or have decided to do the task yourself.

## 2. Load the knowledge

Try in order; a source works when it returns at least one rule, otherwise try the next:

1. `kb` on the PATH: `kb get hardware` (this machine's profile) and
   `kb search "<task class>" --base delegation` (routing and model rules).
2. `$KB_ROOT/INDEX.md`: open the `hardware` and `delegation/routing.md` entries it lists.
3. Neither: **generic mode**. Tell the user once: "no delegation knowledge base: model
   choice is unmeasured, so I will check the result more closely."

From the profile read `delegation_local` and `opencode`:
- `delegation_local: not-configured` → this machine runs no local models: skip every
  `ollama` route.
- No profile → say "machine not profiled" and use what `ollama list` shows.
- `opencode: not-allowed` or `not-installed` → skip every `ask-opencode` route.

Done when you know which source you are using (or generic mode) and which routes this
machine allows.

## 3. Ask about data

Unless the user already said it, ask: **"Does this material contain data or credentials
(database contents, CSV or dumps, personal data, finances, keys)?"** No answer counts as yes.

- **Data** → local models only, or Claude.
- **No data** → cloud models are allowed too: new code from a description, or code without
  data or credentials.

Done when the answer (data: yes or no) is recorded.

## 4. Route

| Task | Data | Route |
|---|---|---|
| Text only (summarize, extract, rewrite, translate, convert, read code) | either | `ask-local` |
| Reads or edits files | yes | `ask-opencode --model ollama/<agent model> --dir <repo>` |
| Reads or edits files | no | `ask-opencode --model <free cloud model> --dir <repo>` |
| Images, PDFs, screenshots | no | `ask-opencode --model <multimodal free cloud model> --dir <folder holding the file>` |
| Images, PDFs, screenshots | yes | keep on Claude |

**Model id:** from the base when it has one for this task class; else from the profile;
else:
- `ask-local` without `--model` uses `$ASK_LOCAL_MODEL` or the smallest installed model.
- A local agent needs a model that passed `/delegation:benchmark-model`: if none is known,
  ask the user which `ollama/<id>` to use.
- A cloud model: run `ask-opencode` without `--model` to list the free ones, and ask the
  user to choose; data policies differ by provider.

Done when one route and one model id are fixed, or the task is back on Claude.

## 5. Write the prompt

Call the Skill tool with "delegation:write-for-model", passing the model id and the task. If it reports `prompt-master` missing, stop here: tell
the user the install command it gave and do the task yourself. Done when it returns the
final prompt.

## 6. Run

```
ask-local --model <id> [--format json|<schema>|@schema.json] [--system "<s>"] "<prompt>"
ask-opencode --model <id> [--dir <repo>] "<prompt>"
```

- For file edits, start from a clean git tree so the change is reviewable as a diff.
- Batch subtasks on one model: switching local models evicts the loaded one.
- `--unsafe` approves every tool permission, destructive ones included: pass it only when the
  user asked for it in this session.

Exit codes and what to do:
- `2` unavailable or failed (no server, no model, no opencode, run error) → one tier up.
- `3` data found for a cloud model → re-route to a local model, or do it yourself.
- `4` model not allowed → pick an allowed model and run again.

Done when the call exits 0 with output, or you have moved one tier up.

## 7. Verify

Every delegated result returns to you and passes two checks before use:

| Check | What | Catches |
|---|---|---|
| **Form** | schema, length, required fields; for edits, the `git diff` scope | broken output, edits outside scope |
| **Content** | 3–5 cases against the source; for edits, read the diff | invented values, wrong logic |

Form without content gives false confidence: schema-valid JSON can hold invented values.

Failed check → redo one tier up: `ask-local` → `ask-opencode` → do it yourself. A cheaper
Claude subagent (`model: haiku`, then `sonnet`) is a tier only when the user approves it. When a task class fails twice, stop delegating it and propose a
failure-log entry for the base to the user.

Done when the result passed both checks, or the task was redone on a higher tier.

## Hard rules

- Only free models: `opencode/*-free`, `google/gemini-*-flash*` (free tier), `ollama/*`.
- Data and credentials stay on this machine or on Claude (step 3).
- You own the QA of everything that comes back (step 7).
