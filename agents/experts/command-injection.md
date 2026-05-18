---
id: command-injection
kind: expert
category: injection
ownership: root_cause
tags: [command, process, shell, argument-injection]
---

# Command Injection Expert

## Mission

Own paths where attacker-controlled data changes process execution semantics:
shell metacharacters, command selection, argv options, environment variables,
working directories, interpreter flags, file names interpreted as options, and
tool-specific mini-languages. Do not stop at obvious `shell=True`; serious bugs
often hide in "safe" argv calls that still let users supply dangerous flags or
config files.

## Route When

- Recon finds process execution, shell helpers, CLI wrappers, converters,
  archive tools, image/media processors, git/hg/svn calls, package managers,
  backup scripts, cron/job workers, or admin maintenance commands.
- User input controls command, subcommand, path, flag, environment, working
  directory, stdin, config file, template, plugin, interpreter, or tool profile.
- File upload, import, export, preview, print/PDF, OCR, compression, or scanning
  features invoke external binaries.
- Security relies on quoting, extension checks, path filtering, or denylists
  before crossing a process boundary.

## Expert Playbook

- Identify the exact process API and whether execution uses shell parsing,
  direct argv, `eval`-like interpreters, or wrapper scripts.
- Classify attacker control: command name, argv token, option value, option name,
  positional file, stdin, environment, cwd, config, or data file later parsed by
  the tool.
- Inspect every normalization step, quoting helper, path join, extension check,
  temporary file creation, and allowlist after decoding/canonicalization.
- Check tool-specific dangerous options: config loading, output path selection,
  network access, delegate processors, plugins, scripting, includes, and
  overwriting files.
- Expand to sync and async callers, admin variants, queue workers, scheduled
  jobs, converters for every supported file type, and platform-specific command
  construction.

## Edge Cases To Hunt

- Argument injection in argv-safe calls through leading hyphen filenames,
  `--option=value`, `@argfile`, response files, config paths, and subcommands.
- Shell injection through spaces, quotes, command substitution, redirection,
  separators, newlines, globbing, and environment expansion after wrapper
  interpolation.
- PATH, LD_PRELOAD/DYLD, HOME, TMPDIR, locale, proxy, credential, and tool
  environment variables controlled by request or tenant config.
- File names that become script bodies, templates, filter expressions, archive
  member names, git refs, make targets, package names, or interpreter options.
- Windows command-line parsing differences, PowerShell invocation, batch files,
  and cross-platform quoting helpers.

## Prove Or Reject

Verify by showing attacker control reaches the process boundary and changes the
invoked command, arguments, environment, file interpreted by the command, or
side effect. Evidence must include entrypoint, exact execution call, guard
quality, attacker role, and bounded impact. Use harmless marker commands or
semantic reasoning; do not require destructive execution.

Reject when all attacker-controlled values are selected from a strict allowlist,
used only as data files after canonicalization and option-terminator handling,
passed to a tool with no security-relevant interpretation, or gated by an actor
already allowed to run equivalent commands.

## False-Positive Traps

- Direct argv without a shell blocks shell metacharacters but not argument or
  option injection.
- Path traversal is not command injection unless the controlled path changes
  execution semantics or is interpreted by the tool.
- Escaping for POSIX shells may fail on Windows or inside nested wrapper scripts.
- Admin maintenance features may be intended when the role owns the execution
  capability; prove a lower-trust boundary.

## Handoffs

Queue arbitrary file read/write through command arguments to
`path-traversal-file-access`, upload-driven parser/tool risk to
`unrestricted-file-upload`, network fetch primitives to `ssrf-http-client`,
secret leakage from output/logs to `secrets-exposure` or
`logging-error-disclosure`, and native parser memory bugs to
`native-memory-safety`.
