# UltraStar song format — the standard this skill targets

Source of truth: `github.com/UltraStar-Deluxe/format` (normative docs: *The UltraStar File Format (v1/v2)*, `VERSIONING.md`) and the rendered spec at `usdx.eu/format`. Do **not** invent tags — verify against those.

## Version

- Target **`#VERSION:1.1.0`** for maximum player compatibility (it is *equivalent* to 1.0.0; 1.1.0 is what USDB adopted).
- `2.0.0` is newer/stricter (formal grammar, medley + timing tags switched to **milliseconds**, adds `#RENDITION`, `*URL` headers). Only target it if the player supports it.
- Absent `#VERSION` ⇒ treated as legacy/unversioned.

## Header tags

**Required:** `#VERSION`, `#TITLE`, `#ARTIST`, `#BPM` (UltraStar BPM = quarter-beat, ~4× musical BPM), and audio (`#AUDIO`, the modern successor to the deprecated `#MP3` — write `#AUDIO`, optionally also `#MP3` for old players).

**Timing/playback:** `#GAP` (ms before beat 0 — almost always needed), `#START`/`#END` (v1 seconds/ms, v2 ms), `#PREVIEWSTART`, `#VIDEOGAP` (may be negative), medley (`#MEDLEYSTARTBEAT/ENDBEAT` beats in v1 → `#MEDLEYSTART/END` ms in v2).

**Media:** `#VIDEO`, `#COVER` (1:1, `[CO]`), `#BACKGROUND` (`[BG]`), `#VOCALS` (`[VOC]`/acapella stem), `#INSTRUMENTAL` (karaoke stem). Each holds a **bare filename** co-located with the `.txt`.

**Metadata:** `#GENRE`, `#YEAR`, `#LANGUAGE` (English name of the language), `#EDITION` (curated pack), `#CREATOR` (author of the txt), `#TAGS` (search keywords), `#COMMENT` (not shown in-game), `#PROVIDEDBY`.

**Multiplayer:** `#P1`…`#P9` = singer display names (required when the body uses voice changes). `#DUETSINGERP1/P2` is deprecated → use `#P1`/`#P2`.

**Deprecated / drop:** `#MP3`→`#AUDIO`, `#ENCODING` (files MUST be UTF-8 no BOM), `#RELATIVE` (use absolute beats), `#AUTHOR`→`#CREATOR`, `#PREVIEW`→`#PREVIEWSTART`. Not part of the spec: `#ALBUM`, `#SOURCE`, `#YOUTUBE`, `#LENGTH`, `#FIXER`.

## Note / body format

Each note line: `type start length pitch text`.

| Marker | Meaning |
|---|---|
| `:` | normal note (scored on pitch) |
| `*` | golden note (double points) |
| `F` | freestyle (not scored, no pitch) |
| `R` / `G` | rap / golden rap (rhythm only, pitch ignored) |

- `start`/`length` in **beats** (integers), `pitch` relative semitone, `text` = the syllable incl. its trailing space when the word continues.
- **Line break:** a line starting with `- <beat>`. Never two consecutive.
- **Melisma / held vowel:** a note whose text is `~` extends the previous syllable (a new pitch on the same syllable). Well-made songs use this; use it sparingly.
- **End:** a single `E`. Everything after a trailing `E` is ignored.

**Timing math:** `ms_per_beat = 15000 / #BPM` (the ÷4 for quarter-beats is baked into `#BPM`). `time_ms(beat) = #GAP + beat * 15000/#BPM`.

**Encoding:** UTF-8, **no BOM**, LF newlines.

## Duet body

Declare `#P1:Name` / `#P2:Name` in the header. In the body, a line `P1` / `P2` switches all following notes to that voice until the next change (`P1` is implied if the body doesn't start with one). Each voice's beats must ascend; a voice change does **not** imply a line break. "Both sing" = duplicate the notes under each voice (no dedicated "both" token).

```
#P1:Alice
#P2:Bob
P1
: 0 4 5 Hel
: 4 4 7 lo
- 8
P2
: 8 4 5 there
E
```

## Folder conventions (de-facto, not in the grammar)

One folder per song; every file shares the base name `Artist - Title`, differing only by suffix/extension: `.txt`, `.mp3`/`.m4a`, ` [VOC]`/`[Vocals]`, ` [INSTR]`/`[Instrumental]`, `.mp4`, ` [CO].jpg`, ` [BG].jpg`. The game resolves media by the header value, so the bracket suffixes are convention, not law — but USDB and the games expect them.
