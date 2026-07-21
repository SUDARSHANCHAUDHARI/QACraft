# Evidence Policy

## Evidence classes

- **Raw restricted evidence:** Original traces, logs, video, network captures, database reads, and customer-provided material.
- **Redacted operational evidence:** Internal evidence with secrets and unnecessary personal data removed.
- **Publishable evidence:** Minimum evidence suitable for the target ticket, report, or stakeholder audience.
- **Derived evidence:** Metrics, summaries, hashes, and classifications generated from source evidence.

## Required metadata

Every evidence item should record:

- evidence ID,
- run ID,
- skill,
- scenario and attempt ID,
- capture timestamp and timezone,
- source tool and version,
- application build and environment,
- actor, role, tenant, platform, and session where relevant,
- capture URL or source identifier after sanitisation,
- SHA-256 digest,
- MIME type and size,
- privacy classification,
- redaction state and redaction record,
- retention and deletion date,
- access policy.

## Rules

1. Filter secrets before writing evidence whenever possible.
2. Keep raw and publishable evidence separate.
3. A screenshot proves only visible state at a point in time.
4. Time-based behaviour requires time-based evidence.
5. API claims require protocol and resulting-state evidence where material.
6. Permission claims require independently verified actor identity.
7. Long-running claims state the actual observation duration.
8. Evidence links use approved schemes and access-controlled locations.
9. Evidence replacement creates a new version and audit event.
10. Publication fails closed when required redaction cannot be verified.

## Integrity

The execution ledger references evidence digests. For stronger assurance, sign the final manifest or store it in write-once storage. A digest alone does not prove capture time or authorship.
