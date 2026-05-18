---
id: mass-assignment-parameter-tampering
kind: expert
category: input-validation
ownership: root_cause
tags: [mass-assignment, overposting, parameter-tampering, model-binding]
---

# Mass Assignment And Parameter Tampering Expert

## Mission

Own failures where client-controlled fields are trusted into models, commands,
settings, workflow state, or persistence without an explicit server-side field
contract. Hunt overposting, dynamic field updates, nested attribute writes,
patch/merge helpers, GraphQL input reuse, import column mapping, and hidden
client fields that influence security or money.

## Route When

- Recon finds generic model binding, `update(request)`, `assignAttributes`,
  `fill`, `merge`, PATCH, JSON body merges, dynamic field names, serializer
  input reuse, or ORM upserts.
- Sensitive fields appear near create/update paths: role, admin, tenant,
  owner_id, price, balance, status, verified, permissions, quotas, scopes,
  feature flags, workflow state, or foreign keys.
- Client-hidden fields influence authorization, billing, invitation, approval,
  notification, entitlement, audit, or routing decisions.
- Bulk import, CSV, webhook sync, mobile API, admin-lite, or GraphQL mutations
  share write models with privileged flows.

## Expert Playbook

- Identify the intended writable field set for the caller, action, role, object
  state, and tenant.
- Trace request body, query params, multipart fields, headers, imported rows,
  webhook payloads, and nested objects into binding, validation, policy,
  persistence, and side effects.
- Check whether allowlists are positive, role-specific, action-specific, and
  applied before model mutation and callbacks.
- Inspect nested relations, arrays, polymorphic types, JSON columns, metadata,
  settings bags, and dynamic path setters where sensitive fields hide.
- Expand to sibling create/update/upsert/bulk/import routes and background jobs
  sharing the same DTO, serializer, schema, model, or repository method.

## Edge Cases To Hunt

- Overposting role/admin/verified/tenant/owner/status fields, foreign keys,
  scopes, entitlements, prices, balances, credits, limits, and feature flags.
- Nested attribute abuse such as creating memberships, changing owner IDs,
  attaching files, modifying child permissions, or writing through join tables.
- PATCH/merge semantics that preserve privileged existing values, clear
  required guards with `null`, or write JSONB/metadata keys outside schema.
- GraphQL input types reused between admin and user mutations, mobile endpoints
  exposing deprecated fields, and import/webhook mappers trusting column names.
- Server-side validation that checks type/shape but not caller authority to set
  the field.

## Prove Or Reject

Verify by showing the attacker can submit the field, the binder accepts it, the
field reaches persistence or a trusted side effect, the caller is not authorized
to set it, and the security impact. Include before/after state and exact field
path.

Reject when the field is ignored, overwritten from trusted server state, removed
by a role-aware allowlist before mutation, guarded by a policy matching the
field/action, or only writable by a role with equivalent authority.

## False-Positive Traps

- Denylists are usually fragile, but they can block a specific field if complete
  in the relevant action; prove the gap.
- Type validation is not authorization, but serializers may combine both.
- Admin bulk editors may intentionally expose sensitive fields when the role
  owns those changes.
- A client-visible field is not vulnerable unless changing it creates a trusted
  server-side effect.

## Handoffs

Queue object/tenant permission issues to `authorization-idor`, workflow state
invariant bypasses to `business-logic-workflow`, auth/session field abuse to
`authentication-bypass`, prototype/key pollution to
`prototype-pollution-object-pollution`, and SQL/query control to
`sql-injection` or `ldap-nosql-xpath-injection`.
