---
name: init
description: Set this Mac up for local delegation (Ollama, models, opencode, machine profile), or re-evaluate newer models against the benchmark.
disable-model-invocation: true
argument-hint: "[--reevaluate]"
---

# init

Two modes. **Setup** installs Ollama and opencode, pulls the models that fit, measures them,
and writes the machine profile. **Re-evaluate** looks for newer models, measures them against
the current ones, and replaces a model only when it wins.

Every install, download, LaunchAgent, removal, and profile or knowledge-base write waits for
the user's explicit yes, asked one step at a time.

## Paths

- **Profile:** with `$DELEGATION_PROFILE_DIR`, the machine file is the `.md` in that folder
  whose `machine_uuid` matches this Mac, or a new `<name>.md` (ask the name: one per machine,
  kebab-case). Without it: `~/.config/delegation/hardware.md`.
- **KB link:** with both `$DELEGATION_PROFILE_DIR` and `$KB_ROOT`, link the profile as
  `$KB_ROOT/hardware.md` (`ln -sfn`). If that path exists and is not a symlink, show it and
  link only after a yes.
- **Results:** `<profile folder>/<name>/benchmark/results/` with `$DELEGATION_PROFILE_DIR`;
  else `$DELEGATION_BENCH_DIR`; else `bench-model`'s default. Pass it to every `bench-model`
  call as `DELEGATION_BENCH_DIR`.
- **Catalog:** `kb get delegation/machine-setup`, or `$KB_ROOT/delegation/machine-setup.md`.

## 0. Detect and choose the mode

Run `delegation-machine-info` (RAM, chip, free disk, UUID, brew, Ollama, opencode). Find the
profile (Paths). Then:
- no profile, or a profile that is not `configured` without `--reevaluate` → **Setup**;
- profile `delegation_local: not-configured` with `--reevaluate` → say there are no local
  models to re-evaluate and offer Setup;
- profile `delegation_local: configured` (with or without `--reevaluate`) → **Re-evaluate**.

**Agent roles** (code agent, fast agent) run their benchmark through opencode: they apply
only when the verdict allows agents and `opencode: allowed`. Otherwise drop them everywhere
below and skip `sync-ollama-to-opencode`.

Done when the mode is chosen and the machine facts are in hand.

## Setup

### 1. Verdict

From the catalog's RAM tiers, or this rule of thumb: model plus context within about two
thirds of unified memory; under 6 GB → not fit; 6–19 GB → text only; 20 GB or more → text
and agent. Tell the user the verdict and why. **Not fit** → "Opencode only".

Done when the user has the verdict.

### 2. Install

Ollama and opencode are both required. `BREW=no` → tell the user to install Homebrew
(https://brew.sh) and stop here. For each missing tool, ask, then run:
- `brew install --cask ollama-app` (it may ask for the user's password: the user types it);
- `brew install opencode`.

Ask whether opencode is allowed on this machine (company policy) and record
`opencode: allowed`, `not-allowed`, or `not-installed` (declined). Declining Ollama ends
Setup: go to "Opencode only".

Offer `delegation-ollama-env install` (flash attention + 8-bit KV cache; halves context
RAM); after it, quit and reopen Ollama so the server reads the variables.

Done when `ollama --version` answers and opencode's state is recorded.

### 3. Models

Propose a table for this RAM tier: role (text default, Spanish tone, reasoning, and the agent
roles when they apply), name, size, `num_ctx`, source, abliterated or normal. From the catalog when
there is one; without it, ask the user for model ids or launch `model-scout` (Re-evaluate
step 2) and verify its ids (step 3). Check the total size against free disk.

After the user's yes, pull each with `delegation-pull-model <name> <num_ctx> <source>`; then,
when opencode is allowed, run `sync-ollama-to-opencode`.

Done when every approved model is on `ollama list` (and registered in opencode).

### 4. Measure

- Every model: `bench-model <name> --tasks fit`. A model **fits** when its `gpu` row passes;
  if not, offer a smaller `num_ctx` or quant and pull again.
- Agents without a code result on this machine: ask (up to ~2 h each), then
  `bench-model <name> --tasks code`.

A role is **cleared** when its model fits; for text default and Spanish tone (quick text)
its `thinking` row also passes; for agents it also passes at least half of the code tasks
that ran. If no role is cleared, offer "Opencode only".

Done when every model has fit rows and every agent a code result, or the user skipped it.

### 5. Profile

Draft the machine file and show it: frontmatter `tier: proven`, `name`, `machine_uuid`,
`last_verified` (today), `review_by` (today + 6 months), `delegation_local: configured`,
`opencode`, `ram_gb`, `chip`, and one field per cleared role: `text_model`, `agent_model`,
`tone_model`, `reasoning_model`, `fast_agent_model`. Body: the machine, a table of installed
models (name, size, `num_ctx`, role, source), the results folder, and one line pointing to
the routing rules (`delegation/routing.md` in the knowledge base). Write it after a yes; link
it (Paths).

### 6. Smoke test

`ask-local "Reply with exactly: OK"` must print `OK`; on exit 2, show its message and fix
the cause (server down, model missing) before finishing. Report: verdict, models,
measurements, profile path.

## Re-evaluate

1. **Roles.** Ask which roles to re-evaluate. The current model of each is its profile field
   (`text_model`, `tone_model`, `reasoning_model`, `agent_model`, `fast_agent_model`). A role
   with no field has no current model: screen its candidates without `--current`, and
   propose the one with the most passes among those that fit (tie → lower median time).
2. **Find.** Per role, launch the `model-scout` agent with: role, RAM budget (two thirds of
   `RAM_GB`), free disk, current model, models on disk.
3. **Verify** every candidate before proposing it: `hf.co/<repo>:<quant>` →
   `curl -sf https://huggingface.co/api/models/<repo>` lists a `.gguf` file for that quant;
   library id → `curl -sf https://ollama.com/library/<name>` answers; `.gguf` URL →
   `curl -sfI` answers. Drop the rest and say so. If a role falls below 3, relaunch
   `model-scout` once, excluding the dropped ids.
   Done when each role has at least 3 verified candidates, or the scout's reason for fewer.
4. **Screen.** Propose at least 2 per role (the user may add more). After the yes, pull each
   with `delegation-pull-model <name> <num_ctx> <source>`, run `sync-ollama-to-opencode`
   (agent roles), then `bench-model <name> --tasks fit` and
   `bench-model <name> --tasks <code|text> --current <current> --class <code|text>`.
5. **Decide** from each `Decision:` line:
   - `keep` → report why; the candidate is out.
   - `finalist` → with the user's yes, run `bench-model <candidate> --tasks <class> --runs 3`
     and `bench-model <current> --tasks <class> --runs 3` (same day: runs add up), then
     `bench-model <candidate> --tasks fit --current <current> --class <class>` to read the
     decision again.
   - `replace` → propose it.
   For text roles also read each `*_T5.txt` rewrite in the results folder and judge the tone.
6. **Apply,** each with the user's yes: update the profile (role fields, models table,
   `last_verified`); draft rule changes for the knowledge base's `delegation` base for the user
   to approve; offer to remove the losers with `ollama rm <name>`, then run
   `sync-ollama-to-opencode` again when opencode is allowed.

Results are saved with their date whether or not anything changes.

## Opencode only

When the machine is not fit, the user declines Ollama, or no role is cleared and the user
chooses cloud models only:
1. If opencode is missing, ask, then `brew install opencode`; ask whether it is allowed.
2. If Ollama is installed, run `delegation-remove-ollama` and show its list; after a yes, run
   `delegation-remove-ollama --apply`. Files go to the Trash; the user empties it.
3. Draft the profile with `delegation_local: not-configured` and `opencode`; show it, write
   it after a yes.

Done when Ollama is gone (or was never installed) and the profile says so.
