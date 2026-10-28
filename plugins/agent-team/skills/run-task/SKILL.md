---
name: run-task
description: "Turns a change request into a tracked ticket and runs the agent team on it. Use first, before reading or editing any code, whenever the owner asks to add, change, fix or remove something (code, copy, UI, data, emails) in a repo whose CLAUDE.md says work runs through run-task or that has .claude/agent-team.json; also when they ask to run, continue or close a ticket. Not for questions about the code, not for repos without .claude/agent-team.json, and not for editing the agent system itself."
model: opus
---

# run-task — one ticket, start to finish

**Effect:** effective. It opens GitHub issues, dispatches agents that change the repo, and ends on a branch with a PR. Every push and PR waits for the owner's yes.

You are the **orchestrator**. The agents do the work, one task each; you hold the order, the gates and the record. Read `references/tickets.md` (next to this file) first, every run: it holds the ticket format, the lifecycle and the stage table.

**Model:** Claude `opus`. Fallback `sonnet`; tell the owner it is running on the fallback. Under another provider, its strongest reasoning tier.

**Invocation:** model-invoked, so a change request reaches the ticket flow without the owner remembering a command; the gate is the approval hook on `ready-for-agent`, not the trigger.

**Precondition:** `.claude/agent-team.json` and `.claude/knowledge/agent-team.md` exist at the repo root. Missing either: say this repo is not set up for agent-team and stop.

**Agents:** plugin agents are dispatched as `agent-team:<name>`; a project-local agent in `.claude/agents/` by its bare name. `## Project` in `.claude/knowledge/agent-team.md` lists the local agents and the stage each joins, and the brief each needs beyond the common one.

## Entry A — the owner describes a change

1. Dispatch `agent-team:pm`. Brief: the owner's words verbatim, any feature or file they named, the absolute path of `references/tickets.md`, and the project-local agents.
2. Open the issue: write the issue body to a temp file outside `.scratch/` with the Write tool (the draft's `**Track:**` and `**Agents:**` lines, then its sections from `## Objective` to `## Open questions`), then `gh issue create --title "<TITLE>" --body-file <tmp> --label <TRACK> --label needs-triage`. A missing label makes it fail: tell the owner to run `setup-tracking <owner/repo>` and stop. Then `mv <draft> .scratch/issues/<N>-<slug>.md` (the ticket guard allows a rename between working files) and set `**Issue:** #<N>`. Move the issue to Backlog: call the Skill tool with "track-work" when it is listed; otherwise tell the owner the board was not updated.
3. Show the owner the issue link, its summary, its `Agents:` line and every open question.
4. Stop and wait for the owner. Write each answer under its question in the working file and in the issue body (rewrite the temp body file, then `gh issue edit <N> --body-file <tmp>`). An answer that settles a product or technical decision for the project also gets one `Decision: <what> — <who> — <why>` line in `## Log`; an answer that only steers this ticket stays under its question. When every open question has an answer and the owner approves in chat, run `gh issue edit <N> --add-label ready-for-agent --remove-label needs-triage`: a hook asks the owner to confirm, and the confirmation is the approval. Then continue at Entry B.

## Entry B — run an approved ticket

1. **Gate.** Find the working file `.scratch/issues/<N>-*.md`. With none (a new machine or session), rebuild it from the issue (`gh issue view <N> --json body,comments`): the header and sections from the body, `Branch:` from the latest `Branch:` comment, `## Log` from the `### <agent>` comments, `Stage:` `building` after a `Branch:` comment, else `planned`; `QA: pending` and `VQA: pending` (or `n/a` as the body says), so `qa` and `vqa` run again; and tell the owner. When a `### memory-keeper` comment exists and no PR is open, rebuild nothing and go straight to step 5, which needs no working file. Then `gh issue view <N> --json state,labels`: the issue must be open and labelled `ready-for-agent`; anything else: say so, name what is missing, and stop. A ticket at `Stage: done` with no open PR resumes at step 5; one with an open PR is finished. Each agent in `Agents:` must exist in the plugin or in `.claude/agents/`, and each plugin agent must have a `write_scopes` entry in `.claude/agent-team.json` (`[]` for read-only ones); a missing agent or entry: name it and stop.
2. **Branch.**
   - **New run** (`Branch: none`): ask the owner whether the work goes on a new branch, and from which base, or on an existing one. Wait for the answer, create or switch, write `**Branch:** <branch> (from <base>)`, set `**Stage:** building`, post `Branch: <branch> (from <base>)` as an issue comment, and move the issue to In progress (track-work).
   - **Resumed run** (any other `Branch:` value): switch to that branch, take the base from the same line, keep `Stage:` as it is, and continue step 3 at the first agent in `Agents:` with no `### <agent>` entry in `## Log` (a `content` entry without a needed `COPY REVIEW` is unfinished: resume at delegation when there is no `### delegation` entry, otherwise at `content` in review mode).
3. **Dispatch**, stage by stage in the table's order, only the agents in `Agents:`, one at a time.

   **Brief**
   - Every agent: the ticket path, the branch, the global KB root as an absolute path (`$CLAUDE_KB_DIR`, or `~/dev/claude-kb` expanded), the scope bullets tagged with its name, and the results it depends on from `## Log`. Absolute paths. Before dispatching an agent with a `knowledge` entry in `.claude/agent-team.json`, check that `kb stale --json` runs and the entry maps at least one file; when either fails, add to its brief: "Your knowledge files are not available: say the KB does not cover a topic instead of answering from memory", and log that. (The launch hook's note arrives after the brief is sent, so it cannot be relied on for this.)
   - A project-local agent: also what its `## Project` entry asks for.
   - Build agents, once a `PLAN` exists: also their `FILES` lines, their `ORDER` steps and the `TO VERIFY` lines they own. `frontend` also gets the UI-library recipe when one exists.
   - `content`: mode `write` on its first run; mode `review` after delegation, with the source copy and the drafts (none when delegation was skipped).
   - `qa`: set `**Stage:** qa` first; brief it with the ticket path and the base from the `Branch:` line.
   - `vqa`: after `qa`, when UI changed; brief it with the ticket path, the routes (from the PLAN's `FILES` or the scope bullets, as URL paths), and the UI-library recipe and `UI DECISIONS` from the log. A `vqa` that returns `OUT OF SCOPE: no running preview` stops the run until the owner fixes the launch configuration or starts the server.
   - `web-graphics`: also the ticket's `## Graphics spec` and the `UI DECISIONS`.
   - `reference-scout`: also the project's aesthetic as the ticket states it, in terms of the aesthetics KB (required), and, when the ticket gives them, how many references and which decisions they must support.

   **After each return**
   - Append to `## Log`: `### <agent> — <date>` and the result, and post the same entry as an issue comment (Write it to a temp file outside `.scratch/`, then `gh issue comment <N> --body-file <tmp>`), so the issue holds the record. Copy verbatim what a later agent or check reads (a port map, architect's `PLAN`, reference-scout's `REFERENCES`, brand's `BRAND GUIDELINES`, content's `COPY` and `COPY REVIEW`, ux's `UX REVIEW`, ui's `UI DECISIONS` and the library recipe in full; the `UI DOCS`, `API FOR FRONTEND`, `VERIFIED` and `NOT VERIFIED` lines; vqa's findings and measurements); condense the rest. Show the owner the same summary.
   - `OPEN QUESTIONS` other than `none` in any agent's result: show them to the owner, write the answers into the ticket (with `Decision:` lines where they settle something), then continue.
   - After `architect`: when its `FILES` name an owning agent missing from `Agents:`, or contradict a scope tag, show the owner and, with their go-ahead, update `Agents:` and the tags. An agent added this way must exist; otherwise name it and stop.
   - After `content` writes source copy that the project shows in other languages (`## content`): delegate the drafts: call the Skill tool with "delegation:delegate", passing only the source strings (public copy only, no personal data) and asking to keep every `{placeholder}` unchanged. When content's `OPEN QUESTIONS` were answered, first brief `content` in write mode again with the answers and log that result, so the drafts start from complete copy. Log `### delegation — <date>` with the drafts verbatim, or "skipped: <why>" when the skill is missing or fails. Then brief `content` in review mode.
   - After `reference-scout`: show the owner every `proposed` entry it added to `.claude/knowledge/brand/reference-board.md` (id, title, URL, trait, supports), and its `UNREACHABLE` and `NO KB TERM` lines. Stop and wait. Write each answer into the board as `**Status:** approved` or `**Status:** rejected`, and log the outcome under the `### reference-scout` entry as `APPROVED: <ids>` / `REJECTED: <ids>`. Add a `Decision:` line only when the owner states a project-wide aesthetic choice.
   - `NEEDS FRONTEND` from web-graphics: show it to the owner and, with their go-ahead, add it as a `- [frontend] …` bullet and dispatch frontend.
   - `BACK TO UI`: brief `ui` with those items, then run the library agent again; when the same item comes back twice, show it to the owner and stop.
   - `NEEDS BACKEND`: show it to the owner. With their go-ahead: add `backend` to `Agents:` before `frontend` if it is missing, add the item as a `- [backend] …` bullet, dispatch backend, then dispatch frontend again with backend's `API FOR FRONTEND`; each run gets its own `### <agent>` log entry.

   **Stops**
   - Before dispatching `brand` (a new or a resumed run): when `.claude/knowledge/brand/reference-board.md` has any `Status: proposed` entry for this ticket, show those entries to the owner and stop; dispatch `brand` once every entry for this ticket is `approved` or `rejected`.
   - A launch blocked because the agent's knowledge expired: show the owner the hook's message and the refresh it names, and stop. After the owner confirms the refresh, resume at that same agent.
   - `OUT OF SCOPE` or a missing input: show it to the owner and stop.
   - `QA: FAIL`: show the failures, and with the owner's go-ahead send each one to the agent that owns the fix, then run `qa` again.
   - `VQA: FAIL`: show the findings; with the owner's go-ahead send each to the agent that owns the fix (frontend, web-graphics, or ui for a decision), then run `qa` and `vqa` again.

   Done when every agent before `memory-keeper` has a log entry (a `content` entry counts only with its `COPY REVIEW` when its copy appears in other languages), `QA: PASS`, and `VQA: PASS` or `n/a`.
4. **Close.** Dispatch `agent-team:memory-keeper` with the ticket path and the branch, then log its return and post it as an issue comment, as in step 3. A blocked close means a verdict is missing: return to step 3.
5. **Deliver.** Commit on the branch (Conventional Commits, English, ≤ 50 characters). Ask the owner before pushing and before opening the PR; its body says `Closes #<N>`. Once the PR is open: move the issue to In review (track-work) and delete the working file (`rm`; the ticket guard allows it at `Stage: done`): the issue's comments hold the log. Merge only when the owner asks for that merge in chat (global rule); the PR closes the issue, and track-work moves it to Done.

## Rules

- Running agents in parallel needs the owner's yes first, each time.
- Every change to the working file reaches the issue in the same step: header and sections through `gh issue edit <N> --body-file <tmp>` (answers, `Agents:` and scope-tag updates, new bullets), `## Log` lines (results, `Decision:` lines, `APPROVED`/`REJECTED`) as an issue comment. Temp files go outside `.scratch/`, written with the Write tool.
- The record lives in the issue; the working file carries it while in flight. You write `Stage:`, `Branch:` and `## Log`; `QA:` belongs to `qa`, `VQA:` to `vqa`.
