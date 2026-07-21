# Example output excerpt

```text
Incident QA status: MITIGATED

Confirmed:
- Tizen 4: black screen on all tested devices
- Tizen 6.5: partial failure
- Tizen 7: unaffected in current sample

Mitigation:
Rollback restores playback on Tizen 4 and 6.5.

Residual risk:
Version rollback has not yet reached all offline devices.

Recovery condition:
Maintain normal playback-start rate for two hours after rollback adoption exceeds 95%.
```
