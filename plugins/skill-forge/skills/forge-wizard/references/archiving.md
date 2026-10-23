# Replacing an existing artifact — archive instead of delete

Read this when the artifact you build supersedes an existing one.

1. Confirm the move with the user (it is an effective change).
2. Move the old files to `_archive/` at the repo root, mirroring their original path
   (`skills/engineering/foo/` → `_archive/skills/engineering/foo/`), with `git mv` so history
   is preserved.
3. Add a first line to the moved artifact: `ARCHIVED (<date>) — superseded by <new artifact>`.
4. If `_archive/` does not exist, create it with a `README.md` explaining the convention and
   a table of what was archived, what replaced it, and when.
5. If the repo has a router skill (a skill that maps the others and when to use each), update
   it so it routes to the new artifact and no longer names the archived one.

Done when the old path is empty, the archived copy carries its note, and `_archive/README.md`
lists it.
