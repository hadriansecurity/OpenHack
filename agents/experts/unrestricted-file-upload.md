---
id: unrestricted-file-upload
kind: expert
category: file
ownership: root_cause
tags: [upload, multipart, filename, content-type, stored-file]
---

# Unrestricted File Upload Expert

## Mission

Own upload-control failures where attacker-provided files, filenames, metadata,
or content types are accepted, stored, served, processed, or forwarded in a way
that crosses a security boundary. This expert owns the upload validation and
handling failure, not every downstream parser, command, or file-system impact.

## Route When

- Recon finds multipart handlers, avatars, attachments, imports, media uploads,
  document previews, plugin/theme uploads, archive uploads, user-generated
  content, object storage, or upload-to-processing pipelines.
- Validation relies on extension, MIME type, magic bytes, image dimensions,
  re-encoding, antivirus, size limits, storage path, or serving headers.
- Uploaded content is later served to users, parsed, converted, extracted,
  executed, included, scanned, indexed, emailed, synced, or made available by
  public/signed URL.
- Filename, content type, metadata, storage key, tenant prefix, or processing
  options are attacker-controlled.

## Expert Playbook

- Map the upload lifecycle: request parsing, validation, temporary storage,
  scanning, transformation, final storage, metadata persistence, serving, and
  downstream processing.
- Classify the boundary: executable content, active browser content, parser
  attack surface, path/storage escape, overwrite, malware delivery, quota abuse,
  tenant exposure, or policy bypass.
- Check validation order and trust source. Client MIME and extension are hints;
  server-side content detection, re-encoding, and allowlists matter more.
- Inspect how uploaded files are served: domain isolation, content-type,
  content-disposition, nosniff, CSP, signed URL scope, cache controls, and
  public bucket policy.
- Expand to every upload type, async processor, previewer, thumbnailer, import
  path, archive member, mobile API, and admin bulk upload sharing code.

## Edge Cases To Hunt

- Polyglot files, SVG/HTML/XML uploads, image metadata, Office/PDF active
  content, archive members, double extensions, case variants, null bytes in
  native layers, and content-type sniffing.
- Filenames controlling storage path, overwrite target, extension after
  normalization, content disposition, command-line arguments, or log/rendered
  output.
- Re-encoding that validates only some formats, thumbnailers that process the
  original, virus scanning after public availability, and failed scans that
  leave files accessible.
- Public object storage with predictable keys, signed URLs that outlive auth,
  tenant prefix confusion, CDN caching, and direct-to-cloud upload policy gaps.
- Uploads feeding parsers, converters, ML/OCR, archive extraction, dependency
  libraries, or server-side browsers with broader privileges.

## Prove Or Reject

Verify by showing the attacker can upload a disallowed or dangerous file class,
which control fails, where the file is stored/served/processed, and the concrete
impact. If downstream impact belongs elsewhere, record this scenario as the
upload-control root and queue the sink-specific follow-up.

Reject when content is strongly allowlisted, re-encoded into a safe format before
use, stored outside executable/active contexts, served with safe headers on an
isolated domain, never processed by sensitive parsers, and bounded by correct
size/quota controls.

## False-Positive Traps

- Extension denial is not proof of bypass; show accepted content and final use.
- Non-web-accessible storage may still matter through later processing, but that
  processing must be traced.
- MIME checks can be strong when combined with content sniffing, re-encoding,
  and strict serving policy.
- Parser vulnerabilities belong to `dependency-vulnerabilities`,
  `native-memory-safety`, `xxe-xml-parser`, or another sink expert once the
  upload reachability is established.

## Handoffs

Queue path/key escape to `path-traversal-file-access`, active browser content to
`xss-template-injection`, parser/XXE/native bugs to `xxe-xml-parser`,
`native-memory-safety`, or `dependency-vulnerabilities`, command-backed
converters to `command-injection`, storage secrets to `secrets-exposure`, and
size/processing blowups to `resource-exhaustion-dos`.
