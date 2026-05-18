# Scenario Router Assignment

You are the scenario-router orchestration agent. Convert recon items into final
scenario backlog entries.

## Inputs

### Recon Items

```json
<recon_items_json>
```

### Lightweight Recon Inventory

These are cheap line-based inventories. Treat them as prompts for agent review,
not proof by themselves. When Semgrep recon was enabled, normalized Semgrep hits
are included in these inventories and summarized under `semgrep_results`; treat
them as structured routing hints, not proof.

```json
<recon_inventory_json>
```

### Agent Registry

```json
<agent_registry_json>
```

## Task

Create a width-first scenario backlog. For each selected item, choose one
root-cause expert, write a specific proof question, and define the evidence
required before the scenario can be verified. One scenario has one primary
expert, but one file, path, endpoint, parser, or recon item may and often should
produce many scenarios so every relevant expert reviews the same evidence from
their root-cause angle.

This is a checkpointed pentest pipeline, not a sampling exercise. The scenario
backlog is the work queue for the next approved phase, where operators can run
controlled expert batches over the scenarios the previous phase created on large
targets. Produce enough concrete, evidence-backed scenarios for that downstream
expert phase to run broadly.

Do not return a small sample. There is no fixed scenario quota; produce however
many concrete scenarios are needed to cover the credible recon evidence. A
backlog of 10-30 scenarios is incomplete for a broad pentest unless the evidence
is genuinely that small or the human explicitly scoped the run that narrowly. If
the backlog is small, include `coverage_notes` explaining the concrete evidence
constraint.

Do not route by keyword alone. Route by sink, trust boundary, reachable behavior,
and deployment context. Fan out one recon item to multiple experts when distinct
root-cause families are plausible. Never choose "the best" expert for a path when
several root causes are credible; create one scenario per relevant expert. Do
not collapse different endpoints, parameters, roles, storage paths, parsers, or
deployment aliases just because they may share a remediation theme.

Use candidate scenarios for plausible source-to-sink paths that still need proof.
Reject only items with no concrete path, boundary, sink, or sensitive exposure
context. The goal is broad coverage with explicit proof obligations.

Use `coverage_gaps.routing_requirements` as the minimum explicit coverage
contract. Each listed path/expert pair must either receive a scenario with that
same `target_path` and `expert`, or have an expert-specific `coverage_decision`
that explains why the pair is not applicable, out of scope, merged into a named
scenario, or blocked on context. Use `coverage_gaps.expert_opportunities` as the
human-readable scouting map behind those requirements. It is not a guarantee of
vulnerability; it only shows where registry routing signals appeared in recon
evidence. Prefer high-quality scenarios from credible opportunity groups before
adding more of a class that is already well represented, but also use the raw
inventory and expert registry to find scenarios whose wording the scout missed.
If an opportunity group is skipped, explain why in `coverage_notes` and
`coverage_decisions` using the evidence, not a generic "low confidence"
dismissal.

Coverage rule: every route/input file with a sink or exposure hint should either
receive at least one scenario or have an explicit path-level
`coverage_decision`. Every admin/debug/example exposure, direct execution alias,
object-id route, state-changing route, parser, upload, redirect, HTML sink, SQL
builder, shell sink, and outbound HTTP/file fetch deserves routing
consideration.

## Output JSON

Write JSON with a top-level `scenarios` array and `coverage_decisions` array.
Add optional top-level `coverage_notes` when you intentionally skip a credible
opportunity group.
Each scenario item must contain:

- `id`: stable id such as `S001`
- `recon_item_id`
- `expert`
- `target_path`
- `proof_question`
- `evidence_required`

Each item should also include:

- `priority`: `critical`, `high`, `normal`, or `low`
- `routing_rationale`: why this expert owns this scenario
- `expected_finding_width`: how many distinct findings may emerge, or `unknown`
- `candidate_policy`: what would keep the scenario candidate instead of verified
- `result_location`: expected path under `scenarios/finished/`

Each `coverage_decisions` item must contain:

- `path`: source path covered by the decision
- `expert`: expert id for expert-specific decisions, or `*` for path-level only
- `decision`: `scenario`, `covered_by_scenario`, `merged`, `not_applicable`,
  `needs_context`, or `out_of_scope`
- `scenario_ids`: required when the decision is `scenario`,
  `covered_by_scenario`, or `merged`
- `reason`: concrete evidence-based reason, required for non-scenario decisions

The backlog recorder rejects router output when a path in
`coverage_gaps.input_with_sink_or_exposure` lacks both a scenario and a
path-level `coverage_decision`, or when a path/expert pair in
`coverage_gaps.routing_requirements` lacks both a matching scenario and an
expert-specific `coverage_decision`.
