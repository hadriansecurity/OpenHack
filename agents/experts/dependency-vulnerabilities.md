---
id: dependency-vulnerabilities
kind: expert
category: supply-chain
ownership: root_cause
tags: [dependencies, advisory, lockfile, reachability]
---

# Dependency Vulnerabilities Expert

## Mission

Own vulnerable third-party, vendored, generated, plugin, and build-chain
components when the vulnerable code is present, reachable, and security-relevant
in this target. Do not stop at CVE matching. Prove version, deployment, call
path, configuration, exploit preconditions, and blast radius.

## Route When

- Recon finds package manifests, lockfiles, vendored libraries, plugin managers,
  container images, generated clients, native extensions, browser bundles, or
  framework/runtime pins.
- A dependency handles auth, parsing, upload, template rendering, SQL, HTTP
  clients, crypto, archive extraction, image/media processing, serialization,
  routing, admin consoles, or sandboxing.
- Version ranges, overrides, forks, patches, transitive deps, optional deps,
  build-only deps, or runtime packaging are unclear.
- Known-vulnerable ecosystems appear near attacker-controlled input or privileged
  processing.

## Expert Playbook

- Establish the effective deployed component: package manager resolution,
  lockfile version, vendored copy, transitive path, build artifact, container
  layer, plugin load path, and environment.
- Identify the vulnerable feature and compare it to target usage, configuration,
  wrappers, feature flags, and reachable entrypoints.
- Look for patch/backport evidence: changelog, local diff, fork commit, distro
  patch level, monkey patch, or wrapper mitigation.
- Distinguish direct exploitability from exposure of a risky dependency that is
  unreachable or only build-time.
- Expand to all consumers of the same parser/client/library and to sibling
  packages with shared vulnerable code.

## Edge Cases To Hunt

- Transitive dependencies pulled by optional features, peer dependencies, plugin
  ecosystems, compiled native modules, browser bundles, and generated assets.
- Vulnerable parsers reached through uploads, imports, webhooks, previews,
  archives, email processing, XML/SAML/SVG, image/media conversion, PDFs, and
  office documents.
- Framework vulnerabilities enabled only with specific middleware order, debug
  flags, proxy trust, route patterns, multipart limits, template engines, or
  cache settings.
- Dependency confusion, typosquatting, path/git dependencies, mutable tags,
  private registry fallback, install scripts, and CI-only package execution.
- Client-side vulnerable libraries that become findings only when reachable
  user input and a browser impact exist.

## Prove Or Reject

Verify by citing the effective version or vendored code, the advisory or flawed
behavior, target configuration, reachable source-to-vulnerable-feature path,
attacker role, and impact. If external advisory freshness matters, say what
must be checked and mark `needs_context` rather than inventing certainty.

Reject when the package is dev-only and not deployed, the vulnerable feature is
unused, a backport/fork removes the flaw, config disables the vulnerable mode,
or the caller already has equivalent power.

## False-Positive Traps

- A vulnerable version string can survive in a patched fork or distro package.
- A production bundle may exclude dev dependencies, tests, examples, and build
  tools.
- Reachability matters: a severe parser CVE is candidate-only until attacker
  input reaches that parser.
- Advisory descriptions often include many variants; match the target's exact
  preconditions instead of copying severity.

## Handoffs

Queue reachable root causes to the owning sink expert such as
`xxe-xml-parser`, `deserialization-object-injection`,
`path-traversal-file-access`, `command-injection`, `ssrf-http-client`,
`xss-template-injection`, `native-memory-safety`, or `crypto-session-token`.
Queue exposed dependency secrets or registry credentials to `secrets-exposure`.
