# Agent Instructions

This repository is a file-based whitebox-pentesting-agent workspace. When a human asks to
start, initiate, run, resume, or continue a pentest/security review, use the
tool structure before doing vulnerability analysis.

## Required Pentest Flow

Do not begin with a broad LLM source sweep, direct expert pass, or ad hoc manual
review of the target repository.

For a new target, use phase checkpoints:

1. Run `python3 scripts/commands/init-run.py <target> <git-url> [--run-id <run-id>] [--branch <branch>]`.
2. Summarize the created run and source commit, then ask the human what
   security experts to use before recon. Show every configured expert and the
   option `all agents`.
3. Run `python3 scripts/commands/run-recon.py <target> <run-id> --all-agents`
   only after approval, or run it with one or more `--expert <expert-id>`
   options if the human selected a subset.
4. Summarize recon counts and artifacts; ask whether to proceed. If the human
   wants deeper source-pattern coverage, rerun recon with `--semgrep` before
   scenario routing.
5. Run `python3 scripts/commands/create-scenarios.py <target> <run-id>` only
   after approval. The scenario-router must use the expert scope recorded
   before recon; do not create scenarios for unselected experts.
6. Summarize the router prompt and ask whether the scenario-router should answer
   it.
7. Record approved router output with `python3 scripts/commands/record-scenario-backlog.py <target> <run-id> router-result.json`.
8. Summarize backlog size and coverage notes; ask for one approval to run the
   entire unfinished scenario backlog. Batch approval is not batch analysis:
   every scenario still needs its own rendered prompt, source review, evidence,
   and result.
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
backlog exists, ask once to run the entire unfinished backlog as a continuous
scenario loop; then iterate over every `scenarios/backlog/S*.json` item
individually. Do not ask again at internal ranges such as `S021-S070`; those are
progress chunks only, not human checkpoints. Do not replace per-scenario expert
review with a broad classification, sampling pass, or templated rejection. Only
write `scenarios/finished/S*.json` after reading that scenario prompt and the
relevant source. If the full backlog cannot be reviewed, stop and report the
remaining scenario IDs instead of marking them finished.

Every scenario must be run by its own subagent. The rendered
`runs/<target>/<run-id>/scenarios/backlog/S*.md` file is the exact prompt for
that scenario's subagent. The orchestrator may schedule subagents, collect their
JSON answers, and record those answers, but it must not answer multiple
scenarios itself, synthesize results from a template, or mark scenarios finished
without a returned per-scenario subagent review. A bundled result file may only
contain a small set of already-returned subagent answers; it is never a shortcut
for running scenarios.

For efficiency, the orchestrator may group unfinished scenarios by expert and use
`python3 scripts/commands/next-expert-queue.py <target> <run-id> --expert <expert> --limit <n>`
to choose a bounded dispatch set. Expert grouping is scheduling only: an expert
queue is not an expert batch review, and no subagent may produce results for
more than one scenario. Each result must include `review_mode:
"per-scenario-subagent"`, a unique `subagent_id`, the rendered prompt hash, the
reviewed source files, and evidence snippets that match cited source lines.

For an existing run, inspect `run-config.yaml`, `plan.md`, `recon-output/`,
`scenarios/index.jsonl`, `scenarios/backlog/`, `scenarios/finished/`, and
`findings/` to determine the next missing phase. Summarize the current state and
ask before continuing from the first missing durable phase instead of starting
over. If unfinished backlog scenarios remain, ask to process all of them as one
approved continuous loop rather than asking for confirmation one scenario or
range at a time.

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
