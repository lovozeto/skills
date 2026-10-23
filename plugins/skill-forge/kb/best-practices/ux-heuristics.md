---
tier: advisory
last_verified: 2026-10-23
review_by: 2027-10-23
---

# Best practices — UX heuristics (for wizard & artifact design)

`tier: advisory` · refreshed 2026-10-23 from Nielsen Norman Group (10 heuristics, rev.
2024-01-30; wizards 2017; progressive disclosure 2006; confirmation dialogs rev. 2026-08-07).

- **Visibility of system status.** Show the whole sequence of steps, the current one, and what
  is DEFINED vs PENDING; state what will happen before any consequential action.
- **Match the real world.** Plain words, no internal jargon or error codes.
- **User control & freedom.** Clear exit, undo, cancel; leave midway and resume later.
- **Consistency & standards.** Same words and patterns for the same thing across the flow.
- **Error prevention.** Constraints and sensible defaults; the Ledger blocks generation before a
  hole becomes a broken artifact.
- **Recognition over recall.** Labeled suggestions, prefilled with previous choices; a
  suggestion never becomes an assumption (house rule).
- **Flexibility & efficiency.** Wizards suit novices and infrequent tasks; give experienced users
  a fast path.
- **Minimalist design.** Extra information competes with what matters.
- **Recover from errors.** Say what failed, where, and how to fix it, in plain language.
- **Help in context.** Beside the step, task-focused.

## Wizards
- Fixed order; if steps can go in any order, a wizard is the wrong pattern. Each step is
  self-contained. Descriptive step names, not "Next".
- Progressive disclosure: two levels at most; staged steps only when they barely depend on
  each other.

## Confirmations
- Only for serious or irreversible actions; frequent confirmations train people to ignore them.
- Say exactly what will happen; label options by outcome ("Delete file" / "Keep file"); no
  preselected "yes"; for the most dangerous actions require a deliberate act (typing a word).
