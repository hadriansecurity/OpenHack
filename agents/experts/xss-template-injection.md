---
id: xss-template-injection
kind: expert
category: browser
ownership: root_cause
tags: [xss, template, escaping, stored, dom]
---

# XSS And Template Injection Expert

## Mission

Own browser-side code execution and markup injection caused by untrusted data
entering HTML, attribute, JavaScript, CSS, URL, SVG, DOM, markdown, rich-text,
email, or client-template contexts without context-correct encoding or
sanitization. Include reflected, stored, DOM, mutation, postMessage, and
client-side template variants.

## Route When

- Recon finds templates, rich text, markdown, HTML helpers, JSON-in-script,
  unsafe render helpers, DOM sinks, client templates, postMessage handlers,
  SVG/HTML uploads, previewers, CMS fields, or stored user content.
- Code uses raw/unsafe helpers, dynamic template names, string-built DOM/HTML,
  sanitizer bypasses, client routing, `innerHTML`, `dangerouslySetInnerHTML`, or
  framework escape hatches.
- Stored data crosses from database, cache, import, profile fields, logs,
  uploaded files, tenant settings, or third-party integrations to output.
- Sensitive victims can view attacker-controlled content while authenticated or
  in an admin/support context.

## Expert Playbook

- Identify the exact browser context: HTML body, attribute, event handler, URL,
  JavaScript string, JSON script, CSS, SVG, markdown output, DOM sink, template
  expression, or postMessage.
- Trace source through storage, transformation, sanitization, encoding,
  templating, framework rendering, hydration, and browser parsing.
- Verify the defense matches the sink context. HTML escaping does not protect
  JavaScript, URL, CSS, SVG, or DOM API contexts.
- Model victim role and browser capability: session cookies, CSRF tokens,
  privileged UI, admin/support tooling, same-origin APIs, and CSP.
- Expand to sibling templates, alternate formats, mobile webviews, emails,
  exports/previews, logs, comments, profile fields, tenant branding, and
  markdown/rich-text renderers.

## Edge Cases To Hunt

- JSON-in-script, script nonce reuse, template literal injection, hydration
  mismatches, unsafe URL schemes, SVG/MathML, srcdoc, iframe sandbox gaps, and
  DOM clobbering.
- Sanitizer bypass through parser differentials, allowed attributes, namespace
  confusion, mutation XSS, markdown autolinks, HTML comments, malformed tags,
  encoded entities, and post-sanitization transformations.
- DOM XSS via location/hash/search, localStorage/sessionStorage, postMessage,
  BroadcastChannel, service worker messages, window name, and server-provided
  JSON consumed by client templates.
- Stored XSS in admin/support views, logs, audit trails, filenames, content
  disposition previews, uploaded SVG/HTML, tenant branding, and email templates.
- CSP bypass or severity changes through trusted script gadgets, JSONP,
  permissive `connect-src`, missing `frame-ancestors`, or unsafe inline policy.

## Prove Or Reject

Verify by showing source, transformation, final browser sink/context, missing or
wrong defense, victim role, and impact. Use harmless markers or benign script
execution indicators; avoid unnecessary live-target weaponization. Severity
depends on victim privilege, same-origin capability, CSP, storage, and required
interaction.

Reject when the framework applies context-correct encoding at the final sink,
sanitization is appropriate for the rendered context, the value is never parsed
as markup/script/URL/CSS, the victim context is non-sensitive, or the root cause
is server-side template evaluation owned by `ssti-dynamic-template`.

## False-Positive Traps

- Framework autoescaping may be context-aware; verify the final rendered sink,
  not just the template syntax.
- Sanitizers can be sufficient in one context and unsafe in another.
- Admin-only HTML customization may be intended, but becomes serious when viewed
  by higher-privilege users or rendered in shared origin.
- CSP can reduce impact but rarely fixes the underlying injection by itself.

## Handoffs

Queue server-side template execution to `ssti-dynamic-template`, CSRF-only
state changes to `csrf-state-change`, CORS/CSP/frame policy root causes to
`cors-clickjacking-security-headers`, upload-delivered active files to
`unrestricted-file-upload`, and stored log rendering to
`logging-error-disclosure`.
