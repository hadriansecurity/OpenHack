---
id: path-traversal-file-access
kind: expert
category: file
ownership: root_cause
tags: [path-traversal, file-read, file-write, download, extraction]
---

# Path Traversal And File Access Expert

## Mission

Own failures where attacker-controlled names, paths, archive members, storage
keys, templates, includes, or file handles cross a filesystem or object-storage
boundary. Cover reads, writes, deletes, overwrites, includes, extraction,
template lookup, static serving, export/import, and file-manager behavior.

## Route When

- Recon finds download, upload, export, import, include, template, archive,
  file-manager, static file, attachment, backup, log, plugin, localization, or
  report paths.
- User input controls filename, directory, extension, storage key, archive member
  name, symlink target, URL-to-file mapping, template name, or output path.
- Object ownership and path authorization both influence access.
- Code joins paths, normalizes paths, strips components, checks extensions,
  extracts archives, serves ranges, or maps storage keys to local files.

## Expert Playbook

- Identify the file boundary: local filesystem, chroot/container volume, object
  storage bucket, virtual storage keyspace, template loader, archive extractor,
  or static-serving root.
- Trace attacker control through decoding, normalization, path joins, extension
  filtering, symlink resolution, storage adapter mapping, and final open/write.
- Compare the canonical final path to the intended base after every decode and
  filesystem resolution step.
- Check authorization on both object identity and resulting path. Owning a file
  record does not imply owning arbitrary path contents.
- Expand to read/write/delete/extract variants, range requests, thumbnails,
  previews, conversions, backups, logs, localization files, and async processors.

## Edge Cases To Hunt

- `../`, encoded traversal, double decoding, mixed separators, Windows drive and
  UNC paths, backslashes, dot-dot after unicode normalization, null bytes in
  native layers, trailing dots/spaces, and case-insensitive filesystems.
- Symlink and hardlink traversal, TOCTOU between path check and open, temp-file
  reuse, predictable filenames, and archive extraction that creates links before
  later writes.
- Zip Slip/Tar Slip through archive member names, absolute paths, pax headers,
  symlinks, hardlinks, file permissions, device files, and nested archives.
- Template/include traversal, localization bundle lookup, plugin path loading,
  static route fallbacks, and extension allowlist bypass through alternate
  handlers.
- Object storage key confusion: prefix checks, tenant prefixes, signed URLs,
  public/private bucket aliases, and path-like keys that are not real paths.

## Prove Or Reject

Verify by showing the attacker-controlled path component, final resolved target
or storage key, missing containment/authorization guard, reachable operation, and
impact such as arbitrary read, overwrite, delete, include, stored payload, or
secret exposure. Use harmless marker files or path reasoning where possible.

Reject when canonicalization and containment checks happen after full decoding
and symlink resolution, storage keys are server-generated, object authorization
prevents cross-boundary access, or the path does not map to sensitive files or
security-relevant writes.

## False-Positive Traps

- `basename` may block simple traversal but not necessarily collisions,
  extension abuse, or symlink/archive issues.
- Virtual storage keys may not map to filesystem paths; prove the adapter
  boundary.
- Extension filtering is not path containment.
- Path read impact depends on deployment: container isolation, file permissions,
  and mounted secrets matter.

## Handoffs

Queue executable upload/storage outcomes to `unrestricted-file-upload`, command
execution via file paths to `command-injection`, secret reads to
`secrets-exposure`, object ownership failures to `authorization-idor`, and
archive/parser memory bugs to `native-memory-safety` or
`dependency-vulnerabilities`.
