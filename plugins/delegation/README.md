# delegation

Hand token-heavy, low-reasoning tasks to free models instead of spending Claude tokens, and
check what comes back.

```bash
/plugin marketplace add lovozeto/skills
/plugin install delegation@lovozeto-skills
```

One rule decides the route:

| The task… | Material with data or credentials | Material without data |
|---|---|---|
| is text only (summarize, extract, rewrite, translate, convert) | `ask-local` (Ollama) | `ask-local` (Ollama) |
| reads or edits files | `ask-opencode --model ollama/<id> --dir <repo>` | `ask-opencode --model <free cloud model> --dir <repo>` |

Never pay-per-use models. Data and credentials never go to a cloud model: `ask-opencode`
scans the prompt and the folder before every cloud call and refuses (exit 3) when it finds
emails, phone numbers, keys, or data files.

## What is inside

| Piece | What it does |
|---|---|
| `bin/ask-local` | One completion on a local Ollama model through the API (~150 tokens of overhead) |
| `bin/ask-opencode` | One task through an isolated opencode agent; model policy and data scan |
| `bin/bench-model` | Measures a model on 12 code tasks and 3 text tasks; compares with earlier runs |
| `delegate` skill | Decides whether and where to delegate, then verifies the result |
| `write-for-model` skill | Builds the prompt for the target model with `prompt-master` |
| `/delegation:benchmark-model` | Runs `bench-model` on demand and proposes knowledge updates |
| Hooks | SessionStart: reports missing dependencies. PreToolUse: blocks disallowed models, asks before `--unsafe` |

## Requirements

| Dependency | Why | Install (macOS) |
|---|---|---|
| `python3`, `curl` | the wrappers' helpers and API calls | `xcode-select --install` |
| Ollama | local models | `brew install --cask ollama-app` |
| opencode | agents for file work | `brew install opencode` |
| `prompt-master` skill | `write-for-model` writes prompts with it | `npx skills add nidhinjs/prompt-master -g -y -a claude-code` |

Nothing is installed for you. Each route works on its own: without opencode, text tasks
still go to Ollama.

## Knowledge

The plugin ships procedure, not measurements. Model choice comes from your own knowledge
base, read with [`kb`](https://github.com/lovozeto/kb) (`kb search --base delegation`,
`kb get hardware`) or from `$KB_ROOT/INDEX.md`. Without one, the skills say the model choice
is unmeasured and check results more closely. Measure your models with
`/delegation:benchmark-model`; results go to `$DELEGATION_BENCH_DIR`.

## Environment

| Variable | Effect |
|---|---|
| `ASK_LOCAL_MODEL` | default model for `ask-local` |
| `ASK_OPENCODE_MODEL` | default model for `ask-opencode` |
| `OLLAMA_HOST_URL`, `OLLAMA_KEEP_ALIVE` | Ollama server and idle unload time |
| `DELEGATION_BENCH_DIR` | where benchmark results live |
| `KB_ROOT` | knowledge base root when `kb` is not on the PATH |

## Platforms

macOS. Linux is planned: `ask-local` starts Ollama only through the macOS app today.

## Planned

- `/delegation:init`: provisions a machine (Ollama, models with a pinned context window,
  opencode registration), records the machine profile, and re-evaluates newer models
  against the benchmark.

## Tests

`tests/run.sh` runs every test (no network; fake Ollama and opencode) and the benchmark
selftest.
