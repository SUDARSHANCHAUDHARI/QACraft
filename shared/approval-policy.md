# Approval Policy

## Approval object

Every approval contains:

- approval ID,
- run ID,
- gate name and number,
- decision,
- approver identity and role,
- timestamp and timezone,
- approved document type and digest,
- run-context digest,
- source and deployment identities,
- expiry,
- comment,
- invalidation status and reason.

## Invalidation

An approval is invalidated when any material approved input changes, including:

- ticket or requirement revision,
- source commit or deployment artifact,
- environment or tenant,
- role or account,
- feature flags or configuration,
- test plan,
- data and side-effect plan,
- expected result,
- publication target,
- evidence bundle relevant to the decision.

## Rules

1. Approval is explicit; silence is not approval.
2. Approval applies only to the exact bound object.
3. Self-approval is permitted only when policy explicitly allows it.
4. Manual override is a separate event and cannot rewrite a calculated outcome.
5. Expired approval blocks the dependent action.
6. External publication and destructive actions require their own gate.
7. Resume revalidates every approval required for remaining work.
