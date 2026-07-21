# Publication Policy

## Default behaviour

Skills draft by default. External writes occur only after the relevant approval gate.

## Idempotency

Use a stable publication key based on run ID, skill, source ID, and target type. Retried publication updates or resumes the same record.

## Conflict handling

Use compare-and-update semantics where possible. If the target changed after drafting, stop with `UPDATE_CONFLICT`, refresh, and request review.

## Audience safety

- Separate restricted internal evidence from stakeholder summaries.
- Remove secrets, customer data, private topology, and unsupported root-cause claims.
- Use plain language appropriate to the audience.
- Preserve links to source reports rather than copying large evidence.
- Record the exact published content and target identifier.

## Corrections

Material corrections are visible audit events. Do not silently rewrite historical decisions.
