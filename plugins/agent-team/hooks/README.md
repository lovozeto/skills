# agent-team hooks

The plugin's guardrails. They act only in a repo with `.claude/agent-team.json` at its root;
anywhere else every hook exits 0 at once. They run for subagents too. Python 3 standard
library only. Global rules (no commit on `main`, no reading `.env*`) are enforced by the
global hooks of the owner's setup, not here.

| Hook | Event · tools | Blocks or asks | Lets through |
|---|---|---|---|
| `guard_ticket.py` | PreToolUse · Edit, Write, Bash | on working files (`.scratch/**/issues/*.md`, any letter case, symlinks resolved): `Stage:` outside planned/building/qa/done; `Stage: done` without `QA: PASS` and `VQA: PASS`/`n/a`; anyone but `qa` changing an existing QA line or writing a verdict (VQA: `vqa`); `qa`/`vqa` changing anything besides their own line; Bash commands that write to a working file. **Asks** before `gh issue edit … --add-label ready-for-agent` or `gh issue create … --label ready-for-agent`: the owner's confirmation is the approval | header fields are read above the first `## ` heading only; reading, `git` and `gh` pass; `rm` of a working file at `Stage: done` passes |
| `guard_write_scope.py` | PreToolUse · Edit, Write, NotebookEdit | an agent writing outside its `write_scopes` globs (matched on the payload's `agent_type`, plugin prefix dropped; symlinks resolved); `reference-scout` doing anything on the board but adding `proposed` entries | the main session and agents without an entry |
| `guard_knowledge.py` | PreToolUse · Agent (and legacy Task) | launching an agent when `kb stale --json` (run in the repo) lists one of its mapped files, or a mapped file does not exist; the reason names `/knowledge-base:kb-pipeline --refresh <base>` or the repo files to review | an agent absent from the map; one mapped to nothing, no global KB, or a `kb` that is missing or fails passes with a note for the main session ("not KB-backed") |
| `preflight.py` | SessionStart | — (names missing `gh` or `kb`, never installs) | silent when all is present |

## Contract

- **Block:** exit 2, reason on stderr. Claude receives the reason and relays it.
- **Allow:** exit 0, nothing printed; the normal permission flow runs.
- **Ask:** exit 0 with a PreToolUse `permissionDecision: "ask"` JSON on stdout; the owner confirms.
- **Exit 1 never blocks** in Claude Code, so it is never used to block.
- **Fail open:** a payload that is not JSON, or any internal error, exits 0, so a broken hook
  never stops every call. The harness covers both.

## The repo config

`.claude/agent-team.json`:

```json
{
  "write_scopes": {"pm": [".scratch/**"], "backend": ["lib/**", "!lib/generated/**"]},
  "knowledge": {"ux": {"kb": ["ux/forms", "ux/laws"]}, "ui": {"repo": ["brand/guidelines"]}}
}
```

- `write_scopes`: agent → globs relative to the repo root (`**` crosses folders, a leading `!`
  excludes, as in `.gitignore`). `[]` makes an agent read-only.
- `knowledge`: agent → files, never folders. `kb` refs are global KB files without `.md`
  (`ux/forms`); `repo` refs are files under `.claude/knowledge/` without `.md`
  (`brand/guidelines`). Map only what the agent reads as knowledge: a working file (a
  reference board, an inputs README) has no `review_by` and would block the agent.

## Known limits

- An agent with Bash can still write through the shell; its instructions and the ticket guard
  cover that.
- A script that edits a working file without naming `.scratch` (a path built at run time) is
  not seen by the ticket guard; one that names it is blocked.
- `cd` inside a command is not followed: `cd .scratch/issues && echo x > 1.md` passes.
- The approval label added through `gh api` or the web UI is not seen; `run-task` reads the
  labels before it starts, so the web UI still counts as an approval.
- `kb stale` names a repo's knowledge after its folder; the hook matches repo refs by the part
  after the `:`, so a worktree folder still matches. A repo outside `kb`'s projects root is not
  indexed, so its repo files are only checked for existence.

## Tests

```bash
python3 plugins/agent-team/hooks/tests/run_tests.py
```

Each case feeds a hook the JSON payload Claude Code sends and checks the result. Exit code is
non-zero if any case fails. The harness creates throwaway git repos in a temp folder (one on
`main`, one on `feat/test`, one detached, one plain folder) and deletes them when it ends.

### Adding cases

One file per hook in `tests/cases/<hook>.json`. A new hook adds its own file; the runner
picks up every `*.json` there.

```json
{
  "hook": "guard_main_branch.py",
  "cases": [
    {
      "name": "commit on main is blocked",
      "payload": {"tool_name": "Bash", "cwd": "{repo:main}", "tool_input": {"command": "git commit -m x"}},
      "expect": "block"
    },
    {"name": "a malformed payload passes", "stdin": "not json", "expect": "allow"}
  ]
}
```

- `expect`: `block` (exit 2 with a reason), `ask` (exit 0 with an ask decision) or `allow` (exit 0).
- `files`: `{path: content}` written before the case runs, for hooks that read a file
  (a ticket before an edit). Use paths under `{dir:plain}` so they land in the temp folder.
- `project`: a placeholder that replaces `CLAUDE_PROJECT_DIR` for this case (default `{project}`,
  a temp repo whose `.claude/agent-team.json` is `tests/fixtures/agent-team.json`).
- `symlinks`: `{link: target}` created before the case runs.
- `env`: extra environment variables for the hook (`CLAUDE_KB_DIR`; `AGENT_TEAM_KB` points the
  knowledge hook at `{tests}/stubs/kb`, which prints `KB_STUB_STALE` or exits `KB_STUB_EXIT`).
- `reason` / `context`: text the stderr reason or the hook's `additionalContext` must contain.
- `agent_type` in a payload plays a subagent (`"pm"`, `"qa"`…); omit it for the main session.
- `payload` gets `hook_event_name: PreToolUse` and `cwd: {project}` unless it sets them.
- `stdin` sends raw text instead of a payload.
- Placeholders in any string: `{repo:main}`, `{repo:feature}`, `{repo:detached}`,
  `{dir:plain}`, `{project}`, `{tests}` (this folder).
- Name cases as the behavior they check ("X is blocked", "Y passes").
