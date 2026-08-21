# Best practices — hooks

`tier: advisory` · seed (unverified). Refresh via `/refresh-forge-kb`.

- **Hooks are a plugin feature.** Declared in `hooks/hooks.json` under event keys
  (`SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Stop`, ...). Commands
  reference `${CLAUDE_PLUGIN_ROOT}`.
- **Guardrail, not decoration.** Use hooks to stop what must not happen: gate missing
  dependencies, block out-of-scope writes, require confirmation before irreversible actions,
  verify on `Stop`.
- **Sensor vs decision.** A hook that only emits `additionalContext` is a *sensor*. A hook
  that returns a `permissionDecision` (`allow|ask|deny`) on `PreToolUse` is a *gate*. Know
  which you are writing.
- **Matchers.** `PreToolUse`/`PostToolUse` take a `matcher` (e.g. `Bash|Write|Edit`) to scope
  when they fire.
- **Fail safe and fast.** Keep hook scripts quick, with a timeout; never let a hook install
  software on its own — it asks permission and blocks.
- **Valid JSON out.** Hook stdout must be valid JSON in the expected shape, or the hook is
  ignored.

## To verify / expand via refresh
- Exact Claude Code hook event names, input payloads, and output schema (permission decisions,
  additionalContext, async rewake).
