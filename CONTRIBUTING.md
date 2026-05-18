# Contributing

Thanks for helping improve `whitebox-pentesting-agent`.

Before opening a pull request:

- Keep generated run artifacts out of commits. `runs/**`, target checkouts, and
  review outputs are local data.
- Add new commands as `whitebox` subcommands in
  `src/whitebox_pentesting_agent/cli.py`; keep shared behavior in the package.
- Preserve the durable workflow:
  `recon item -> scenario -> result -> finding candidate -> triage -> finding`.
  Scenario experts may propose finding candidates, but final findings require
  recorded finding-triage decisions.
- Run `whitebox validate-run` before submitting changes.
