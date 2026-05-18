---
id: open-redirect-header-injection
kind: expert
category: response
ownership: root_cause
tags: [open-redirect, header-injection, response-splitting, location]
---

# Open Redirect And Header Injection Expert

## Mission

Own response-control bugs where attacker input influences redirect destinations,
HTTP headers, cookies, content disposition, status lines, or response splitting.
Treat open redirects as security findings when they enable phishing with trusted
domains, auth-code/token theft, account linking abuse, policy bypass, cache
poisoning, or navigation across a protected trust boundary.

## Route When

- Recon finds `next`, `return`, `redirect`, `url`, `continue`, `callback`,
  `destination`, `RelayState`, `Location`, file download names, content
  disposition, cookie setters, or header helper code.
- User input reaches headers, redirects, cookies, filenames, status codes,
  cache headers, CORS/CSP headers, or proxy response metadata.
- OAuth/SAML/login/reset/invite flows use redirect destinations or callback
  parameters.
- URL allowlists, host checks, relative URL checks, CRLF filtering, filename
  sanitizers, or header encoders are custom.

## Expert Playbook

- Classify the sink: redirect, response header value, cookie attribute,
  content-disposition filename, status line, cache/security header, or response
  splitting.
- Trace URL/header input through decoding, normalization, parsing, allowlist
  comparison, reconstruction, and final response emission.
- Evaluate allowlists after canonicalization, including scheme, host, port,
  path, userinfo, backslashes, encoded separators, Unicode/punycode, and
  redirect chains.
- Determine impact in context: auth flow, trusted-domain phishing, token/code
  leakage, header injection, cache poisoning, cookie manipulation, or file
  download confusion.
- Expand to every redirect alias, mobile deep link, SSO callback, logout, error
  handler, file download/export, proxy wrapper, and locale switcher.

## Edge Cases To Hunt

- Scheme-relative URLs, backslash normalization, mixed slash encodings, nested
  URLs, userinfo `@`, punycode, trailing dots, case folding, duplicate params,
  double decoding, and path traversal into redirect handlers.
- Allowlist bypass through suffix/prefix checks, wildcard subdomains, attacker
  controlled custom domains, open redirect chains on allowed hosts, and
  post-validation URL reconstruction.
- CRLF/header injection through encoded newlines, unicode separators, folded
  headers, response splitting in older stacks, and content-disposition filename
  quirks.
- Cookie/header manipulation via untrusted names, domains, paths, SameSite,
  Secure/HttpOnly flags, cache-control, CSP, CORS, or refresh headers.
- OAuth/SAML `redirect_uri`, `next`, and `RelayState` interactions that turn a
  redirect primitive into account takeover.

## Prove Or Reject

Verify by showing the attacker-controlled input, final response sink, bypassed
normalization/allowlist, and security impact. For redirects, include why the
destination is outside the intended trust boundary and what attacker capability
is gained. For headers, show the exact header context and browser/proxy effect.

Reject when only same-origin relative redirects are possible, header encoders
remove control characters in the final sink, URL parsing and allowlisting are
done on the canonical destination, or no credible security impact exists beyond
low-risk navigation.

## False-Positive Traps

- Open redirect without auth, token, trust, or policy impact may be low severity
  or informational.
- URL validation before decoding can be bypassed, but validation after canonical
  parsing may be sufficient.
- Content-Disposition filename control is usually not header injection if the
  framework safely encodes it.
- A redirect to a user-owned custom domain may be intended in multi-tenant
  products; prove the trust-boundary mismatch.

## Handoffs

Queue OAuth/SAML account impacts to `oauth-saml-identity-federation`, login/reset
impacts to `authentication-bypass`, cache poisoning through headers to
`cache-proxy-host-poisoning`, CORS/CSP/cookie policy issues to
`cors-clickjacking-security-headers`, and XSS through response body contexts to
`xss-template-injection`.
