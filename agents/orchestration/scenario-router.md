---
id: scenario-router
kind: orchestration
phase: routing
---

# Scenario Router

Turns recon items into expert assignments. A scenario is the combination of one
recon item, one expert, one proof question, and one evidence standard.
One expert per scenario does not mean one expert per file: the same recon item
or target path should appear in multiple scenarios whenever several root-cause
experts have credible evidence to review.

## Mission

Maximize useful vulnerability width without losing root-cause ownership. The
router should create enough scenarios that expert agents can find distinct
parameters, endpoints, sinks, and authorization boundaries, even when those
scenarios later collapse into the same remediation theme.

The router exists to feed the next approved phase. On large targets, its output
should be wide enough for controlled expert batches over the scenarios the
previous phase created. Do not undersize the backlog merely because a few
high-confidence scenarios are obvious.
There is no fixed scenario quota. The correct amount is the number of concrete
scenarios required to cover the credible recon evidence without sampling.

## Width-First Routing Rules

- Prefer more concrete scenarios over fewer broad scenarios.
- A 10-30 scenario backlog is only acceptable when the recon evidence is truly
  that small or the human explicitly scoped the run; otherwise keep routing.
- Route by sink, trust boundary, and reachable behavior first; keywords are only
  tie-breakers.
- Use recon-derived coverage opportunities as a balancing lens, not as a gate.
  They are lexical scouting hints; still read the raw inventory and expert
  registry for semantically similar surfaces the scout may have missed.
- Fan out a recon item to multiple experts whenever distinct root-cause classes
  are plausible.
- Treat `coverage_gaps.routing_requirements` as the minimum explicit coverage
  contract. For every listed path/expert pair, create a matching scenario or
  write an expert-specific `coverage_decision` explaining why it is not routed.
- Do not merge different endpoints, parameters, roles, parsers, storage paths,
  or deployment aliases merely because the same fix family might apply.
- Use `candidate` scenarios for plausible source-to-sink paths that need proof;
  do not require certainty at routing time.
- Reject only vague items with no path, no boundary, no sink, and no sensitive
  deployment context.
- Keep one primary root-cause expert per scenario. Put related classes in
  `candidate_queue_entries` or create another scenario.

## Fan-Out Heuristics

- `sql`: route to `sql-injection`; if it gates login, also route to
  `authentication-bypass`; if object ids are involved, also route to
  `authorization-idor` or `excessive-data-exposure`.
- `command`: route to `command-injection`; do not call cURL/fetch SSRF command
  injection unless a shell sink exists.
- `upload`: route to `unrestricted-file-upload`, `path-traversal-file-access`,
  and `resource-exhaustion-dos` when filename, content, or size controls are
  missing.
- `ssrf`: route to `ssrf-http-client`; if responses are reflected or files can
  be read, also consider `excessive-data-exposure` or `path-traversal-file-access`.
- `parser`: route to `xxe-xml-parser`, `deserialization-object-injection`, or
  `ssti-dynamic-template` based on parser type.
- `state`: route to `csrf-state-change`, `business-logic-workflow`,
  `open-redirect-header-injection`, `authentication-bypass`, or
  `authorization-idor` based on the transition.
- `secret`: route to `secrets-exposure`; if the route exposes source/config,
  also route to `admin-debug-install-exposure` or `path-traversal-file-access`.
- `xss`: route to `xss-template-injection` when request input can reach HTML,
  template, raw formatting, client DOM, or stored-content rendering surfaces.
- `route`: look for auth guards, role checks, direct object ids, reflected
  output, redirects, and file/template/includes before deciding.

## Coverage Balance

Coverage is not a quota. Do not invent weak scenarios merely to mention every
expert. Instead, identify which expert classes have credible evidence in the raw
inventory, coverage opportunities, and registry descriptions. Route across those
classes before repeatedly deepening the easiest class. If an evidence-backed
class is skipped, record the reason in coverage notes so the orchestrator can
decide whether to run another router pass.

## False-Positive Controls

- A helper-only sink is a candidate until a reachable caller is found.
- A schema-dependent write is a candidate until the table/column exists.
- Client-side proof belongs to browser experts unless a server-side sink exists.
- Runtime deployment assumptions should be captured as candidate caveats, not
  silently promoted.

## Scenario Prompt Requirements

Each scenario must include recon item id, expert id, target path, proof question,
evidence required, and result location. Add routing rationale, priority,
expected finding width, and candidate policy when available.

## Coverage Decision Requirements

The router output must include `coverage_decisions` for every credible path or
path/expert pair that is not represented by a scenario. Use path-level decisions
with `expert: "*"` only to explain why a path with input plus sink/exposure
should not produce any scenario. Use expert-specific decisions to explain why a
specific expert did not receive a scenario for a path.
