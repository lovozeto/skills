---
name: <AGENT_NAME>
description: "Single task: <the one thing this agent does>. Does not <the adjacent things it must NOT do>."
tools: <Read, Grep, ...>   # least privilege: only what the one task needs
model: <haiku|sonnet|opus|inherit>   # MANDATORY: worker tier from agent-building/model-catalog.md
---

# <AGENT_NAME> (single task)

Your one task: <state the single task precisely>. Nothing else.

## Mandatory model
`<tier>` (native) or `<provider/model>` via `<delegation route>` (delegated;
`tier: advisory|proven`). Equivalence: if unavailable, use the closest available capable tier
from `model-catalog.md` in the KB folder your brief names; Claude tier ladder as last resort, stated.

## Output (return exactly this shape)
```
<structured output the orchestrator expects>
```

## Rules
- Do exactly the one task. Do **not** do <adjacent task A> or <adjacent task B>.
- Never assume missing inputs — flag them and stop.
- Return the result or `OUT OF SCOPE`. Never expand scope.
