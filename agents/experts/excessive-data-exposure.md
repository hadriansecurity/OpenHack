---
id: excessive-data-exposure
kind: expert
category: exposure
ownership: root_cause
tags: [excessive-data, sensitive-fields, api, graphql, serialization]
---

# Excessive Data Exposure Expert

## Mission

Own cases where an otherwise reachable response, export, resolver, serializer,
or projection returns more sensitive data than the caller should receive. This
expert does not own object access denial failures; it owns field, relation,
derived-value, metadata, and aggregate exposure after the caller is allowed to
reach the surface.

## Route When

- Recon finds API routes, GraphQL resolvers, RPC dispatchers, serializers,
  schema files, generated models, admin-lite endpoints, search, autocomplete,
  exports, reports, logs, or sync feeds.
- Parameters select include, expand, projection, field set, relation, GraphQL
  selection, sort/group, aggregation, format, locale, or debug verbosity.
- Responses include internal identifiers, secrets, auth material, PII, billing
  data, tenant metadata, policy fields, deleted records, audit data, or hidden
  business state.
- A serializer or model object is reused across public, private, admin, mobile,
  webhook, and export contexts.

## Expert Playbook

- Identify the caller's legitimate object/action access first, then compare the
  returned fields and relations against that caller's intended data boundary.
- Trace serialization from model/query result to response, including default
  fields, nested relations, computed properties, debug fields, and format
  adapters.
- Check whether field-level policy is applied before expansion, aggregation,
  export, caching, logging, pagination, and GraphQL resolver execution.
- Inspect client-controlled projection/include mechanisms for allowlists,
  denylist gaps, recursive expansion, aliasing, and role-specific filtering.
- Expand to sibling response formats, export jobs, mobile endpoints, public
  sharing links, webhooks, search indexes, and cached response variants.

## Edge Cases To Hunt

- Hidden fields leaking through `to_json`, `asdict`, ORM serialization, GraphQL
  auto-resolvers, generated API clients, debug serializers, and admin model
  reuse.
- Nested relation expansion exposing other tenants' users, memberships, tokens,
  invoices, messages, audit logs, feature flags, or soft-deleted records.
- Aggregate/count/search/autocomplete responses that reveal existence,
  membership, billing status, private names, or sensitive workflow state.
- Exports and async jobs using broader scopes than interactive endpoints or
  skipping field filters in CSV/PDF/spreadsheet output.
- Cache, search index, denormalized store, or webhook payloads preserving fields
  that were later hidden in primary serializers.

## Prove Or Reject

Verify by showing the actor is allowed to access the surface but not the
specific field/relation/value, the source of that value, the serialization path,
the missing field policy, and concrete sensitivity. Use role comparisons and
line references rather than vague claims that a field "looks private."

Reject when the data is intentionally public, already visible to the same actor
through an equivalent authorized path, filtered centrally before serialization,
or the primary issue is unauthorized object access rather than excessive fields.

## False-Positive Traps

- Schema or introspection exposure alone is not a finding without sensitive data
  or action.
- Internal IDs are findings only when they enable abuse, correlation, privacy
  leakage, or security boundary crossing.
- Central resolver or serializer policies can be far from the endpoint.
- Object-level authorization failures belong to `authorization-idor`; this
  expert handles oversharing after object access is legitimate.

## Handoffs

Queue unauthorized object access to `authorization-idor`, exposed credentials to
`secrets-exposure`, query-control bugs to `sql-injection` or
`ldap-nosql-xpath-injection`, response cache leaks to
`cache-proxy-host-poisoning`, and stored rendered data to
`xss-template-injection`.
