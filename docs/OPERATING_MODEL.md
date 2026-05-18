# Operating Model

This repository is a standalone workspace for local whitebox vulnerability discovery and
source-guided security review.

Every run is stored under `runs/<target>/<run-id>/` and starts with a fresh git
clone into `sourcecode/`. Agents operate through files: recon output, scenario
prompts, scenario results, findings, and logs.

Run initiation is command-first and checkpointed. A new pentest must begin by
creating or identifying a run folder, running recon, creating the
scenario-router prompt, and recording a scenario backlog. Each phase stops with
a short summary, the artifacts to review, and the next command to run after the
human approves. Broad LLM-based checks over the target source are not the first
phase; they belong inside recorded expert scenarios after routing.

The durable model is:

1. Recon item: a discovered route, file, sink, auth boundary, manifest, or other
   security-relevant place. Recon also emits lightweight line-based inventories
   for routes, inputs, sinks, exposures, and coverage gaps. These inventories
   are intentionally cheap hints, not proof. Optional Semgrep recon adds
   structured source-pattern hits and stores the raw Semgrep JSON, but those hits
   are still routing evidence rather than verified vulnerabilities.
2. Router assignment: the scenario-router agent reviews recon items and the
   expert registry, then creates a width-first backlog. It should fan out
   plausible source-to-sink paths to multiple root-cause experts instead of
   collapsing distinct endpoints, parameters, roles, storage paths, parsers, or
   deployment aliases too early. Recon also writes `routing_requirements`, a
   path/expert coverage contract that the backlog recorder enforces.
3. Scenario: one recon item paired with one expert and a proof question.
4. Finding: a verified vulnerability. One scenario may create many findings,
   and broad finding width is preferred over overly aggressive grouping.

Logs are audit artifacts, not private reasoning transcripts. They record what
was done, what evidence was used, what decision was made, and what should happen
next.

## Human Checkpoints

The tool does not need to be autonomous to be systematic. Phase commands should
complete exactly one durable phase and print:

1. What phase completed.
2. Which artifacts changed.
3. What the operator should review.
4. Which command would continue the run after approval.

Agents using this workspace should summarize those points and ask the human
whether to proceed before running the next phase, unless the human has already
approved a continuous batch.

Expert agents own 12 OWASP/MITRE-aligned root-cause families. Recon surfaces such
as API, GraphQL, upload, admin, parser, or native boundaries are not
deterministically assigned to experts by scripts. They are routed by the
scenario-router agent, and the final finding must name one primary root-cause
owner. The current registry is broad enough for general source-guided review,
while still allowing cross-family handoffs when one bug enables another.

`config/agents.json` uses `routing_signals` to connect recon evidence to
plausible experts. These signals are intentionally broad enough to find review
opportunities, but they are not vulnerability signatures and do not prove impact.

One primary root-cause owner per scenario does not mean one expert per file. If a
path credibly touches upload handling, file paths, parser behavior, and resource
exhaustion, the router should create separate scenarios for every relevant
expert. If it intentionally skips a path or path/expert pair, it must write a
structured `coverage_decision`; otherwise `record-scenario-backlog.py` rejects
the router output.

Expert result recording supports both single-scenario files and bundles. A
bundle uses a top-level `results` array where each entry includes `scenario_id`
plus the usual scenario result fields. The recorder fans that bundle into
`scenarios/finished/` and `findings/`, which avoids manual JSON splitting after
parallel expert work.
