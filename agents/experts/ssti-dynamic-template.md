---
id: ssti-dynamic-template
kind: expert
category: injection
ownership: root_cause
tags: [ssti, template, expression, sandbox, dynamic-template]
---

# SSTI Dynamic Template Expert

## Mission

Own server-side template injection and dynamic template selection failures where
attacker-controlled text, names, expressions, filters, macros, includes, or
context objects are interpreted by a server-side template engine. Distinguish
SSTI from browser XSS: the root cause here is server-side evaluation or template
loader control before the response reaches the browser.

## Route When

- Recon finds render-from-string, dynamic template names, CMS/template editors,
  email templates, notification templates, report builders, localization with
  interpolation, macros, helpers, partials, or custom expression evaluators.
- User input reaches expression delimiters, template paths, filters, includes,
  macro names, helper arguments, sandbox policy, or template context keys.
- Admin/tenant template editors render content seen by other users, workers, or
  privileged integrations.
- The engine supports object/property access, function calls, filters, includes,
  custom helpers, sandbox escape primitives, or file/network loaders.

## Expert Playbook

- Identify the engine and mode: Jinja, Twig, Liquid, Handlebars, Mustache, ERB,
  EJS, Freemarker, Velocity, Smarty, Django, Go templates, Razor, or custom.
- Trace attacker control into template source, template name, include path,
  expression, helper/filter name, context object, or sandbox configuration.
- Determine the server-side capability exposed: expression evaluation, file
  include/read, command invocation, object traversal, SSRF, secret access,
  privilege change, or stored rendering into trusted channels.
- Check escaping separately from evaluation. Output escaping prevents some XSS
  but does not stop server-side template execution.
- Expand to email, PDF, export, preview, notification, localization, CMS,
  tenant-branding, markdown, and report-rendering paths sharing the engine.

## Edge Cases To Hunt

- "Logicless" engines becoming dangerous through custom helpers, partials,
  lambdas, unsafe context objects, prototype pollution, or helper lookup.
- Template name/path control leading to arbitrary template include, theme
  traversal, cache poisoning, or loading tenant-provided templates in privileged
  context.
- Sandboxes missing restrictions on attribute access, filters, constructors,
  globals, environment objects, file loaders, debug extensions, or method calls.
- Second-order SSTI from stored profile fields, tenant settings, translations,
  imported templates, CRM data, and notification variables.
- Multi-stage rendering where one engine output feeds another, or markdown/HTML
  sanitization happens before template evaluation.

## Prove Or Reject

Verify by showing attacker control of server-interpreted template material, the
engine evaluation path, missing sandbox/allowlist, reachable render context, and
impact. Safe proofs should demonstrate arithmetic/context access or harmless
server-side marker behavior before arguing higher impact from reachable objects.

Reject when attacker data is passed only as a variable value, template names are
strictly allowlisted, the engine is logicless without dangerous helpers, sandbox
policy blocks sensitive operations, or the only impact is browser-side rendering
owned by `xss-template-injection`.

## False-Positive Traps

- Autoescaping is not an SSTI defense, but it may prevent the separate XSS
  impact.
- User-controlled variables are normal; user-controlled template syntax or
  loader choice is the danger.
- Admin template editors may be intended unless rendered across a lower-trust
  boundary or with privileged server capabilities.
- A templating dependency CVE still needs target reachability and configuration.

## Handoffs

Queue browser-only script execution to `xss-template-injection`, template path
traversal to `path-traversal-file-access`, network fetches to `ssrf-http-client`,
command/file impacts to `command-injection`, sandbox/dependency CVEs to
`dependency-vulnerabilities`, and context-key pollution to
`prototype-pollution-object-pollution`.
