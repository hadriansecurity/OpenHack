# Contributing

Thanks for helping improve `whitebox-pentesting-agent`.

Before opening a pull request:

- Keep generated run artifacts out of commits. `runs/**`, target checkouts, and
  review outputs are local data.
- Keep public command wrappers small. Shared behavior belongs in
  `src/whitebox_pentesting_agent/`.
- Preserve the durable workflow:
  `recon item -> scenario -> result -> finding candidate -> triage -> finding`.
  Scenario experts may propose finding candidates, but final findings require
  recorded finding-triage decisions.
- Run `python3 scripts/commands/validate-run.py` before submitting changes.

The compatibility scripts under `scripts/commands/` remain supported, but new
integrations should prefer the `whitebox` CLI from an editable checkout.
