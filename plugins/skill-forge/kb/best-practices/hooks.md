---
tier: advisory
last_verified: 2026-10-23
review_by: 2026-11-23
---

# Best practices — hooks

`tier: advisory` · refreshed 2026-10-23 from Claude Code hooks docs (partially read: per-event
input payloads not covered).

- **Where.** Plugin `hooks/hooks.json` (events under a top-level `"hooks"` key) or settings.
  Handler types: `command`, `http`, `mcp_tool`, `prompt`, `agent`. Commands reference
  `"${CLAUDE_PLUGIN_ROOT}"` (quoted).
- **Events.** SessionStart/End, UserPromptSubmit, PreToolUse, PermissionRequest, PostToolUse,
  PostToolUseFailure, Stop, SubagentStart/Stop, PreCompact/PostCompact, and more.
- **Matchers.** Exact name or `A|B` list; anything else is an unanchored regex (`^…$` to
  anchor). SessionStart matches `startup|resume|clear|compact`. Some events take no matcher
  (UserPromptSubmit, Stop).
- **Exit codes.** 0 = success (JSON parsed). 2 = blocking (stderr is the reason) on events
  that can block (PreToolUse, UserPromptSubmit, Stop…; not SessionStart or PostToolUse). Any
  other code, including 1, does **not** block.
- **Gate vs sensor.** A sensor emits `additionalContext` (inside `hookSpecificOutput` with
  `hookEventName`; ≤10k chars). A gate returns `permissionDecision` on PreToolUse:
  `allow | deny | ask | defer` (`defer` only in `-p` mode). `ask` shows the reason to the user;
  a hook `allow` does not override a deny/ask permission rule; across hooks deny > defer > ask
  > allow.
- **Write context as facts.** `additionalContext` arrives as a system reminder; factual
  statements work, imperative "system" instructions can trip prompt-injection defenses.
- **Stdout is only the JSON.** Shell-profile output breaks parsing; malformed JSON fails open
  (the action proceeds) unless `onFailure: "block"`.
- **Fast and safe.** Default command timeout is 600 s: set a short one. A hook never installs
  software on its own; it explains, asks, and blocks.
- **Guardrail, not decoration.** Gate missing deps, out-of-scope writes, irreversible actions;
  verify on Stop.
