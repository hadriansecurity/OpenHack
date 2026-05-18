---
id: rate-limit-enumeration-abuse
kind: expert
category: abuse
ownership: root_cause
tags: [rate-limit, enumeration, brute-force, spraying, guessing]
---

# Rate Limit And Enumeration Abuse Expert

## Mission

Own abuse cases where an attacker can cheaply repeat guesses, probes, or
expensive actions to discover protected state, brute-force secrets, spray
credentials, enumerate users/tenants/objects, harvest data, or degrade service.
Focus on attacker economics: signal quality, request cost, defense scope, and
practical scale.

## Route When

- Recon finds login, reset, invite, OTP, MFA, magic links, coupon/redeem,
  search, user lookup, autocomplete, export, webhook, file preview, object fetch,
  or public identifier routes.
- Responses differ by account, tenant, token, role, object existence, email
  verification, membership, payment status, quota, or workflow state.
- Expensive or sensitive operations can be repeated cheaply by an attacker.
- Rate limits, lockouts, CAPTCHA, proof-of-work, backoff, monitoring, or abuse
  controls are missing, per-instance only, per-IP only, or easy to shard.

## Expert Playbook

- Define the abuse goal: secret guessing, credential spraying, account
  enumeration, tenant/object discovery, invite/token brute force, data scraping,
  quota bypass, or cost amplification.
- Compare attacker-controlled cardinality, request cost, signal strength,
  throttling key, lockout behavior, and reset window.
- Inspect every distinguishing signal: status code, body, headers, timing,
  redirects, email/SMS side effects, rate-limit headers, cache behavior, and
  downstream events.
- Check limit scope across IP, account, tenant, session, device, token, route,
  cluster node, CDN, worker queue, and external provider.
- Expand to sibling endpoints with the same lookup/token generator/rate limiter,
  plus mobile/API variants and async resend flows.

## Edge Cases To Hunt

- Username/email/phone enumeration through reset, invite, registration, login,
  SSO domain discovery, autocomplete, avatar, profile, billing, and org lookup.
- OTP, backup code, coupon, invite, reset, magic-link, short ID, slug, or
  tracking-token brute force with weak entropy or unbounded attempts.
- Credential stuffing/spraying where lockout is per-account but IP sharding or
  distributed attempts avoid controls, or where lockout creates victim DoS.
- Timing side channels, response length differences, redirect destinations,
  secondary emails/SMS/webhooks, and cache hits exposing existence.
- Expensive search/export/preview endpoints where no limit, pagination cap,
  query complexity cap, or per-tenant budget exists.

## Prove Or Reject

Verify by showing the repeated action, attacker cost, missing or bypassable
control, observable signal or scalable effect, and security impact. Quantify
entropy, allowed attempts, window, and practical request volume when relevant.

Reject when signals are indistinguishable in the attacker's channel, limits are
scoped to the abuse goal and enforced before expensive work, token entropy makes
guessing infeasible within rate limits, or enumeration reveals only intended
public data.

## False-Positive Traps

- Generic messages can still leak through timing or side effects; measure the
  actual attacker-visible channel.
- Missing per-IP rate limits may be acceptable when stronger per-account or
  per-token controls exist.
- Account lockout can be an availability issue; do not call it auth protection
  without considering victim DoS.
- A guessable ID is not vulnerable without unauthorized access, enumeration
  value, or brute-forceable secret semantics.

## Handoffs

Queue successful auth bypass to `authentication-bypass`, token entropy/design to
`crypto-session-token`, object access after enumeration to `authorization-idor`,
expensive computation impact to `resource-exhaustion-dos`, and workflow abuse to
`business-logic-workflow`.
