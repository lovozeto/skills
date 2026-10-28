# lovozeto/skills — maintenance rules

When you add, rename, archive, or change how a skill is invoked, in the same change:

- **Router:** update `skills/productivity/ask-wolf/SKILL.md`. A router that names a missing
  skill, or misses a new one, sends the user the wrong way.
- **README:** update the skill table in `README.md`.
- **Invocation in sync:** a skill is user-invoked in both harnesses or neither:
  `disable-model-invocation: true` in `SKILL.md` ⇔ `policy.allow_implicit_invocation: false`
  in `agents/openai.yaml`. Every skill has an `agents/openai.yaml`.
- **Skill-to-skill steps** say `Call the Skill tool with "<name>"` and only target
  model-invoked skills; a user-invoked one is recommended to the human by its `/name`.
- **Plugins:** after touching a manifest run `claude plugin validate plugins/<name>`, bump the
  version and add a `CHANGELOG.md` entry.

Superseded artifacts go to `_archive/` (see its README).
New skills, agents, and plugins are built with `/forge-wizard` (plugin `skill-forge`).
House conventions: `~/dev/claude-kb/CONVENTIONS.md`.
