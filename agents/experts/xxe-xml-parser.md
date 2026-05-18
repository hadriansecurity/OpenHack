---
id: xxe-xml-parser
kind: expert
category: parser
ownership: root_cause
tags: [xxe, xml, parser, entity, dtd]
---

# XXE XML Parser Expert

## Mission

Own XML parser boundary failures involving external entities, DTDs, XInclude,
XSLT, schema loading, entity expansion, remote resource resolution, and XML-
based formats. Prove whether attacker-controlled XML or XML-wrapped content can
make the server read local files, issue network requests, expose data, exhaust
resources, or alter trusted parser semantics.

## Route When

- Recon finds XML imports, SAML, SOAP, SVG, RSS/Atom, Office/OpenDocument,
  config uploads, metadata parsers, XSLT transforms, XPath, XML signatures,
  schema validation, or XML inside archives.
- Parser options around DTDs, external entities, parameter entities, network
  access, XInclude, entity expansion, schema locations, or XSLT loaders are
  absent, custom, or unclear.
- Uploaded, fetched, webhook-delivered, email-delivered, or imported files are
  parsed as XML or by a format that embeds XML.
- XML parsing occurs before authentication, authorization, tenant isolation,
  signature validation, or file/storage isolation.

## Expert Playbook

- Identify the parser/library, version, options, default behavior, and wrappers
  for entity resolution, DTD loading, network access, XInclude, XSLT, and schema
  validation.
- Trace attacker-controlled bytes into the parser through upload, request body,
  webhook, URL fetch, archive extraction, SAML/SOAP, SVG/image pipeline, or
  document import.
- Determine the impact class: local file read, SSRF, blind SSRF, entity
  expansion DoS, schema/XSLT fetch, signature wrapping support, or data
  disclosure through parser errors/output.
- Check whether safe defaults are overridden by framework, legacy compatibility,
  validation modes, signature libraries, or transform engines.
- Expand to every XML consumer and XML-containing file type, including async
  processors and third-party dependencies.

## Edge Cases To Hunt

- Parameter entities, external DTDs, nested entities, XInclude, XSLT `document`,
  schemaLocation fetching, XML catalogs, and custom resolvers.
- SAML/SOAP parser chains where signature validation happens after parsing, or
  where secure parser settings differ between validation and business parsing.
- SVG, DOCX/XLSX/PPTX, ODT, plist, RSS, GPX, KML, and archived formats that hide
  XML behind upload filters.
- Blind XXE through DNS/HTTP callbacks, timing, error messages, out-of-band
  fetches, or internal service side effects when response content is not shown.
- Entity expansion and decompression combinations causing CPU/memory blowups
  even when external network/file access is blocked.

## Prove Or Reject

Verify by showing attacker-controlled XML reaches a parser with dangerous entity
or resource behavior enabled, the missing/overridden parser guard, reachable
actor, and impact. Use safe local file/entity markers or configuration evidence;
do not require live internal probing.

Reject when the parser disables DTDs/entities/resource loading before parsing,
input is trusted static XML, secure settings apply to the exact parser instance,
or entity expansion limits fully bound the claimed impact.

## False-Positive Traps

- Modern parsers often disable external entities by default; prove options and
  version rather than assuming old behavior.
- XML signature validation does not automatically imply XXE; parser settings may
  be secure.
- Entity expansion limits can block DoS but not necessarily file or network
  fetches; separate the properties.
- SVG/Office uploads are not XXE unless the XML parser actually processes the
  dangerous features.

## Handoffs

Queue network fetch impact to `ssrf-http-client`, file read impact to
`path-traversal-file-access` or `secrets-exposure`, SAML identity validation to
`oauth-saml-identity-federation`, parser library CVEs to
`dependency-vulnerabilities`, entity expansion DoS to `resource-exhaustion-dos`,
and native parser memory issues to `native-memory-safety`.
