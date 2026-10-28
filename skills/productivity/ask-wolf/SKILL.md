---
name: ask-wolf
description: Ask which skill or flow fits your situation. A router over this setup's skills and plugins.
disable-model-invocation: true
---

# Ask Wolf

You don't remember every skill, so ask. Match the user's situation to a row below and name
the skill to run, with one line on why.

Before stating what a skill does or recommending a step be skipped, read that skill's
`SKILL.md`: the summaries here are for orientation only. **Auto** means Claude reaches it on
its own; **manual** means the user types it.

## Sessions

| Situation | Skill | |
|---|---|---|
| Starting work in a repo | `/resume-session` | auto |
| Closing a session (QUICK-STATE must be updated) | `/save-session close` | auto |
| Handing the work to a fresh session | `/handoff` (Matt) | manual |
| A session went sideways; improve the environment for next time | `/retro` (Matt) | manual |

## Repos and commits

| Situation | Skill | |
|---|---|---|
| A repo has no `CLAUDE.md` / `QUICK-STATE.md` yet | `/init-project` | auto |
| Committing with the house standard | `/commit` | manual |

## Building skills, agents, plugins

| Situation | Skill | |
|---|---|---|
| Create, change, or audit a skill, agent, or plugin | `/forge-wizard` | auto |
| skill-forge says its KB expired | `/refresh-forge-kb` | manual |
| Writing or editing a `CLAUDE.md`, `AGENTS.md`, or skill by hand | `writing-for-agents` (Matt) | auto |

## Knowledge base

| Situation | Skill | |
|---|---|---|
| What does a KB rule mean, and why | `/ask-knowledge-base` | auto |
| Research a whole topic, or refresh expired KB files | `/kb-pipeline` | auto |
| Fix or add one KB entry from a known source URL | `/update-knowledge-base` | auto |
| A UX intent clashes with a verified technical constraint | `/arbitrate` | manual |

## Saving tokens

| Situation | Skill | |
|---|---|---|
| A big, low-reasoning task (summarize, extract, convert, mechanical refactor) | `/delegation:delegate` (plugin `delegation`) | auto |
| Writing the prompt for a delegated model | `/delegation:write-for-model` | auto |
| Measuring a model before routing to it | `/delegation:benchmark-model` | manual |

## Thinking and learning

| Situation | Skill | |
|---|---|---|
| Stress-test a plan or idea | `/grill-me` (Matt), or `/grill-with-docs` inside a repo | manual |
| Learn a concept inside the current project | `/teach` (Matt) | manual |
| The last answer did not land | `/wait-what` (Matt) | manual |
| A decision someone else must answer | `/to-questionnaire` (Matt) | manual |

## Engineering flows (idea → spec → tickets → TDD → review → PR)

Run `/ask-matt`: it maps Matt Pocock's engineering skills (`/to-spec`, `/to-tickets`,
`/implement`, `/tdd`, `/code-review`, `/wayfinder`, `/prototype`, `/diagnosing-bugs` and more)
and how they chain. This router does not repeat that map.

## Media

| Situation | Skill | |
|---|---|---|
| Build or repair an UltraStar karaoke library | `/karaoke-builder` | auto |
| Audit old photo/video folders before importing | `/inspecting-photo-archives` | auto |

## Keeping this router honest

A router that names a missing skill, or misses a new one, sends you the wrong way. Whenever a
skill in `lovozeto/skills` is added, renamed, archived, or changes how it is invoked, update
this file in the same change.
