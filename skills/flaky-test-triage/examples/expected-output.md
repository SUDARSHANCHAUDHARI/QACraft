# Example output excerpt

```text
Flake classification: TEST FLAKE

Cause:
The test releases the mouse before the drop target finishes its layout transition. The final assertion checks API state but not the visible order.

Evidence:
- Failure follows reduced CPU allocation.
- Network and API responses are successful.
- Adding a fixed wait changes frequency but does not remove the race.
- Waiting for stable target geometry removes the failure in 100 retry-disabled runs.

Remediation:
Use a stable drag completion signal and assert both UI order and persisted API order.
```
