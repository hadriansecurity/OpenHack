---
id: cors-clickjacking-security-headers
kind: expert
category: browser
ownership: root_cause
tags: [cors, clickjacking, csp, cookies, security-headers]
---

# CORS Clickjacking And Security Headers Expert

## Mission

Own browser trust-boundary failures caused by cross-origin read permissions,
frameability, cookie policy, CSP/security header mistakes, and origin reflection.
Treat headers as controls only when they protect a concrete boundary: sensitive
data read, credentialed action, UI redress, token theft, script execution, or
tenant crossing. Missing hardening alone is not enough.

## Route When

- Recon finds CORS middleware, origin allowlists, frame policy, CSP, cookie
  attributes, cross-origin embeds, postMessage bridges, JSONP, iframe-able admin
  pages, or security-header customization.
- Origins, methods, headers, credentials, frame ancestors, CSP directives, or
  cookie options are reflected from requests or tenant config.
- Sensitive authenticated responses can be read cross-origin, sensitive actions
  can be framed, or trust decisions depend on `Origin`, `Referer`, Host, or
  subdomain relationships.
- Browser-exposed APIs mix session cookies, bearer tokens in storage, webviews,
  sandboxed frames, or third-party integrations.

## Expert Playbook

- Identify the browser primitive at issue: credentialed CORS read, noncredentialed
  public read, clickjacking, postMessage trust, CSP bypass, cookie scope, or
  header weakening.
- Trace how origin/frame/cookie policy is computed, including config, regexes,
  tenant domains, wildcard handling, null origins, and proxy-normalized hosts.
- Prove what a malicious origin can read or cause, and whether the victim's
  browser supplies credentials.
- Check response sensitivity and action sensitivity. Frameability matters most
  for authenticated irreversible actions or consent/approval flows.
- Expand to API, mobile-web, admin, docs consoles, GraphQL, file downloads,
  OAuth callbacks, and custom-domain tenant aliases.

## Edge Cases To Hunt

- Reflecting `Origin` with `Access-Control-Allow-Credentials: true`, including
  regex allowlists that accept attacker subdomains, suffix tricks, punycode,
  scheme confusion, or `null` origins.
- CORS preflight bypass via simple requests, method override, content-type
  confusion, wildcard headers, or endpoints that expose sensitive GET responses.
- Clickjacking through missing `frame-ancestors`/X-Frame-Options on payment,
  MFA, approval, admin, OAuth consent, destructive settings, or file-sharing
  pages.
- Cookie domain, path, SameSite, Secure, HttpOnly, and prefix mistakes that let
  sibling subdomains set or receive security cookies.
- CSP nonce reuse, unsafe dynamic script, JSON-in-script, CDN allowlist abuse,
  report-only policies, and tenant-controlled CSP sources.

## Prove Or Reject

Verify with the exact response headers, browser credential behavior, reachable
victim role, attacker origin/frame setup, protected data or action, and why
existing controls fail. Keep examples conceptual and bounded: show read
eligibility, framing eligibility, or cookie-scope impact without live abuse.

Reject when the response is public, credentials are not included, preflight
blocks the action, frame controls apply to the protected page, cookies are scoped
correctly, or the missing header is only defense-in-depth with no concrete
security boundary.

## False-Positive Traps

- `Access-Control-Allow-Origin: *` is not credentialed when browsers reject
  credentials with wildcard origins.
- Missing CSP is usually hardening unless a real injection or framing path needs
  it.
- `SameSite=Lax` still sends cookies on top-level safe navigations; model the
  exact request method and browser behavior.
- CORS does not protect server-to-server callers; do not use it as an
  authorization control finding unless browser reads are the impact.

## Handoffs

Queue forged state changes to `csrf-state-change`, script injection to
`xss-template-injection`, host/origin poisoning to
`cache-proxy-host-poisoning`, auth/token impacts to `authentication-bypass` or
`crypto-session-token`, and object permission failures to `authorization-idor`.
