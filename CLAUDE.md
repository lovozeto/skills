# lovozeto/skills — maintenance rules

This repo is the **public export** of `lobomorir-ai-setup/shared/skills` (private). Edit skills
there and run `./sync.sh --export-public`; do not edit `skills/` here by hand, the next export
overwrites it. Private skills (today: `karaoke-builder`) never land here.

When a skill is added, renamed, archived, or changes how it is invoked, in the same change:

- **README:** update the skill table in `README.md`.
- **Invocation in sync:** a skill that is user-invoked only says `disable-model-invocation: true`
  in `SKILL.md` and, when it ships an `agents/openai.yaml`, `policy.allow_implicit_invocation:
  false` there. The two must agree. `agents/openai.yaml` is optional.
- **Skill-to-skill steps** say `Call the Skill tool with "<name>"` and only target
  model-invoked skills; a user-invoked one is recommended to the human by its `/name`.
- **Plugin:** this repo is one plugin (`.claude-plugin/plugin.json`, served by
  `.claude-plugin/marketplace.json`). After touching a manifest run `claude plugin validate .`
  and bump `version` in both files.

Superseded artifacts go to `_archive/` (see its README).
New skills are built with Anthropic's `skill-creator` skill (evals included).
House conventions: `~/dev/claude-kb/CONVENTIONS.md`.
