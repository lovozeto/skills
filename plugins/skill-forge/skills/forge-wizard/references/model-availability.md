# Model availability & the equivalence rule

Read this in Phase 3. The mandatory-model field must name a model that can actually launch
the agent on this machine. Never assume a model is present.

## What to check, in order

1. **Claude tiers** — always available: `haiku`, `sonnet`, `opus`. These are the safe
   fallback for any orchestrator/worker.
2. **Local models** — read the active profile's `hardware.md` (set up by the machine's
   AI-setup, e.g. `~/dev/claude-kb/` profile). It lists local models and wrappers. If there
   is no profile, treat local delegation as **not configured** and do not wire it.
3. **Cloud cross-provider** (ChatGPT, Kimi/Moonshot, OpenCode Zen) — available only if a
   verified wrapper/credential exists on the machine. Without one, the route is `advisory`:
   document it in the agent body but do not promise a real call.

## The equivalence rule

If the model `kb/model-catalog.md` recommends for a role is **not** available:
1. Look up the role (orchestrator vs worker) and the recommended model in the catalog's
   **equivalence table**.
2. Pick the **closest available** equivalent (same role tier, prefer same provider, then the
   cheapest that clears the bar).
3. If nothing equivalent is verifiably available, fall back to the Claude tier ladder and
   **state in the output** that availability could not be verified and the fallback was used.

## Writing the field

- Native Claude tier → put it in the agent/skill `model:` frontmatter.
- Delegated cross-provider → leave `model:` as a Claude tier (or `inherit`) and record the
  delegation route + provider + `tier: advisory|proven` in the agent body.

The point of the whole rule is token economy without hallucination: pick the cheapest
capable model that is real on this machine, and be explicit whenever you had to fall back.
