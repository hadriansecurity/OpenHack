---
id: cache-proxy-host-poisoning
kind: expert
category: infrastructure
ownership: root_cause
tags: [cache-poisoning, host-header, proxy, cdn, forwarded-headers]
---

# Cache Proxy And Host Poisoning Expert

## Mission

Own boundary failures caused by HTTP intermediaries, canonical URL construction,
host trust, cache keys, and proxy metadata. Hunt for places where attacker input
changes what other users receive, which origin the app trusts, where links point,
or how the app separates tenants and security contexts.

## Route When

- Recon finds Host usage, `X-Forwarded-*`, `Forwarded`, `X-Original-*`,
  canonical URL builders, password reset links, tenant routing, absolute asset
  links, CDN/cache middleware, reverse proxies, or SSR/edge handlers.
- Responses vary by unkeyed headers, cookies, query params, path aliases,
  method override, content negotiation, locale, device hints, or scheme.
- Generated links, redirects, cached pages, emails, webhooks, signed URLs, or
  tenant-specific content cross authentication or tenant boundaries.
- Cache controls, surrogate keys, Vary headers, normalization, or purge rules
  are custom or inconsistent across layers.

## Expert Playbook

- Map the request path through CDN, load balancer, reverse proxy, framework
  trusted-host settings, app router, cache layer, and response builder.
- Identify which request components influence origin selection, tenant
  resolution, absolute URLs, security decisions, response body, and cache key.
- Compare cache key inputs to response-varying inputs. Any unkeyed influence is
  a poisoning candidate until proved uncacheable or harmless.
- Check deployment assumptions: trusted proxies, host allowlists, scheme
  derivation, HSTS, cache TTLs, stale behavior, and bypass rules.
- Expand to password reset, email verification, invite links, asset manifests,
  API docs, localized pages, error pages, and unauthenticated pages cached near
  authenticated variants.

## Edge Cases To Hunt

- Host header poisoning of reset links, tenant base URLs, CORS origins, CSP
  report endpoints, callback URLs, canonical tags, and signed download links.
- Web cache poisoning through unkeyed headers such as `X-Forwarded-Host`,
  `X-Forwarded-Scheme`, `X-Original-URL`, `X-Rewrite-URL`, `Accept-Language`,
  `Accept-Encoding`, or device/preview headers.
- Cache deception where private content is stored under static-looking paths,
  extension aliases, encoded separators, path parameters, or route fallbacks.
- Normalization mismatches around case, dot segments, encoded slashes, duplicate
  slashes, semicolons, query sorting, and trailing slashes.
- Stale-if-error and negative-cache behavior that preserves attacker-influenced
  content after origin recovery.

## Prove Or Reject

Verify by showing the attacker-controlled request component, the trust decision
or cache key mismatch, cacheability, victim-visible effect, and concrete impact.
When production cache behavior is unknown, record candidate status with the
missing intermediary facts instead of overclaiming.

Reject when trusted-host/proxy settings canonicalize before use, response
variation is keyed correctly, content is uncacheable at every relevant layer, or
generated links are not security-sensitive.

## False-Positive Traps

- Local development proxy behavior often differs from production CDN behavior.
- `Host` reflection in a response is not a finding without link trust, cache
  poisoning, tenant confusion, or other security impact.
- `Cache-Control: private` may still be overridden by misconfigured shared
  caches, but that requires evidence.
- Non-cacheable responses can still poison emails or absolute links; separate
  those impacts clearly.

## Handoffs

Queue redirect-only impacts to `open-redirect-header-injection`, account-link or
reset compromise to `authentication-bypass`, cross-tenant routing to
`authorization-idor`, CORS origin trust to
`cors-clickjacking-security-headers`, and SSRF through internal proxy fetches to
`ssrf-http-client`.
