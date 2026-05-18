# Agent Instructions

This repository is a file-based whitebox-pentesting-agent workspace. When a human asks to
start, initiate, run, resume, or continue a pentest/security review, use the
tool structure before doing vulnerability analysis.

## Required Pentest Flow

Do not begin with a broad LLM source sweep, direct expert pass, or ad hoc manual
review of the target repository.

For a new target, use phase checkpoints:

1. Run `python3 scripts/commands/init-run.py <target> <git-url> [--run-id <run-id>] [--branch <branch>]`.
2. Summarize the created run, source commit, and next command; ask the human
   whether to proceed.
3. Run `python3 scripts/commands/run-recon.py <target> <run-id>` only after
   approval.
4. Summarize recon counts and artifacts; ask whether to proceed. If the human
   wants deeper source-pattern coverage, rerun recon with `--semgrep` before
   scenario routing.
5. Run `python3 scripts/commands/create-scenarios.py <target> <run-id>` only
   after approval.
6. Summarize the router prompt and ask whether the scenario-router should answer
   it.
7. Record approved router output with `python3 scripts/commands/record-scenario-backlog.py <target> <run-id> router-result.json`.
8. Summarize backlog size and coverage notes; ask before rendering or assigning
   expert prompts.
9. Review only recorded `runs/<target>/<run-id>/scenarios/backlog/S*.md` expert
   prompts and record results with `python3 scripts/commands/record-scenario-result.py <target> <run-id> ...`.
10. Validate with `python3 scripts/commands/validate-run.py <target> <run-id>`.

Do not begin vulnerability analysis from recon alone. Recon is only a scouting
phase; summarize it and ask before scenario routing. Do not treat the
scenario-router prompt as final output; the next approved phase records router
output into `scenarios/index.jsonl` and `scenarios/backlog/`.

Do not present a sample of scenarios as complete coverage. There is no fixed scenario quota:
the correct amount is however many concrete scenarios are needed to cover the
credible recon evidence. Route every route/input file with a sink or exposure
hint, every credible expert opportunity, and every distinct endpoint, parameter,
role, parser, storage path, trust boundary, or deployment alias. If the backlog
is small, record coverage notes that explain why the evidence is genuinely
small. One scenario has one primary expert, but the same file, path, or recon
item must be routed to every relevant expert as separate scenarios. Do not let a
single expert assignment suppress other plausible root-cause classes. Once a
backlog exists, process approved checkpoints until every `scenarios/backlog/S*.json`
item has a corresponding `scenarios/finished/S*.json` result, unless the human
explicitly pauses or narrows the run.

For an existing run, inspect `run-config.yaml`, `plan.md`, `recon-output/`,
`scenarios/index.jsonl`, `scenarios/backlog/`, `scenarios/finished/`, and
`findings/` to determine the next missing phase. Summarize the current state and
ask before continuing from the first missing durable artifact instead of
starting over.

## Durable Model

The required flow is:

`recon item -> scenario -> result -> finding`

Verified findings must be recorded through `scenarios/finished/` and
`findings/`. Expert analysis outside a recorded scenario may create routing
input, candidate notes, or `needs_context`, but it should not create final
findings.

## Generated Run Artifacts

Treat `runs/**`, target source code, and generated review artifacts as run data.
Do not commit target source or generated run artifacts unless the human
explicitly asks for that.

Logs are structured. The tool writes `logs/events.jsonl` and `trace.jsonl`; it
does not write `human.log`.
