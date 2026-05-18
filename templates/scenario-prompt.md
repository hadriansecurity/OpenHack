# Scenario <scenario_id>

- Expert: `<expert>`
- Recon item: `<recon_item_id>`
- Target path: `<target_path>`
- Priority: `<priority>`
- Routing rationale: <routing_rationale>
- Expected finding width: <expected_finding_width>
- Candidate policy: <candidate_policy>
- Result location: `<result_location>`
- Proof question: <proof_question>
- Evidence required: <evidence_required>

## Instructions

Read the expert manifest, shared protocol, run config, recon item, and source
file before answering. Stay inside this scenario unless same-root expansion or a
cross-class handoff is needed.

If this prompt is part of an approved multi-scenario run, still answer this
scenario as an individual expert review. Do not use a bulk classification,
sampled sweep, or repeated template as a substitute for reading this prompt and
the relevant source. If you did not review this scenario, do not emit a finished
result for it.

Operate as a specialist for the assigned root-cause class, not as a generic
scanner. Use the expert manifest as a playbook: map the reachable entrypoint,
trace attacker control to the exact sink or boundary, inspect guards in the
context where they are consumed, check class-specific edge cases, and expand to
sibling parameters/endpoints/jobs that share the same root cause.

Evidence must be concrete enough for another reviewer to replay the reasoning
without guessing. Prefer exact files, functions, routes, line references,
configuration paths, data-flow steps, caller roles, preconditions, and final
security impact. Suspicious names, dangerous APIs, dependency folklore, and
framework reputation are only leads until tied to reachability and impact.

When the scenario is promising but not yet proven, return `candidate` or
`needs_context` with the smallest missing facts. When a different vulnerability
class owns the next step, create `candidate_queue_entries` instead of stretching
this expert beyond its root cause.

Write JSON with:

- `status`: `verified`, `candidate`, `rejected`, or `needs_context`
- `expert`
- `summary`
- `evidence`
- `surface_class_coverage`
- `same_root_expansion`
- `candidate_queue_entries`
- `findings`

Prefer width: one verified scenario may emit multiple findings when distinct
parameters, endpoints, sinks, roles, or deployment paths are independently
vulnerable. Only put verified vulnerabilities in `findings`. Use
`candidate_queue_entries` for promising but unproven leads or work that belongs
to another expert.

For each verified finding, include enough context for both engineering and
non-technical review:

- `title`: `<severity> - <type of vuln> - <location>`
- `severity`
- `target_path`
- `attacker_role`
- `preconditions`
- `non_technical_summary`
- `summary`
- `evidence`
- `attack_chain`
- `example_attack`
- `impact`
- `impact_analysis`
- `attacker_use`
- `recommended_fix`
- `validation_notes`

Write the attack chain and example as controlled-test explanations: concrete
enough to understand exploitability, but avoid unnecessary live-target
weaponization when a conceptual proof is sufficient.
