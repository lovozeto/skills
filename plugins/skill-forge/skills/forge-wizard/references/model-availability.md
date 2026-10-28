# Model availability & the equivalence rule

Read this in Phase 3. The mandatory-model field is **Claude-first**: name a Claude tier as the
base, then add a cross-provider note so the instruction stays coherent if the artifact runs
under ChatGPT or OpenCode. **No local models.**

## Base: Claude tiers (always available)
`haiku`, `sonnet`, `opus` — the safe baseline for any orchestrator/worker. This is what goes
in `model:` when the artifact runs under Claude.

## Cross-provider note (coherence, not detection)
You are not probing the machine for other providers. You are making the artifact's
instructions portable: from `kb get agent-building/model-catalog`, add the ChatGPT and OpenCode Zen (and, when
relevant, Kimi) equivalents for the chosen role, marked `advisory` until `/refresh-forge-kb`
verifies the exact ids. Example line in an agent body:

> Model: `sonnet` (Claude base). If run under ChatGPT, use <equivalent>; under OpenCode, use
> the <Zen equivalent>.

## The equivalence rule (within Claude)
If the recommended Claude tier does not fit (too weak/too costly for the role), step along the
Claude ladder (`haiku` ↔ `sonnet` ↔ `opus`) to the cheapest tier that clears the bar, and
**say so**. Never assume a specific cross-provider model exists — keep it `advisory` until
verified.

The point is token economy without hallucination: cheapest capable Claude tier as the base,
plus coherent cross-provider guidance, and explicit about anything unverified.
