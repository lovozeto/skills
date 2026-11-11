---
name: ask-kb
description: Look up the team's knowledge base before deciding anything about UX, UI, accessibility, content, brand, visual design, media formats, Swift, C++, reverse engineering, backend, Docker, React or React Native. Use whenever a design or engineering decision could have a documented rule, when the user asks "what does the KB say", "según la base de conocimiento", "qué regla tenemos para", or wants a rule explained or cited.
---

# ask-kb — consult the knowledge base with the `kb` CLI

The KB is a folder of Markdown rules (`~/dev/claude-kb`, or `$KB_ROOT`) indexed by the `kb`
command. Never load a folder or a whole file into context: search, then fetch one section.

## Procedure

1. **Search.** `kb search "<two or three words>" --limit 8`. Add filters when the question is
   specific: `--base ux`, `--tag a11y`, `--tier proven`, `--fresh`. Words can be English or
   Spanish; synonyms are resolved.
2. **Fetch the section** behind the best hit: `kb get <ref>` (the `ref` is `base/file#anchor`
   in the search output). That is the full context of the rule. Fetch at most two sections.
3. **Answer with the rule and its ref**, for example: "Show the error next to the field
   (`ux/forms-and-errors#validation`, GOV.UK)". The ref is how the user checks you.
4. **Say when the KB is silent.** If nothing relevant comes back after one reformulation, say
   "the KB has nothing on this" in one line and continue with your own judgement. Do not
   invent a rule or attribute one to the KB.

## Trust and freshness

- `tier: advisory` comes from documentation and guides a decision; `tier: proven` was run on
  this machine and is the only thing code may depend on.
- A hit from a file whose `review_by` has passed, or marked `status: ambiguous`, is a lead,
  not a rule: say so when you use it. `kb stale` lists those files.
- The machine you are on is described in `hardware.md` (`kb get hardware`): which tools are
  allowed here and whether local models exist.

## Without the CLI

If `kb` is not on PATH: read `$KB_ROOT/INDEX.md` (default `~/dev/claude-kb/INDEX.md`), pick
exactly one file from the table, open it, and cite `file#heading` the same way.

## Repo knowledge

A repo's own rules live in `<repo>/.claude/knowledge/`; `kb` includes them when you run it
from inside that repo, with refs like `myrepo:palette#primary`. Prefer a repo rule over a
global one when they clash, and say that you did.

## Writing back

You do not edit the KB from here. To add or correct a rule, recommend `/kb-curate` with the
source; to flag a conflict, say which two refs disagree so the owner can set
`status: ambiguous` on the file.
