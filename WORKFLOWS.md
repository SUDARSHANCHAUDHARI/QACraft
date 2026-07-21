# Recommended Skill Chains

## New feature

`/ticket-review` → `/test-plan` → `/feature-qa` → `/release-qa` → `/staged-rollout-check`

## Customer issue

`/customer-issue-repro` → `/bug-triage` → `/bug-report` → `/verify-fix`

## Production incident

`/incident-qa` → `/bug-report` or `/network-qa` → `/verify-fix` → `/qa-retrospective`

## Platform release

`/platform-matrix` → `/regression-scope` → `/smoke-test` → `/release-qa` → `/staged-rollout-check`

## Automation improvement

`/automation-review` → `/flaky-test-triage` → `/test-case-review` → `/qa-retrospective`

## Daily operation

Use `/qa-daily-summary` for communication and `/qa-handoff` when ownership or time zone changes.

Each skill remains independently version-bound. An upstream result does not automatically satisfy a downstream approval gate.
