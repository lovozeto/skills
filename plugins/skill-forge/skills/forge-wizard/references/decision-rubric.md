# Decision rubric — agent vs skill vs plugin

Read this in Phase 2. Classify by **complexity and required surface**, recommend one type
with reasons, and confirm with the user. Complexity drives the choice — a single internet
searcher, a skill with two agents, and several skills bundled into a plugin are all valid
outcomes.

## The three types

| Type | It is | Choose when |
|---|---|---|
| **Agent** (subagent) | A `.md` with its own system prompt, tool set, and model, run as a scoped delegate in an isolated context. | The work is **one** isolated, tool-restricted task with a clean input/output and no reusable workflow around it. Example: "search the web and return N sources." |
| **Skill** | A `SKILL.md` (+ optional bundled `scripts/`, `references/`, `assets/`) that Claude auto-loads by description. | It is a **reusable workflow** Claude should reach for by itself, needs **no** hooks, slash commands, or MCP, and ships no proprietary binaries. It may internally use subagents. |
| **Plugin** | A bundle (`.claude-plugin/plugin.json`) that can contain skills, agents, commands, hooks, and MCP servers, distributable via a marketplace. | Any of the forcing conditions below hold. |

## Forcing conditions → plugin

Pick **plugin** if **any** is true:
- It needs **hooks** (e.g. dependency gating, guardrails that must run automatically).
- It needs **slash commands** or an **MCP server**.
- It must **package its own dependencies** (proprietary scripts/assets that ship with it).
- It **coordinates several skills/agents** as one installable unit.

Note: because this project mandates **guardrail hooks on every artifact**, and hooks are a
plugin feature, most non-trivial artifacts land as plugins. A lone agent or a single
dependency-free skill can still ship without a plugin wrapper when its guardrail need is
covered by its own instructions rather than an automatic hook — state that trade-off
explicitly when you recommend it.

## Decision procedure

1. Count the **distinct tasks**. One → lean agent. Several coordinated → lean skill/plugin.
2. Check the **forcing conditions**. Any true → plugin.
3. Check **dependencies** (Phase 4 preview): own deps → plugin; universal deps needing a
   gate → plugin.
4. Recommend the **smallest** type that satisfies all constraints (token economy), and name
   the constraint that would push it up a level if it changed.
5. Confirm with the user before locking the type into the Ledger.
