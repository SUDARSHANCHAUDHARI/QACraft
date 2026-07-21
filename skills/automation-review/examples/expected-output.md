# Example output excerpt

```text
Automation audit: CRITICAL REMEDIATION

Critical finding:
14 tests call the API, wait for a fixed timeout, and pass without asserting that the expected UI state appears.

Other findings:
- 23 arbitrary waits
- 8 tests share one organisation
- 6 selectors depend on generated CSS classes
- CI retries hide first-attempt failures in 11 tests

Recommendation:
Fix false-confidence tests first, then isolate data and remove fixed waits.
```
