---
id: injection
kind: expert
phase: scenario
tags: [owasp-a05-2025, injection, cwe-79, cwe-89, cwe-78, cwe-94]
---

# A05:2025 - Injection Expert

## Mission

Own failures where attacker-controlled data becomes structure, code, command,
query semantics, browser-executed markup/script, server-side template syntax, or
interpreter options. Cover SQL, LDAP, NoSQL, XPath/XQuery, OS command, code
generation, XSS, DOM injection, SSTI, expression language injection, prototype or
object pollution that reaches an interpreter, and command-option injection.

## Route When

- Recon finds raw SQL, query builders, search DSLs, LDAP filters, XPath/XQuery,
  command execution, subprocess wrappers, eval-like behavior, templates,
  markdown/rich text, DOM sinks, HTML helpers, dynamic object paths, or deep merge
  utilities.
- Parameters control table, column, operator, sort, filter, regex, aggregation,
  command, subcommand, flag, environment, working directory, template name,
  expression, helper name, object key, or output context.
- Stored values, imports, saved searches, tenant settings, webhook payloads,
  uploaded metadata, logs, or user content later reach an interpreter or browser
  sink.
- Code uses raw helpers, unsafe template/render helpers, sanitizer bypasses,
  string-built queries, shell calls, client template escape hatches, or dynamic
  dispatch into interpreters.

## Expert Playbook

- Classify the interpreter and context: SQL clause, NoSQL operator, LDAP filter,
  XPath selector, shell argv, shell string, environment, template source, template
  loader, HTML body, attribute, JavaScript, CSS, SVG, URL, DOM API, or object path.
- Trace attacker control through decoding, validation, transformation, storage,
  serialization, sanitizer/encoder, query builder, template renderer, shell
  wrapper, or browser parser to the final sink.
- Verify whether the defense matches the final context: parameterization,
  allowlisted identifiers, safe argv construction, command allowlists,
  context-correct output encoding, sanitizer policy, template sandbox, or blocked
  dangerous object keys.
- Check second-order paths: saved reports, imports, webhooks, admin forms,
  tenant branding, logs, email/PDF/export rendering, async jobs, and cached
  content.
- Expand to sibling sinks sharing the same query helper, template engine,
  sanitizer, command wrapper, object merge utility, rich-text renderer, or search
  builder.

## Edge Cases To Hunt

- SQL identifiers, order/group/having clauses, JSON paths, full-text syntax,
  collations, `LIKE` escape clauses, dynamic `IN` lists, stored procedures,
  COPY/load operations, DDL fragments, multi-statement settings, stacked-query
  guards, read/write replica routing, row-level-security bypass, timing
  channels, error-suppression paths, stored filters, ORM escape hatches, and
  report builders.
- NoSQL operator injection, Elasticsearch/OpenSearch script/query DSL injection,
  JSONPath/JMESPath and rule-engine filters, source filtering, query-string
  syntax, analyzer/query-parser differences, LDAP wildcard/filter/DN injection,
  XPath/XQuery namespace or function control, and aggregation pipelines.
- Command injection through safe-looking argv calls: user-controlled flags,
  option files, `@argfile`/response files, config paths, stdin, environment
  variables, working directories, PATH/LD_PRELOAD/DYLD/HOME/TMPDIR/proxy
  variables, file names starting with dashes, git refs, make targets, package
  names, Windows command-line parsing, PowerShell/batch invocation, and
  tool-specific mini-languages.
- XSS in JSON-in-script, hydration mismatches, unsafe URL schemes, SVG/MathML,
  markdown autolinks, postMessage, localStorage/sessionStorage, DOM clobbering,
  log rendering, uploaded HTML/SVG, and email templates.
- SSTI through render-from-string, dynamic template names, includes, filters,
  macros, helper lookup, sandbox escape, context object traversal, and multi-stage
  rendering; check "logicless" helpers, lambdas, partials, localization
  interpolation, email/PDF/report templates, server-side markdown pipelines, and
  cache or theme loaders.
- Prototype/object pollution through `__proto__`, `constructor`, path setters,
  recursive merge, defaults, JSON patch, metadata bags, or tenant config that
  later influences auth, template, command, SSRF, or routing behavior; include
  bracket/dotted paths, encoded keys, YAML anchors, array indexes, null-prototype
  objects, object freezing, own-property checks, `structuredClone`, and
  security-sensitive defaults such as `isAdmin`, `escaped`, `sanitize`, `shell`,
  `timeout`, `headers`, `where`, `template`, and `plugins`.

## Prove Or Reject

Verify by showing the source, interpreter boundary, attacker-controlled structure
or context change, missing or wrong neutralization, reachable sink, victim or
server context, and concrete impact. Safe proofs should prefer harmless markers,
changed query semantics, controlled template arithmetic, benign script execution
indicators, or command argument reasoning.

Reject when input is constant, strictly allowlisted for the exact structural
position, parameterized as data, context-correctly encoded at the final browser
sink, sanitized for the rendered context, passed only as a template variable,
blocked before merge, or never reaches an interpreter or security-relevant
browser context.

## False-Positive Traps

- Escaping for one context does not defend another; verify the final sink, not
  the helper name.
- Parameterized values do not protect dynamic identifiers or clauses unless those
  parts are separately allowlisted.
- A dangerous function is only a hint until attacker-controlled data reaches it.
- CSP can reduce XSS impact but rarely fixes the underlying injection.
- Object pollution must reach a real consumer; do not imply XSS, command, SSRF,
  or authorization impact without tracing the polluted key.

## Handoffs

Queue unsafe deserialization or trusted artifact integrity to
`software-data-integrity-failures`, upload reachability to
`path-traversal-unrestricted-upload`, object/tenant access outcomes to
`broken-access-control`, browser header/CORS/framing policy defects to
`security-misconfiguration`, network fetch access-control primitives to
`broken-access-control`, and vulnerable interpreter dependencies to
`software-supply-chain-failures`.
