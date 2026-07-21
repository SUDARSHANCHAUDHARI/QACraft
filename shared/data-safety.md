# Test Data and Side-Effect Safety

## Data ownership

Before creation, record an intent event with an idempotency key. After creation, record the real returned resource ID immediately.

## Required controls

- Prefer dedicated test tenants.
- Use synthetic data by default.
- Prefix display names with a run marker only as a convenience; ownership depends on returned IDs.
- Map parent and child resources.
- Detect cascade deletion and shared dependencies.
- Route email, SMS, webhook, and notification effects to approved test sinks.
- Bound uploads, requests, concurrency, storage, and retention.
- Preserve original failure state before clear-cache, reset, re-pair, migration, or destructive recovery.
- Use reversible changes where possible.
- Require explicit approval for uncertain ownership or destructive cleanup.

## Cleanup states

- `COMPLETE`
- `PARTIAL`
- `NOT_REQUIRED`
- `PRESERVED_FOR_INVESTIGATION`
- `BLOCKED`
- `FAILED`

Residual resources include owner, reason, risk, and follow-up.
