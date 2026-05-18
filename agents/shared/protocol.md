# Shared Agent Protocol

Agents operate inside a single run folder. Target source is read-only unless the
human explicitly asks for code changes.

Expert agents own OWASP/MITRE-aligned root-cause families. Surfaces such as API,
GraphQL, upload, admin, or parser entrypoints are recon and routing signals;
impacts such as RCE or account takeover are finding impacts. They are not
primary expert ownership labels.

## Working Model

The durable flow is `recon item -> scenario -> result -> finding`.

- New pentest work starts with the commands and run folder, not an ad hoc LLM
  sweep. If no run exists, initialize one; if recon has not run, run recon; if no
  backlog exists, create and record scenarios before expert review.
- Each phase ends with a short artifact summary, the next command, and an
  explicit request for human approval before continuing.
- A recon item is a route, file, sink, auth boundary, parser, manifest, or other
  place worth review.
- A scenario is one recon item paired with one expert and one proof question.
- Multiple scenarios may reference the same recon item or path when multiple
  root-cause experts are relevant. One expert per scenario is an ownership rule,
  not a cap on expert coverage.
- A finding is a verified vulnerability. One scenario may create many findings.

## Phase Completion Gates

Agents should finish the approved phase by writing durable artifacts, not just a
prompt or handoff file. Recon is ready for routing when recon inventories exist.
Routing is ready for expert work only when the scenario backlog is recorded.
Expert review is ready for triage only when scenario results are recorded. After
each phase, summarize the artifacts and ask before moving on. Do not present
recon, prompt generation, or a small sample of expert scenarios as complete
coverage. Once a backlog exists, process approved scenario checkpoints until
every recorded scenario is finished unless the human explicitly pauses or
narrows the run.

Before reporting a run as unblocked or complete, validate the run. If the run
config defines a scenario minimum, the recorded backlog must meet it unless a
human explicitly accepts a smaller scoped run. If the run config requires all
backlog scenarios to be finished, every `scenarios/backlog/S*.json` item must
have a corresponding `scenarios/finished/S*.json` result.

## Evidence Bar

Accepted findings require all of these:

- Reachable entrypoint or execution path.
- Attacker-controlled input, including stored or second-order control.
- Sensitive sink or security boundary.
- Missing, misplaced, or context-wrong guard.
- Concrete impact and required attacker role.

Dangerous functions, scanner hits, framework folklore, and suspicious names are
hints, not proof.

## Expert Depth Standard

Expert agents should behave like family specialists. For each scenario, use the
manifest's playbook to inspect obscure variants, second-order paths, runtime
configuration, sibling sinks, and false-positive traps specific to that root
cause. A shallow "source reaches sink" answer is incomplete unless it also
explains context, guard quality, exploit preconditions, actor role, and concrete
impact.

Expert agents should widen within the same root cause before stopping. If the
same vulnerable helper, policy, parser, serializer, validator, or sink is reused
by nearby endpoints, jobs, tenants, file formats, or deployment aliases, record
the sibling checks in `same_root_expansion` and emit distinct findings when they
are independently vulnerable.

## Required Agent Workflow

1. Read the scenario, expert manifest, run config, and relevant source.
2. Map the entrypoint before judging exploitability.
3. Trace source to sink with exact paths and line numbers.
4. Check guards in the context where the sink consumes data.
5. Decide `verified`, `candidate`, `rejected`, or `needs_context`.
6. Record sibling sinks with the same root cause before stopping.
7. Queue cross-family leads instead of burying them in prose.
8. Write concise logs covering actions, evidence, decisions, status, and next
   handoffs. Do not log private chain-of-thought.

## Result Expectations

Scenario results should include:

- `status`: `verified`, `candidate`, `rejected`, or `needs_context`.
- `expert`: the expert id.
- `primary_vulnerability_class`: the root-cause family or subtype owned by the expert.
- `summary`: concise decision.
- `evidence`: exact source, sink, guard, and impact references.
- `surface_class_coverage`: reviewed surfaces and per-class decisions.
- `same_root_expansion`: sibling source/sink checks.
- `candidate_queue_entries`: structured follow-up leads.
- `findings`: verified findings only.

Each verified finding should include:

- `title`: standardized title in the form `<severity> - <type of vuln> - <location>`.
- `severity`: `critical`, `high`, `medium`, `low`, or `informational`.
- `target_path`: affected source path or component.
- `attacker_role`: minimum attacker access or privilege needed.
- `preconditions`: required deployment state, feature flags, data, or user steps.
- `non_technical_summary`: plain-language explanation for stakeholders.
- `summary`: technical root-cause summary.
- `evidence`: source, sink, missing guard, line references, and proof notes.
- `attack_chain`: ordered chain from entrypoint to impact.
- `example_attack`: controlled-test example of what exploitation looks like.
- `impact`: short impact statement for summary tooling.
- `impact_analysis`: thorough blast-radius and security-boundary analysis.
- `attacker_use`: how an attacker could practically use the issue.
- `recommended_fix`: specific remediation guidance.
- `validation_notes`: safe reproduction and fix-verification notes.

## Rejection Rules

Reject or downgrade when input is constant, trusted, strictly allowlisted,
framework-bound in the relevant context, CLI/test-only, or gated by privileges
equivalent to the claimed impact. Record the reason so future agents do not
repeat the same trace.
