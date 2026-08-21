# Definition Ledger — <ARTIFACT_NAME>

> Anti-hallucination contract. You may **suggest**, you must **not assume**. No field is
> filled from memory. Generation is **blocked** while any field is `PENDING`. A suggestion
> stays `PENDING` (marked `SUGGESTED:`) until the user confirms it.

| Field | Status | Value / intent |
|---|---|---|
| objective | PENDING | <the single task/scope> |
| expected_output | PENDING | <format, shape, success criteria> |
| mode | PENDING | new build \| fix/review (if fix: existing paths, read first) |
| type | PENDING | agent \| skill \| plugin (confirmed, Phase 2) |
| orchestrator_model | PENDING | <native tier or delegated route> |
| dependencies_own | PENDING | <scripts/assets to package, or "none"> |
| dependencies_universal | PENDING | <binaries/packages to gate, or "none"> |
| hooks | PENDING | <event → purpose; at least one guardrail> |
| kb_needed | PENDING | yes (+sources +maintainer) \| no (justify "trivial for KB") |
| verification | PENDING | <levels that will run; 0 always, 1 opt-in> |

## Subagents (one task each)

| # | task (exactly one) | model (mandatory) | tools |
|---|---|---|---|
| 1 | PENDING | PENDING | PENDING |

## Blocked fields

<list any `PENDING (blocked: <reason>)` here; they keep blocking generation>

## Gate

- [ ] Zero `PENDING` across all fields and subagents.
- [ ] HTML approval view rendered and approved by the user.

Do not write any artifact file until both boxes are checked.
