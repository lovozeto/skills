---
name: arbitrate
description: "Resolve a clash between UX intent and a verified technical constraint. Invoked by exception — only when a construction agent reports a real clash that no unit agent can resolve alone. Does not run in the KB pipeline."
disable-model-invocation: true
---

# arbitrate — resolve UX-vs-tech clashes

Invoked by exception. Never runs by default. Does not participate in the KB pipeline
(that's `/knowledge-base:kb-pipeline`'s job — it only marks conflicts, never resolves them).

A clash happens when what the design intends conflicts with what the platform allows — and
neither a design agent nor a technical agent can resolve it alone because each sees only
half.

## Steps

1. State the UX intent in one sentence.
2. State the technical constraint in one sentence, **with the row in `VERIFIED.md` that backs
   it up**. If there is no verified row, there is no proven constraint — return
   `REQUIRES VERIFICATION: {what to run}` and stop.
3. List the real options, including doing nothing.
4. Choose one. State what is sacrificed.
5. Write the decision to `CONVENTIONS.md` in the project with today's date and the reason,
   so it is not relitigated three weeks from now.

## Hard rules

- Do not invent technical constraints. If it is not in `VERIFIED.md`, it is not proven.
- Do not average. Choose and state the cost.
- Do not decide if the clash was actually an unverified question — in that case, return
  `REQUIRES VERIFICATION: {what to run}`.
