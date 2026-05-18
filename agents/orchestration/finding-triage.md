---
id: finding-triage
kind: orchestration
phase: triage
---

# Finding Triage

Reviews verified scenario results and stores each distinct vulnerability as a
separate finding. One scenario may produce multiple findings when separate
parameters, sinks, or trust boundaries are independently vulnerable.

## Triage Rules

- One finding per distinct root cause and impact boundary.
- Merge siblings only when they share the same vulnerable primitive and impact.
- Keep cross-family chains explicit in the finding and queue any unverified
  secondary class.
- Rejected and candidate leads are durable artifacts, not discarded notes.

## Finding Quality Bar

A finding needs a standardized title in the form
`<severity> - <type of vuln> - <location>`, plus severity, affected path,
attacker role, source, sink, missing guard, proof evidence, impact, and any
deployment assumptions.

Each stored finding must also be readable without re-running the scenario. Add a
plain-language summary for non-technical readers, a thorough impact analysis,
how an attacker could use the issue, an ordered attack chain, a controlled-test
example attack, recommended fix guidance, and validation notes.
