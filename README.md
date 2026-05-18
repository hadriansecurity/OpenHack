<p align="center">
  <img src="public/hadrian.png" alt="Hadrian" width="320">
</p>

<h1 align="center">Hadrian Whitebox Pentesting Agent</h1>

<p align="center"><em>A lightweight, file-based workspace for source-guided whitebox security review.</em></p>

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)

`whitebox-pentesting-agent` is a set of agents and tools that mimics how the
Hadrian research team performs automated vulnerability research. The methodology
has been adjusted so it can run inside a common model harness — Claude Code,
Codex, Cursor, or a custom runner — while keeping durable state in plain files:
cloned source, recon items, scenario prompts, scenario results, finding
candidates, triage decisions, findings, and logs. The harness provides model
execution, terminal access, repository access, and human-in-the-loop approval;
this tool provides the durable workflow and review artifacts.

**The core idea:** checkpointed, scenario-first review. Recon discovers surfaces,
a router agent turns them into scoped scenarios, expert agents prove or reject
each scenario, and an independent triage agent decides which verified candidates
become final findings. The human approves every phase transition.

---

<p align="center">
  <img src="./public/lazy.jpeg">
</p>

## Quick Start

The easiest way to get started is to open this repository in a coding harness
such as Codex, Claude Code, or Cursor and ask it:

```text
Initiate a whitebox pentest on https://github.com/example/app.git
```

The harness should follow `AGENTS.md`: initialize a run, summarize each
checkpoint, and ask before moving to the next phase.

**Manual CLI flow:** install the CLI from the repository root:

```bash
python3 -m pip install -e .
```

**2. Walk through a run.** Execute one command at a time. Each command prints a
checkpoint summary and the next command to run — review the output and approve
before continuing.

```bash
# Create a run from a fresh git checkout
whitebox init-run demo https://github.com/example/app.git --run-id demo-001

# Choose expert scope, then run reconnaissance
whitebox run-recon demo demo-001 --all-agents

# Or scope the run to selected experts
whitebox run-recon demo demo-001 \
  --expert injection \
  --expert broken-access-control

# Optional: enrich recon with bundled Semgrep rules
whitebox run-recon demo demo-001 --all-agents --semgrep

# Build the scenario-router prompt from recon output
whitebox create-scenarios demo demo-001

# Record the router agent's selected backlog
whitebox record-scenario-backlog demo demo-001 router-result.json

# Render a scenario prompt for an expert agent
whitebox render-scenario-prompt demo demo-001 S001

# Record an expert's verified result (materializes finding-candidates/)
whitebox record-scenario-result demo demo-001 S001 result.json

# Render and record independent triage before final findings are created
whitebox render-finding-triage-prompt demo demo-001 S001-F001
whitebox record-finding-triage demo demo-001 S001-F001 triage-result.json

# Resume or hand off: prints current counts + next checkpoint
whitebox summarize-run demo demo-001
```

> **Resuming a run?** Run `whitebox summarize-run <target> <run-id>` to see counts
> and the next checkpoint command without executing anything.

Set `WHITEBOX_AGENT_ROOT` to this workspace path if you invoke the CLI from
outside the repo root. See [`docs/QUICKSTART.md`](docs/QUICKSTART.md) for more
detail.

---

## How It Works

The durable chain is always:

```text
recon item  →  scenario  →  result  →  finding candidate  →  triage  →  finding
```

Everything is deliberately small: commands create files, agents read those files,
and the human approves each phase before the next command runs.

```mermaid
flowchart TB
  classDef human fill:#FF003D,stroke:#111111,color:#FFFFFF,stroke-width:2px;
  classDef command fill:#FFFFFF,stroke:#111111,color:#111111,stroke-width:2px;
  classDef artifact fill:#F3F0EC,stroke:#5F5652,color:#111111,stroke-width:1.5px;
  classDef scope fill:#FFE8EF,stroke:#FF003D,color:#111111,stroke-width:2px;
  classDef agent fill:#111111,stroke:#FF003D,color:#FFFFFF,stroke-width:2px;
  classDef finding fill:#FF003D,stroke:#111111,color:#FFFFFF,stroke-width:2px;
  classDef checkpoint fill:#FFFFFF,stroke:#5F5652,color:#111111,stroke-width:2px,stroke-dasharray: 5 3;

  human["Human operator<br/>reviews checkpoint<br/>and approves next phase"]:::human
  logs["logs/ + trace.jsonl<br/>audit trail"]:::artifact

  init["1. init-run.py<br/>fresh clone + run config"]:::command
  source["sourcecode/<br/>target checkout"]:::artifact
  cp1{{Checkpoint<br/>confirm branch, commit,<br/>and expert scope}}:::checkpoint

  expertChoice["Expert scope<br/>all agents or selected<br/>security experts"]:::scope
  runConfig["run-config.yaml<br/>expert_scope"]:::artifact

  recon["2. run-recon.py<br/>scoped reconnaissance"]:::command
  reconFiles["recon-output/<br/>routes, inputs, sinks,<br/>exposures, coverage"]:::artifact
  cp2{{Checkpoint<br/>review recon counts<br/>and routing hints}}:::checkpoint

  routePrompt["3. create-scenarios.py<br/>router prompt"]:::command
  routerAgent["scenario-router<br/>chooses expert work"]:::agent
  cp3{{Checkpoint<br/>approve router answer<br/>before recording}}:::checkpoint

  recordBacklog["4. record-scenario-backlog.py<br/>scenario queue"]:::command
  backlog["scenarios/backlog/<br/>S001.json + S001.md"]:::artifact
  cp4{{Checkpoint<br/>confirm backlog coverage<br/>and batch size}}:::checkpoint

  render["5. render-scenario-prompt.py<br/>expert prompt"]:::command
  experts["expert agents<br/>prove, reject,<br/>or request context"]:::agent
  cp5{{Checkpoint<br/>review expert answer<br/>before recording}}:::checkpoint

  result["6. record-scenario-result.py<br/>result + candidates"]:::command
  finished["scenarios/finished/<br/>durable results"]:::artifact
  candidates["finding-candidates/<br/>proposed findings"]:::artifact
  triagePrompt["7. render-finding-triage-prompt.py<br/>triage prompt"]:::command
  triageAgent["finding-triage<br/>severity + scope due diligence"]:::agent
  triageRecord["8. record-finding-triage.py<br/>triage decision"]:::command
  triageDecisions["finding-triage/decisions/<br/>admission records"]:::artifact
  findings["findings/<br/>verified reports"]:::finding
  validate["9. validate-run.py<br/>quality gate"]:::command

  human --> init --> source --> cp1
  cp1 --> expertChoice --> runConfig --> recon --> reconFiles --> cp2
  cp2 --> routePrompt --> routerAgent --> cp3
  cp3 --> recordBacklog --> backlog --> cp4
  cp4 --> render --> experts --> cp5
  cp5 --> result --> finished --> candidates --> triagePrompt --> triageAgent --> triageRecord --> triageDecisions --> findings --> validate
  validate --> human

  init -. writes .-> logs
  expertChoice -. recorded in .-> runConfig
  recon -. writes .-> logs
  routePrompt -. writes .-> logs
  recordBacklog -. writes .-> logs
  result -. writes .-> logs
  triagePrompt -. writes .-> logs
  triageRecord -. writes .-> logs
  validate -. reads .-> finished
  validate -. reads .-> triageDecisions
  validate -. reads .-> findings
```

---

## Core Concepts

| Artifact | What it is |
|---|---|
| **Recon item** | A discovered place worth review — a route, sink, auth boundary, manifest, upload handler, or parser entrypoint. |
| **Scenario** | One recon item + one expert + one proof question. The same file may appear in multiple scenarios when multiple root-cause experts are relevant. |
| **Finding candidate** | A scenario expert's proposed verified vulnerability, pending independent triage. |
| **Finding** | A triage-accepted vulnerability. One scenario can produce multiple candidates when separate parameters, sinks, or trust boundaries are independently vulnerable. |

**Expert scope** is chosen before recon. Use `all agents` for broad coverage, or
select one or more expert IDs to focus routing. The chosen scope is written to
`run-config.yaml`, and later coverage, router prompts, and backlog recording are
constrained to that same set of experts.

**Findings are accepted only when recorded through `scenarios/finished/`,
`finding-candidates/`, `finding-triage/decisions/`, and `findings/`.** Do not
start a pentest with a broad LLM source sweep — the contract is command-first
and artifact-first.

Logs are audit artifacts, not private reasoning transcripts: what was done, what
evidence was used, what decision was made, status, and handoffs.

---

## Command Reference

Run commands from the repository root (or set `WHITEBOX_AGENT_ROOT`). The
`python3 scripts/commands/*.py` wrappers remain supported alongside the
`whitebox` CLI.

| Command | Purpose |
|---|---|
| `whitebox init-run <target> <git-url> [--run-id <id>] [--branch <branch>]` | Clone the target into a fresh run workspace. |
| `whitebox run-recon <target> <run-id> --all-agents [--semgrep]` | Source reconnaissance with every configured security expert; `--semgrep` adds bundled rule hints. |
| `whitebox run-recon <target> <run-id> --expert <id> [--expert <id> ...] [--semgrep]` | Source reconnaissance scoped to selected expert IDs. |
| `whitebox create-scenarios <target> <run-id>` | Build the scenario-router agent prompt from recon output. |
| `whitebox record-scenario-backlog <target> <run-id> <router-result.json>` | Materialize the router's selected backlog into `scenarios/backlog/`. |
| `whitebox render-scenario-prompt <target> <run-id> <S###>` | Render a scenario prompt for an expert agent. |
| `whitebox record-scenario-result <target> <run-id> <S###> <result.json>` | Record an expert result and materialize any finding candidates. |
| `whitebox record-scenario-result <target> <run-id> <bundle.json>` | Record a multi-scenario bundle (top-level `results` array). |
| `whitebox render-finding-triage-prompt <target> <run-id> <S###-F###>` | Render a prompt for the independent finding-triage agent. |
| `whitebox record-finding-triage <target> <run-id> <S###-F###> <triage-result.json>` | Record reportability, dedupe, confidence, and severity due diligence; accepted/downgraded decisions materialize final findings. |
| `whitebox summarize-run <target> <run-id>` | Print current counts and the next checkpoint command. |
| `whitebox log-event <target> <run-id> <actor> <status> <summary>` | Append an operational log event. |
| `whitebox validate-run [<target> <run-id>]` | Validate the whole repo or a specific run. |

### What recon produces

`run-recon` writes `recon-items.jsonl` plus lightweight `routes.jsonl`,
`inputs.jsonl`, `sinks.jsonl`, `exposures.jsonl`, and `coverage-gaps.json`. With
`--semgrep`, raw `semgrep-results.json` is also written and normalized into the
same recon items and routing requirements. **Semgrep hits are hints, not verified
vulnerabilities.** Recon also records expert scope in `run-config.yaml`; rerun
with `--all-agents` or repeated `--expert` options to change scope before
scenario routing.

### What the router does

`create-scenarios` does not create final scenarios itself. It writes
`runs/<target>/<run-id>/scenarios/scenario-router-prompt.md`, which the
scenario-router agent answers with JSON containing top-level `scenarios` and
`coverage_decisions` arrays. `record-scenario-backlog` validates that every
recon path and path/expert requirement is either represented by a scenario or
explicitly explained by a coverage decision before materializing the backlog.
The prompt and validator only use experts selected before recon, so a focused
run does not create backlog work for unselected experts.

---

## Run Layout

Every run lives under `runs/<target>/<run-id>/`:

```text
runs/<target>/<run-id>/
  sourcecode/           Fresh git checkout for this run.
  recon-output/         Recon items: routes, sinks, manifests, etc.
  scenarios/
    backlog/            Scenario JSON and rendered expert prompts.
    finished/           Recorded scenario results.
  finding-candidates/   Proposed findings emitted by scenario experts.
  finding-triage/
    prompts/            Rendered one-candidate triage prompts.
    decisions/          Recorded triage decisions.
  findings/             Triage-accepted findings for this run.
  logs/                 Structured event log.
  run-config.yaml       Target URL, commit, branch, expert scope, workflow metadata.
  run-state.jsonl       Run lifecycle events.
  trace.jsonl           Structured agent and command trace.
```

`runs/**`, `sourcecode/`, nested `sourcecode/`, and `targets/` are gitignored so
target code and review artifacts never get committed.

---

## Repository Structure

```text
config/                            Registry, defaults, and schema contracts.
agents/
  orchestration/                   Run lifecycle, scenario routing, finding triage.
  reconnaissance/                  Source recon agents that emit recon items.
  experts/                         OWASP/MITRE-aligned root-cause family experts.
  shared/                          Protocol all agents follow.
scripts/commands/                  Compatibility wrappers for the public commands.
src/whitebox_pentesting_agent/     Shared implementation and packaged CLI.
templates/                         Scenario, result, finding, recon-item templates.
docs/                              Operating model and quickstart notes.
runs/                              Generated run workspaces (gitignored).
```

Shared Python lives in `src/`; `scripts/commands/` files remain as stable command
wrappers for model harnesses and existing workflows.

---

## Agent Model

Agents are Markdown manifests — intentionally compact, but each expert must be
operational. It states when it should receive a scenario, what evidence proves or
rejects the root-cause family, common false positives, and where to handoff
cross-family leads.

The workflow roles:

- **Orchestration agents** own run lifecycle, scenario routing, and finding triage.
- **Reconnaissance agents** find surfaces — routes, files, sinks, auth boundaries,
  upload paths, parser entrypoints, manifests, and debug/admin areas.
- **Expert agents** own OWASP/MITRE-aligned root-cause families. The current
  registry defines **12 expert families** in `config/agents.json`.

The expert families are:

| Expert ID | Standard-aligned title |
|---|---|
| `broken-access-control` | A01:2025 - Broken Access Control |
| `security-misconfiguration` | A02:2025 - Security Misconfiguration |
| `software-supply-chain-failures` | A03:2025 - Software Supply Chain Failures |
| `cryptographic-failures` | A04:2025 - Cryptographic Failures |
| `injection` | A05:2025 - Injection |
| `memory-buffer-boundary-errors` | CWE-119 - Improper Restriction of Operations within the Bounds of a Memory Buffer |
| `insecure-design` | A06:2025 - Insecure Design |
| `authentication-failures` | A07:2025 - Authentication Failures |
| `software-data-integrity-failures` | A08:2025 - Software or Data Integrity Failures |
| `sensitive-information-exposure` | CWE-200 - Exposure of Sensitive Information to an Unauthorized Actor |
| `path-traversal-unrestricted-upload` | CWE-22 / CWE-434 - Path Traversal and Unrestricted Upload |
| `unrestricted-resource-consumption` | API4:2023 / CWE-770 - Unrestricted Resource Consumption |

> **Surfaces are not expert ownership labels.** API, GraphQL, upload, parser,
> admin, and native boundaries are recon signals that fan out to multiple
> experts. Impacts like RCE or account takeover are finding impacts. A verified
> finding must name one primary root-cause owner.
>
> SSRF is covered inside `broken-access-control` because OWASP Top 10:2025 maps
> CWE-918 to A01:2025; the dedicated outbound-client checklist is preserved in
> that expert rather than kept as a separate family.

---

## Development

Validate the workspace or a specific run:

```bash
whitebox validate-run
whitebox validate-run <target> <run-id>
```

See [`AGENTS.md`](AGENTS.md), [`CONTRIBUTING.md`](CONTRIBUTING.md), and
[`docs/OPERATING_MODEL.md`](docs/OPERATING_MODEL.md) for deeper documentation.

---

## Disclaimer

A note before you use this: this project is an experimental research prototype, provided as-is and without warranty of any kind. It is not a security product, has not been independently audited, and is not intended to be relied upon for any decision involving the security, safety, or correctness of software. It will miss real vulnerabilities and may report issues that do not exist. It is not a substitute for a professional security audit, manual code review, or established static analysis tools, and should never be used as a sole or primary means of assessing risk. By using it, you accept full responsibility for any outcomes, and the authors disclaim all liability for any damages, losses, or consequences arising from its use.

## License

MIT. See [`LICENSE`](LICENSE).
