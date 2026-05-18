---
id: ssrf-http-client
kind: expert
category: network
ownership: root_cause
tags: [ssrf, http-client, webhook, url-fetch, metadata]
---

# SSRF And HTTP Client Expert

## Mission

Own server-side request forgery and outbound-client boundary failures where
attacker input influences a server, worker, parser, proxy, or integration to
make network requests, resolve names, follow redirects, or fetch resources the
attacker could not reach directly. Cover HTTP and non-HTTP schemes, metadata
services, internal control planes, webhooks, previews, imports, callbacks, and
egress policy bypass.

## Route When

- Recon finds URL fetchers, webhooks, import-by-url, link previews, crawlers,
  oEmbed, PDF/image rendering, callback validation, proxy endpoints, cloud
  metadata access, package fetching, XML/XSLT, or server-side browser automation.
- User input controls scheme, host, port, path, redirect target, DNS name,
  request headers, method, body, proxy settings, timeout, or URL embedded inside
  another format.
- Host allowlists, private-range blocks, redirect handling, DNS pinning,
  protocol restrictions, or cloud metadata protections are missing or custom.
- Responses are reflected, stored, parsed, used for authorization, or acted on
  by downstream services.

## Expert Playbook

- Identify the outbound client, runtime environment, egress network, DNS
  resolver, proxy layer, redirect policy, and supported schemes.
- Trace attacker control through parsing, normalization, validation, DNS
  resolution, redirect following, IP classification, request construction, and
  response consumption.
- Evaluate validation after canonicalization and after redirects. Re-check DNS
  and IP at the moment of connection, not only before.
- Determine impact: internal service reachability, metadata credentials,
  blind request primitive, response exfiltration, webhook abuse, file fetch,
  port scanning, cache poisoning, or service-side state change.
- Expand to every feature using the same HTTP client, URL validator, preview
  worker, webhook sender, import pipeline, proxy, and headless browser.

## Edge Cases To Hunt

- IP literal variants, IPv6, IPv4-mapped IPv6, decimal/octal/hex IPs, DNS
  rebinding, CNAME chains, localhost aliases, link-local/private ranges, and
  cloud metadata hostnames.
- Redirect chains across allowed to forbidden hosts, scheme changes, protocol
  smuggling, username/password URL components, fragments, backslashes, encoded
  separators, and parser mismatch between validator and client.
- Non-HTTP schemes such as file, gopher, dict, ftp, jar, mailto, data, unix
  sockets, and library-specific adapters.
- Header/body control enabling internal API actions, host header confusion,
  request signing with server credentials, or credential forwarding.
- Blind SSRF with timing, DNS callbacks, error messages, cache effects, webhook
  delivery logs, or downstream side effects.

## Prove Or Reject

Verify by showing attacker-controlled destination or request component, bypassed
egress/validation control, actual server-side request path, reachable internal
or privileged target, and impact. Use safe internal markers or reasoning; do not
probe live third-party infrastructure unnecessarily.

Reject when destinations are selected from a closed allowlist after redirects
and DNS resolution, private ranges and metadata endpoints are blocked at connect
time, responses and side effects are not security-relevant, or the feature is an
intended webhook to arbitrary public hosts with no privileged network position.

## False-Positive Traps

- User-configured webhooks are often intended; the issue is privileged network
  reachability, credential forwarding, response exposure, or internal action.
- Blocking `localhost` strings is not enough, but robust IP classification and
  egress firewalling can be sufficient.
- Fetching public URLs only is usually safe if redirects, DNS rebinding, and
  private ranges are handled correctly.
- File reads through URL schemes may belong to `path-traversal-file-access` when
  the root cause is local file access rather than network reachability.

## Handoffs

Queue file-scheme/local path reads to `path-traversal-file-access`, XML/XSLT
entity fetches to `xxe-xml-parser`, response data oversharing to
`excessive-data-exposure`, cloud secrets to `secrets-exposure`, command-backed
fetch wrappers to `command-injection`, and dependency-specific client flaws to
`dependency-vulnerabilities`.
