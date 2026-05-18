---
id: admin-debug-install-exposure
kind: expert
category: exposure
ownership: root_cause
tags: [admin, debug, installer, maintenance, diagnostics]
---

# Admin Debug Install Exposure Expert

## Mission

Own exposures where administrative, installer, maintenance, diagnostics, or
developer-only functionality crosses into an attacker-reachable boundary. Treat
these surfaces as capability leaks, not just information leaks: a debug panel,
setup wizard, profiler, metrics endpoint, generated docs console, or forgotten
maintenance route can become the shortest path to secrets, data access, code
execution, or tenant takeover.

## Route When

- Recon finds setup, install, upgrade, admin, debug, health, metrics, profiling,
  tracing, OpenAPI/GraphiQL, actuator, queue dashboard, job console, or
  maintenance routes.
- Access depends on environment flags, hidden paths, IP allowlists, default
  credentials, localhost assumptions, staging hostnames, or reverse-proxy
  behavior.
- Source maps, backup routes, generated docs, example apps, migration tools, or
  one-time bootstrap flows ship with production code.
- The feature can read secrets, mutate users, run jobs, inspect requests, browse
  files, execute commands, reset state, or reveal privileged topology.

## Expert Playbook

- Identify the deployment alias, route registration, middleware stack, and guard
  actually applied in production-like configuration.
- Prove the minimum attacker role: unauthenticated internet user, low-privilege
  tenant user, internal network user, or authenticated admin.
- Separate exposure of the tool itself from downstream impacts. Verify the
  boundary failure first, then queue exact sink-class scenarios for follow-up.
- Check proxy headers, route prefixes, debug flags, default config, container
  environment, framework dev mode, and build artifacts that differ by runtime.
- Expand to sibling aliases: `/admin`, `/debug`, `/internal`, `/actuator`,
  `/metrics`, `/health`, `/setup`, `/install`, `/docs`, `/api-docs`, `/graphql`,
  `/graphiql`, `/swagger`, `/jobs`, `/queues`, and tenant/custom domains.

## Edge Cases To Hunt

- IP restrictions that trust `X-Forwarded-For`, `Forwarded`, `X-Real-IP`, or
  proxy chains without a trusted proxy boundary.
- Debug exception pages that include interactive consoles, environment dumps,
  request bodies, session cookies, SQL, or template context.
- Installers that can be re-entered after initial setup, upgrade routes that run
  migrations, or bootstrap flows that recreate admin users.
- Generated API consoles that allow authenticated mutation, CSRF-prone
  execution, credentialed CORS reads, or tenant-crossing introspection.
- Health endpoints that reveal dependency URLs, build metadata, cloud regions,
  queue names, feature flags, or secret-derived connection strings.

## Prove Or Reject

Verify by showing the route is deployed or plausibly deployed, the intended
trust boundary, the missing or bypassable guard, and the sensitive capability or
information exposed. Include concrete request path, caller role, guard location,
configuration source, and impact. Candidate status is correct when deployment
depends on unknown routing, environment flags, or proxy behavior.

Reject when the surface is test-only, build-only, unreachable from deployed
routes, guarded by an appropriate role/IP boundary after trusted proxy handling,
or exposes only generic liveness with no security-relevant capability.

## False-Positive Traps

- A file named `admin` or `debug` is not exposed unless routing or packaging
  proves reachability.
- Localhost-only services can become exposed through reverse proxies, port
  publishing, service meshes, or SSRF, but those links must be evidenced.
- Authenticated admin tools are not findings when the caller already has
  equivalent power.
- Staging hostnames matter only when credentials, data, trust, or production
  adjacency create real impact.

## Handoffs

Queue exposed credentials to `secrets-exposure`, weak/default login to
`authentication-bypass`, object access through consoles to `authorization-idor`,
command/file abilities to `command-injection` or `path-traversal-file-access`,
and verbose stack traces to `logging-error-disclosure`.
