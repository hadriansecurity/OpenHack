---
id: oauth-saml-identity-federation
kind: expert
category: identity
ownership: root_cause
tags: [oauth, oidc, saml, sso, federation, account-linking]
---

# OAuth SAML Identity Federation Expert

## Mission

Own federation-specific identity failures in OAuth 2.0, OIDC, SAML, social
login, enterprise SSO, SCIM-adjacent provisioning, and account linking. Prove
whether the relying party binds the right browser, authorization response,
issuer, audience, subject, tenant, email verification state, and redirect target
to the local account it creates or upgrades.

## Route When

- Recon finds SSO callbacks, SAML XML, OIDC metadata, OAuth redirects, token
  exchange, account linking, social login, enterprise domain mapping,
  provisioning, or IdP-initiated login.
- State, nonce, PKCE, RelayState, audience, issuer, subject, ACS URL, redirect
  URI, email verification, tenant, group mapping, or signature validation is
  absent, custom, optional, or split across layers.
- Flows accept multiple providers, dynamic IdP config, custom domains, mobile
  deep links, callback aliases, or legacy migration paths.
- Local account identity depends on email, username, external id, domain, group,
  or tenant claims.

## Expert Playbook

- Draw the federation flow from login initiation through callback, token/assertion
  validation, account lookup/linking, session creation, and post-login role
  mapping.
- Verify binding of browser session to response using state/nonce/PKCE/RelayState
  and anti-replay checks.
- Validate trust anchors: issuer, audience, client id, redirect URI/ACS,
  certificate/key, signature, token endpoint, metadata source, and tenant.
- Inspect local account mapping: provider subject, verified email semantics,
  domain ownership, invited user binding, group/role mapping, and account-link
  confirmation.
- Expand to every provider, tenant config, mobile/deep-link callback, IdP-
  initiated path, logout path, error fallback, and migration compatibility mode.

## Edge Cases To Hunt

- OAuth mix-up, code substitution, missing state, missing nonce, weak PKCE,
  redirect URI wildcard, open redirect in callback chain, and token accepted from
  the wrong issuer/client.
- OIDC trusting unverified `email`, failing to bind `sub` to issuer, ignoring
  `aud`/`azp`, accepting stale tokens, or using userinfo without token validation.
- SAML XML signature wrapping, unsigned assertions, weak reference validation,
  audience/recipient mismatch, clock skew abuse, replay, IdP-initiated confusion,
  and RelayState open redirect/account binding issues.
- Account takeover through auto-linking by email/domain, tenant confusion,
  deleted/reinvited users, invited-but-unverified accounts, or provider switch.
- Dynamic metadata, `kid`/JWKS lookup, certificate rollover, custom IdP config,
  and multi-tenant callback aliases.

## Prove Or Reject

Verify by showing the federation step that fails, the attacker-controlled
response or configuration, the missing validation/binding, the local identity
created or linked, and the takeover or privilege impact. Use synthetic IdP or
token/assertion reasoning when possible; do not need live third-party abuse.

Reject when mature middleware validates issuer/audience/signature/state/nonce in
the exact flow, account linking requires local reauthentication or verified
invite binding, and redirect/account mapping cannot cross tenant or identity
boundaries.

## False-Positive Traps

- OAuth open redirect matters most when it affects code/token delivery or trust
  ceremony; otherwise it may belong to redirect impact.
- Email equality is safe only with clear verified-email semantics from the
  trusted issuer and issuer-bound subject handling.
- Framework defaults can be strong, but custom callbacks often bypass them.
- IdP-initiated SSO may be intentional; prove replay, tenant confusion, or
  wrong-account binding.

## Handoffs

Queue generic session/login bypass to `authentication-bypass`, token crypto and
JWT key issues to `crypto-session-token`, XML entity parsing to
`xxe-xml-parser`, redirect/header primitives to
`open-redirect-header-injection`, and role/object authorization after login to
`authorization-idor`.
