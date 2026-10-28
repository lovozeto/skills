# Work tickets (agent-team)

> The ticket format and stage table that `run-task` and `pm` follow. The record of a ticket is
> its GitHub issue on the repo's board (global rule: `agent-skills/issue-tracker` in the KB).
> The file under `.scratch/issues/` is only the working copy while the ticket is in flight:
> `.scratch/issues/` is git-ignored, and the file is deleted once the PR is open: every log entry
> is also an issue comment.

Every piece of work runs as a ticket through `run-task`. The `pm` agent drafts it, `run-task`
opens the issue, the owner approves it (label `ready-for-agent`), `run-task` dispatches the
agents it lists, and `memory-keeper` closes it. Hooks enforce the gates (`hooks/README.md` in
the plugin).

## Lifecycle

| Moment | Issue | Working file |
|---|---|---|
| pm drafts | none yet | `.scratch/issues/draft-<slug>.md`, `Issue: none` |
| run-task opens it | created with the body (`Track`, `Agents`, Objective … Open questions), the track label and `needs-triage`; board: Backlog | renamed `.scratch/issues/<N>-<slug>.md`, `Issue: #<N>` |
| owner answers | body updated with the answers | answers under each question |
| owner approves | label `ready-for-agent` replaces `needs-triage` (the hook asks the owner: that confirmation is the approval) | — |
| run starts | `Branch:` comment; board: In progress | `Branch:`, `Stage: building` |
| each agent returns | its `### <agent>` log entry as a comment | appended to `## Log` |
| memory-keeper closes | its entry as a comment | `Stage: done` |
| PR opened | body says `Closes #<N>`; board: In review | deleted |
| PR merged | closed by the PR; board: Done (run-task when it merges; otherwise the owner or the board's automation) | — |

## Format

```markdown
# <short title>

**Issue:** none | #<N>
**Stage:** planned
**Track:** dev | design | discovery
**Agents:** <agents in stage order, e.g. architect, backend, qa, memory-keeper>
**Branch:** none
**QA:** pending
**VQA:** pending | n/a

## Objective
<one or two sentences: what changes for whom>

## Scope
- <what this ticket changes>

## Out of scope
- <what it does not touch>

## Acceptance criteria
- [ ] <observable, checkable outcome>

## Open questions
- <what the pm could not answer; the owner's answer goes under each question>

## Log
<run-task appends each agent's result here, newest last, as `### <agent> — <date>`,
and one `Decision: <what> — <who> — <why>` line per owner decision>
```

- **Issue** is `none` in the draft, then the issue number. The issue's labels hold the triage role (`needs-triage`, `ready-for-agent` …); the file holds no status.
- **Stage** moves `planned` → `building` (run-task starts) → `qa` (before the quality gate) → `done` (memory-keeper closes). `done` is blocked unless `QA: PASS` and `VQA: PASS` or `n/a`.
- **Track** is the issue's track label: `dev` when code changes, `design` when only brand, UX, UI or copy decisions change, `discovery` for research with no build agents.
- **Scope** bullets always start with their owning agent (`- [backend] …`, `- [frontend] …`). Ownership follows `write_scopes` in `.claude/agent-team.json`: a path belongs to the agent whose globs match it.
- **Graphics spec** (`## Graphics spec`, after Acceptance criteria) holds the measurements web-graphics builds from, when the ticket lists it.
- **Branch** is `none` until run-task starts the work, then `<branch> (from <base>)`, so a later session can resume it on the right branch and base.
- **QA / VQA** hold `pending` or a verdict with a reason: `PASS — lint, types, build ok`. Only the `qa` agent writes the QA verdict and only `vqa` the VQA verdict. `VQA: n/a` when no UI changes.

## Stages and agents

`run-task` walks the stages in this order and dispatches only the agents named in the ticket's
`Agents:` line, one at a time, in the order listed within a stage. Each agent gets the scope
bullets tagged with its name. Plugin agents are `agent-team:<name>`; a project-local agent
(in the repo's `.claude/agents/`) keeps its bare name and joins the stage its `## Project`
entry in `.claude/knowledge/agent-team.md` names.

| Stage | Plugin agents | Typical project-local agents |
|---|---|---|
| 1. Plan | architect | a porter that maps a feature from source repos (before architect) |
| 2. Brand | reference-scout (only when the ticket needs visual references), the owners' approval of the reference board, then brand (only when the visual identity is touched) | — |
| 3. Experience | ux, content | — |
| 4. Interface | ui, then the UI-library agent (`ui-mui`) | a library agent for another library (`ui-m3`) |
| 5. Build | backend, then frontend, then web-graphics | an operations agent (`messaging-ops`) |
| 6. Quality gate | qa, vqa (when UI changed) | — |
| 7. Close | memory-keeper | — |

An agent listed in a ticket that exists neither in the plugin nor in `.claude/agents/` stops
the run. Each agent's write scope is in `.claude/agent-team.json`.
