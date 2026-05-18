# Quickstart

The easiest way to get started is to open this repository in a coding harness
such as Codex, Claude Code, or Cursor and ask it:

```text
Initiate a whitebox pentest on https://github.com/example/app.git
```

The harness should follow `AGENTS.md`: initialize a run, summarize each
checkpoint, and ask before moving to the next phase.

From the repository root, install the packaged CLI:

```bash
python3 -m pip install -e .
```

Do this sequence before any expert/LLM vulnerability review. Run one command at
a time. Each command prints what changed, what to review, and the next command
to run after the human approves proceeding.

```bash
whitebox init-run demo https://github.com/example/app.git
whitebox run-recon demo <run-id>
whitebox create-scenarios demo <run-id>
whitebox record-scenario-backlog demo <run-id> router-result.json
whitebox render-scenario-prompt demo <run-id> S001
whitebox record-scenario-result demo <run-id> S001 result.json
whitebox render-finding-triage-prompt demo <run-id> S001-F001
whitebox record-finding-triage demo <run-id> S001-F001 triage-result.json
whitebox validate-run demo <run-id>
whitebox summarize-run demo <run-id>
```

The first review phase is recon and scenario routing; expert analysis starts
from recorded `scenarios/backlog/S*.md` prompts. Use `summarize-run` when
resuming a run to see the current counts and next checkpoint.

Recon writes `recon-items.jsonl` plus lightweight `routes.jsonl`,
`inputs.jsonl`, `sinks.jsonl`, `exposures.jsonl`, and `coverage-gaps.json`.
The scenario-router prompt embeds these as routing hints. Router output must
cover every `routing_requirements` path/expert pair with a scenario or an
explicit `coverage_decision`.

To enrich recon with bundled Semgrep rules, run:

```bash
whitebox run-recon demo <run-id> --semgrep
```

Semgrep output is stored as `semgrep-results.json` and normalized into the same
recon items and routing requirements. Treat these matches as routing evidence,
not verified vulnerabilities.

To record a verified scenario result as a finding candidate:

```bash
whitebox record-scenario-result demo <run-id> S001 result.json
```

To record independent finding triage and materialize an accepted final finding:

```bash
whitebox render-finding-triage-prompt demo <run-id> S001-F001
whitebox record-finding-triage demo <run-id> S001-F001 triage-result.json
```

To record a multi-scenario expert bundle:

```bash
whitebox record-scenario-result demo <run-id> expert-results.json
```

The bundle must contain a top-level `results` array. Each item needs
`scenario_id` and the normal scenario result fields. Bundles create finding
candidates, not final findings; triage each candidate separately.
