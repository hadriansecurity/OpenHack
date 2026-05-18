---
id: resource-exhaustion-dos
kind: expert
category: availability
ownership: root_cause
tags: [dos, resource-exhaustion, cpu, memory, disk, queue]
---

# Resource Exhaustion DoS Expert

## Mission

Own attacker-scalable availability failures caused by unbounded CPU, memory,
disk, database, network, cache, parser, queue, recursion, regex, fan-out, or
third-party cost. Prove not just that something is slow, but that a realistic
attacker can force disproportionate work across a protected boundary.

## Route When

- Recon finds expensive search, exports, uploads, parsers, compression,
  regexes, template rendering, image/media conversion, PDF generation, reports,
  webhooks, queues, background jobs, recursion, or external API fan-out.
- User input controls size, depth, count, fan-out, query complexity, regex,
  sort/group, concurrency, retry loops, archive structure, or cache-busting keys.
- Limits, timeouts, pagination, streaming, quotas, body-size caps, parser caps,
  worker budgets, and circuit breakers are missing or applied after heavy work.
- A low-privilege or unauthenticated caller can trigger high-cost synchronous or
  asynchronous processing.

## Expert Playbook

- Identify the scarce resource: app CPU, memory, DB CPU/locks, disk, object
  storage, queue workers, cache, outbound bandwidth, third-party quota/cost, or
  browser/client resources.
- Trace input-controlled dimensions through validation, parsing, allocation,
  database queries, loops, recursion, fan-out, retries, and cleanup.
- Compare attacker cost to defender cost and note concurrency requirements,
  authentication, quotas, and amplification factors.
- Check where limits are enforced relative to expensive work. Limits after parse
  or after enqueue may not protect the system.
- Expand to sibling formats, export types, search filters, background jobs,
  previewers, webhooks, importers, and cache-busting aliases.

## Edge Cases To Hunt

- ReDoS, catastrophic backtracking, glob/path matching blowups, parser recursion,
  deeply nested JSON/XML/YAML, entity expansion, compression bombs, and archive
  fan-out.
- N+1 queries, unbounded joins, wildcard search, expensive sorts, aggregation,
  GraphQL depth/complexity, relation expansion, and offset pagination on large
  tables.
- Uploads that consume memory before size checks, image/PDF/video conversion
  blowups, thumbnail storms, temp-file leaks, and disk-fill via failed cleanup.
- Queue amplification through webhooks, retries, email/SMS sending, cache misses,
  scheduled jobs, dedup misses, and user-triggered rebuilds.
- Per-node in-memory rate limits, cache-key explosion, lock contention, and
  slowloris-style body or response streaming without timeouts.

## Prove Or Reject

Verify by showing attacker-controlled input, missing or late limit, resource
amplification, reachable role, and operational impact. Use bounded estimates,
complexity analysis, safe local tests, or code evidence; avoid disruptive live
testing.

Reject when hard caps, streaming, timeouts, complexity limits, pagination,
quotas, worker isolation, or circuit breakers bound defender cost below a
security-relevant impact for the attacker's role.

## False-Positive Traps

- Slow operations are not findings without attacker scalability or protected
  resource impact.
- Admin-only maintenance jobs may be acceptable if the actor already owns the
  operational risk.
- Rate limits can mitigate resource exhaustion only when enforced before heavy
  work and scoped to the abuse vector.
- Parser crash or memory corruption may belong to `native-memory-safety` if the
  impact is memory safety rather than resource consumption.

## Handoffs

Queue brute-force/enumeration economics to `rate-limit-enumeration-abuse`, XML
entity specifics to `xxe-xml-parser`, dependency CVEs to
`dependency-vulnerabilities`, native crashes to `native-memory-safety`, query
injection to `sql-injection` or `ldap-nosql-xpath-injection`, and upload control
failures to `unrestricted-file-upload`.
