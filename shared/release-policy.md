# Ordered Release Decision Policy

The first applicable outcome takes precedence.

1. **INVALID CANDIDATE or INVALID RUN**
   - deployment identity is not trustworthy,
   - required approvals are invalid,
   - evidence integrity is compromised,
   - the tested environment changed materially.

2. **REJECT**
   - unresolved release-blocking product, security, privacy, data-integrity, compliance, or operational risk.

3. **BLOCKED**
   - any required criterion is blocked, inconclusive, not tested, flaky, errored, or lacks valid evidence.

4. **CONDITIONAL PASS**
   - all required criteria pass,
   - only approved optional gaps or residual risks remain,
   - owners, expiry, monitoring, and rollback conditions exist.

5. **PASS**
   - all required criteria pass,
   - no unaccepted release-blocking risk remains,
   - operational readiness and cleanup state are acceptable.

A business choice to release against a QA recommendation is recorded as an override, not as a modified QA result.
