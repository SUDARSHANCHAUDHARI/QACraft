# Shared QA Standards

## Purpose

These standards apply to every skill in this repository. A skill may add stricter rules but may not silently weaken them.

## Core principles

1. **Version everything material.** Record source revision, deployment identity, environment, role, configuration, plan, evidence, and approvals.
2. **Never infer a pass.** A pass requires execution and evidence appropriate to the claim.
3. **Separate result layers.** Attempt outcome, scenario verdict, workflow decision, publication state, and manual override are different records.
4. **Preserve uncertainty.** Use blocked, invalid, inconclusive, unknown, error, aborted, or not-tested states where appropriate.
5. **Risk drives coverage.** Priority reflects customer impact, likelihood, data sensitivity, detectability, recoverability, and operational exposure.
6. **Requirements remain authoritative.** Implementation behaviour alone does not define the expected result.
7. **Evidence must have provenance.** Capture context, timestamp, source, actor, environment, build, scenario, attempt, privacy class, and integrity metadata.
8. **Human decisions are bound and auditable.** Approvals and risk acceptance identify who decided what, against which version, and why.
9. **External writes are explicit.** Ticket comments, defects, emails, rollouts, configuration changes, and data changes require the relevant gate.
10. **Cleanup is part of the outcome.** Residual resources and failed cleanup remain visible.

## Priority model

- **P0:** Critical customer, security, data-integrity, availability, or release-gating path.
- **P1:** High-impact core behaviour or high-probability regression.
- **P2:** Material but non-blocking behaviour, compatibility, recovery, or quality.
- **P3:** Optional confidence, low-impact edge, exploratory follow-up, or improvement.

Priority is not defect severity. A P2 scenario can reveal a critical defect.

## Required scenario fields

Every executable scenario should have:

- stable scenario ID,
- source requirement or risk,
- priority,
- required or optional status,
- preconditions,
- data and ownership,
- actor, role, tenant, platform, and environment,
- steps,
- approved expected result,
- assertion type,
- evidence type,
- stop condition,
- cleanup,
- result and attempts.

## Review rule

A workflow is not production-ready because the document sounds safe. The runtime and integrations must implement the controls described in `security-boundaries.md`, `approval-policy.md`, `evidence-policy.md`, and `data-safety.md`.
