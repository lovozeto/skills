# Definition Ledger protocol

The Ledger is the anti-hallucination mechanism. It makes "no holes" auditable: every
required field is explicitly `DEFINED` or `PENDING`, and generation is blocked while any
field is `PENDING`.

## Lifecycle

1. **Instantiate.** Copy `../../assets/templates/DEFINITION.ledger.md` into the scratchpad
   at the start of Phase 1. One Ledger per run.
2. **Fill by asking.** Walk each field. For a `PENDING` field, ask the user. Record the
   answer verbatim in intent. Never fill from memory.
3. **Suggestions are explicit.** You may propose a value, but write it as
   `SUGGESTED: <value>` and keep the field `PENDING` until the user confirms. On
   confirmation, flip it to `DEFINED` and drop the `SUGGESTED` marker.
4. **Blocked fields stay blocking.** If the user cannot answer, write
   `PENDING (blocked: <reason>)`. It still blocks generation. Do not invent a value to get
   unblocked.
5. **Gate.** Before the HTML approval view and before any file write, verify the Ledger has
   **zero** `PENDING`. If not, return to Phase 1.

## Required fields (minimum)

- `objective` — the single task/scope.
- `expected_output` — format, shape, success criteria.
- `mode` — new build | fix/review (if fix: the existing paths, read first).
- `type` — agent | skill | plugin (from Phase 2, confirmed).
- `orchestrator_model` — mandatory (native tier or delegated route).
- `subagents[]` — for each: `task` (exactly one), `model` (mandatory), `tools`.
- `dependencies` — own[] (to package) and universal[] (to gate).
- `hooks` — the guardrail hooks to wire (always at least one), with the event and purpose.
- `kb` — needed? if yes: sources + maintainer agent; if no: justification ("trivial for KB").
- `verification` — which levels will run (0 always; 1 opt-in).

Add artifact-specific fields as needed. Every added field follows the same `DEFINED` /
`PENDING` discipline.

## Audit

Keep the completed Ledger in the scratchpad. It is the record that nothing was assumed. If
the user later asks "why is this field X," the Ledger shows it was confirmed, not invented.
