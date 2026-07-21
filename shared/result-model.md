# Result Model

## Attempt outcomes

Recommended attempt-level outcomes:

- `OBSERVED_PASS`
- `OBSERVED_FAIL`
- `INFRA_ERROR`
- `AUTOMATION_ERROR`
- `DATA_ERROR`
- `POLICY_DENIED`
- `ABORTED`
- `CANCELLED`

## Scenario verdicts

Skills define domain-specific verdicts. A scenario verdict is calculated from all relevant attempts and approved rules. An assertion failure followed by a pass is not silently converted to pass.

## Workflow decisions

Workflow decisions combine required scenario status, context validity, evidence integrity, risk, and operational conditions.

## Publication state

- `DRAFT`
- `AWAITING_APPROVAL`
- `PUBLISHED`
- `UPDATE_CONFLICT`
- `PUBLICATION_FAILED`
- `WITHDRAWN`

## Override

A manual override records:

- calculated outcome,
- chosen business action,
- approver,
- reason,
- accepted risk,
- expiry,
- monitoring and rollback conditions.

The calculated QA outcome remains unchanged.
